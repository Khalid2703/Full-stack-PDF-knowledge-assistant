"""
RAG (Retrieval-Augmented Generation) service
Manages vector store, retrieval, and ranking of relevant chunks
"""

import faiss
import numpy as np
import pickle
import os
import traceback
from typing import List, Dict, Tuple, Optional
from app.services.embedding_service import embedding_service
from app.database import SessionLocal
from app.models.chunk import Chunk
from app.utils.logger import app_logger
from app.config import settings


class RAGService:
    """Service for vector storage and retrieval"""
    
    def __init__(self):
        """Initialize vector store"""
        self.index = None
        self.document_map = {}  # Maps vector IDs to document metadata
        self.index_path = os.path.join(settings.VECTOR_STORE_PATH, "faiss_index.bin")
        self.map_path = os.path.join(settings.VECTOR_STORE_PATH, "document_map.pkl")
        
        # Load existing index if available
        self._load_index()
    
    def _load_index(self):
        """Load existing FAISS index and document map"""
        try:
            if os.path.exists(self.index_path) and os.path.exists(self.map_path):
                self.index = faiss.read_index(self.index_path)
                with open(self.map_path, 'rb') as f:
                    self.document_map = pickle.load(f)
                app_logger.info(f"Loaded existing index with {self.index.ntotal} vectors")
            else:
                # Create new index
                self._create_new_index()
        except Exception as e:
            app_logger.error(f"Error loading index: {str(e)}")
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index"""
        dimension = embedding_service.embedding_dim
        self.index = faiss.IndexFlatL2(dimension)  # L2 distance for similarity
        self.document_map = {}
        app_logger.info(f"Created new FAISS index with dimension {dimension}")
    
    def _save_index(self):
        """Save FAISS index and document map to disk"""
        try:
            faiss.write_index(self.index, self.index_path)
            with open(self.map_path, 'wb') as f:
                pickle.dump(self.document_map, f)
            app_logger.info(f"Saved index with {self.index.ntotal} vectors")
        except Exception as e:
            app_logger.error(f"Error saving index: {str(e)}")
            raise
    
    def add_documents(self, chunks: List[Dict[str, any]]) -> List[int]:
        """
        Add document chunks to vector store
        
        Args:
            chunks: List of chunk dictionaries with 'content', 'file_id', 'chunk_index', etc.
        
        Returns:
            List of vector IDs assigned to chunks
        """
        try:
            # Extract texts
            texts = [chunk['content'] for chunk in chunks]
            
            # Generate embeddings
            embeddings = embedding_service.generate_embeddings_batch(texts)
            
            # Convert to numpy array
            embeddings_array = np.array(embeddings).astype('float32')
            
            # Get starting vector ID
            start_id = self.index.ntotal
            
            # Add to FAISS index
            self.index.add(embeddings_array)
            
            # Store metadata in document map
            vector_ids = []
            for i, chunk in enumerate(chunks):
                vector_id = start_id + i
                vector_ids.append(vector_id)
                
                self.document_map[vector_id] = {
                    'file_id': chunk.get('file_id'),
                    'chunk_id': chunk.get('chunk_id'),
                    'chunk_index': chunk.get('chunk_index'),
                    'content': chunk.get('content'),
                    'page_number': chunk.get('page_number'),
                    'filename': chunk.get('filename'),
                }
            
            # Save index
            self._save_index()
            
            app_logger.info(f"Added {len(chunks)} chunks to vector store")
            return vector_ids
        
        except Exception as e:
            app_logger.error(f"Error adding documents: {str(e)}")
            raise
    
    def search(self, query: str, top_k: int = 5, file_ids: Optional[List[int]] = None) -> List[Dict[str, any]]:
        """
        Search for relevant chunks
        
        Args:
            query: Search query
            top_k: Number of results to return
            file_ids: Optional list of file IDs to filter results
        
        Returns:
            List of relevant chunks with metadata and scores
        """
        try:
            if self.index is None or getattr(self.index, 'ntotal', 0) == 0:
                app_logger.warning("Vector store is empty")
                return []
            
            # Ensure embedding dimension matches index dimension; if not, attempt reindex
            try:
                index_dim = int(getattr(self.index, 'd', embedding_service.embedding_dim))
            except Exception:
                index_dim = embedding_service.embedding_dim

            if embedding_service.embedding_dim != index_dim:
                app_logger.warning(f"Embedding dim mismatch (index={index_dim}, current={embedding_service.embedding_dim}). Rebuilding index to match current backend.")
                # Rebuild index using current embedding backend
                try:
                    self._reindex_all()
                    # After reindexing, update index_dim to match new index
                    index_dim = embedding_service.embedding_dim
                except Exception as re:
                    error_msg = str(re) if str(re) else type(re).__name__
                    app_logger.error(f"Reindexing failed: {error_msg}")
                    app_logger.error(f"Reindexing traceback: {traceback.format_exc()}")
                    raise RuntimeError(f"Failed to reindex: dimension mismatch (index={index_dim}, current={embedding_service.embedding_dim}). Reindexing failed: {error_msg}") from re

            # Generate query embedding (this might change embedding_dim if switching backends)
            query_embedding = embedding_service.generate_embedding(query)
            
            # Verify dimension AFTER embedding generation (in case backend switched)
            query_dim = len(query_embedding) if hasattr(query_embedding, '__len__') else query_embedding.shape[0] if hasattr(query_embedding, 'shape') else None
            current_index_dim = int(getattr(self.index, 'd', index_dim))
            
            if query_dim and query_dim != current_index_dim:
                app_logger.warning(f"Query embedding dimension ({query_dim}) doesn't match index dimension ({current_index_dim}). Triggering reindex.")
                try:
                    self._reindex_all()
                    current_index_dim = embedding_service.embedding_dim
                except Exception as re:
                    error_msg = str(re) if str(re) else type(re).__name__
                    app_logger.error(f"Emergency reindexing failed: {error_msg}")
                    app_logger.error(f"Reindexing traceback: {traceback.format_exc()}")
                    raise RuntimeError(f"Dimension mismatch: query={query_dim}, index={current_index_dim}. Reindexing failed: {error_msg}") from re
            
            query_embedding = np.array([query_embedding]).astype('float32')
            
            # Final safety check before search
            if query_embedding.shape[1] != current_index_dim:
                raise ValueError(
                    f"Critical dimension mismatch: query embedding has {query_embedding.shape[1]} dimensions, "
                    f"but FAISS index expects {current_index_dim} dimensions. "
                    f"Please delete the vector store and re-upload documents, or check embedding service configuration."
                )
            
            # Search in FAISS (search more than needed if filtering by file_ids)
            search_k = top_k * 3 if file_ids else top_k
            distances, indices = self.index.search(query_embedding, search_k)
            
            # Prepare results
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx == -1:  # FAISS returns -1 for empty slots
                    continue
                
                doc_metadata = self.document_map.get(int(idx))
                if not doc_metadata:
                    continue
                
                # Filter by file_ids if specified
                if file_ids and doc_metadata['file_id'] not in file_ids:
                    continue
                
                # Convert L2 distance to similarity score (0 to 1)
                # Lower distance = higher similarity
                similarity_score = 1 / (1 + float(distance))
                
                results.append({
                    'vector_id': int(idx),
                    'file_id': doc_metadata['file_id'],
                    'chunk_id': doc_metadata.get('chunk_id'),
                    'chunk_index': doc_metadata['chunk_index'],
                    'content': doc_metadata['content'],
                    'page_number': doc_metadata.get('page_number'),
                    'filename': doc_metadata['filename'],
                    'relevance_score': similarity_score,
                    'distance': float(distance)
                })
                
                if len(results) >= top_k:
                    break
            
            app_logger.info(f"Found {len(results)} relevant chunks for query")
            return results
        
        except Exception as e:
            error_msg = str(e) if str(e) else type(e).__name__
            app_logger.error(f"Error searching: {error_msg}", exc_info=True)
            app_logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def delete_file_vectors(self, file_id: int):
        """
        Remove all vectors associated with a file
        Note: FAISS doesn't support efficient deletion, so we rebuild the index
        
        Args:
            file_id: ID of file to remove
        """
        try:
            # Filter out vectors from the specified file
            remaining_vectors = []
            remaining_metadata = {}
            
            for vector_id, metadata in self.document_map.items():
                if metadata['file_id'] != file_id:
                    remaining_vectors.append(vector_id)
                    remaining_metadata[len(remaining_vectors) - 1] = metadata
            
            if len(remaining_vectors) == len(self.document_map):
                app_logger.info(f"No vectors found for file_id {file_id}")
                return
            
            # Rebuild index with remaining vectors
            if remaining_vectors:
                # Extract embeddings from old index
                embeddings = []
                for vid in remaining_vectors:
                    vector = self.index.reconstruct(int(vid))
                    embeddings.append(vector)
                
                # Create new index
                self._create_new_index()
                embeddings_array = np.array(embeddings).astype('float32')
                self.index.add(embeddings_array)
                self.document_map = remaining_metadata
            else:
                # No vectors left, create empty index
                self._create_new_index()
            
            self._save_index()
            app_logger.info(f"Deleted vectors for file_id {file_id}")
        
        except Exception as e:
            app_logger.error(f"Error deleting file vectors: {str(e)}")
            raise

    def _reindex_all(self):
        """
        Rebuild the FAISS index using the current embedding backend.
        This will re-embed all stored chunks using `embedding_service` and update
        the `document_map` and the DB `chunks.vector_id` values to match the new index ids.
        """
        app_logger.info("Reindex: Starting full reindex using current embedding backend")

        # Collect existing metadata ordered by previous vector id
        items = sorted(self.document_map.items(), key=lambda x: int(x[0]))
        texts = [meta['content'] for _, meta in items]

        if not texts:
            app_logger.info("Reindex: No documents to reindex, creating empty index")
            self._create_new_index()
            self._save_index()
            return

        try:
            # Generate embeddings for all texts
            app_logger.info(f"Reindex: Generating embeddings for {len(texts)} texts")
            embeddings = embedding_service.generate_embeddings_batch(texts, batch_size=128)
            
            if not embeddings or len(embeddings) == 0:
                raise ValueError("Failed to generate embeddings - empty result")
            
            embeddings_array = np.array(embeddings).astype('float32')
            
            # Verify embedding dimension matches expected
            if embeddings_array.shape[1] != embedding_service.embedding_dim:
                raise ValueError(f"Embedding dimension mismatch: got {embeddings_array.shape[1]}, expected {embedding_service.embedding_dim}")

            # Create new index with current embedding dim
            dimension = embedding_service.embedding_dim
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings_array)
        except Exception as e:
            error_msg = str(e) if str(e) else type(e).__name__
            app_logger.error(f"Reindex: Failed to generate embeddings or create index: {error_msg}")
            app_logger.error(f"Reindex traceback: {traceback.format_exc()}")
            raise

        # Rebuild document_map and update DB chunk.vector_id
        new_map = {}
        db = SessionLocal()
        try:
            for new_vid, (old_vid, meta) in enumerate(items):
                new_map[new_vid] = meta.copy()

                # Update DB chunk record vector_id if chunk_id exists
                chunk_id = meta.get('chunk_id')
                if chunk_id is not None:
                    try:
                        chunk_rec = db.query(Chunk).filter(Chunk.id == int(chunk_id)).first()
                        if chunk_rec:
                            chunk_rec.vector_id = str(new_vid)
                            db.add(chunk_rec)
                    except Exception as e:
                        app_logger.warning(f"Reindex: failed to update DB chunk {chunk_id}: {e}")

            db.commit()
        except Exception as e:
            db.rollback()
            app_logger.error(f"Reindex: DB update failed: {e}")
            raise
        finally:
            db.close()

        self.document_map = new_map
        self._save_index()
        app_logger.info(f"Reindex: Completed. New index size: {self.index.ntotal}")


# Global instance
rag_service = RAGService()
