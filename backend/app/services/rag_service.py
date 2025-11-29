"""
RAG (Retrieval-Augmented Generation) service
Manages vector store, retrieval, and ranking of relevant chunks
FIXED: Handles empty/missing FAISS index gracefully on Render deployments
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
        
        # ✅ FIX: Ensure directory exists
        os.makedirs(settings.VECTOR_STORE_PATH, exist_ok=True)
        
        # Load existing index if available
        self._load_index()
    
    def _load_index(self):
        """Load existing FAISS index and document map"""
        try:
            if os.path.exists(self.index_path) and os.path.exists(self.map_path):
                self.index = faiss.read_index(self.index_path)
                with open(self.map_path, 'rb') as f:
                    self.document_map = pickle.load(f)
                app_logger.info(f"✅ Loaded existing FAISS index with {self.index.ntotal} vectors")
            else:
                # Create new index - this is normal on first deployment
                self._create_new_index()
                app_logger.info("📝 Created new FAISS index (no existing index found)")
        except Exception as e:
            app_logger.warning(f"⚠️ Could not load existing index: {str(e)}")
            app_logger.info("📝 Creating fresh FAISS index")
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
            # ✅ FIX: Ensure directory exists before saving
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            os.makedirs(os.path.dirname(self.map_path), exist_ok=True)
            
            faiss.write_index(self.index, self.index_path)
            with open(self.map_path, 'wb') as f:
                pickle.dump(self.document_map, f)
            app_logger.info(f"✅ Saved FAISS index with {self.index.ntotal} vectors")
        except Exception as e:
            app_logger.error(f"❌ Error saving index: {str(e)}")
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
            # ✅ FIX: Recreate index if it's None
            if self.index is None:
                app_logger.warning("⚠️ FAISS index was None, recreating...")
                self._create_new_index()
            
            # Extract texts
            texts = [chunk['content'] for chunk in chunks]
            
            # Generate embeddings
            app_logger.info(f"Generating embeddings for {len(texts)} chunks...")
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
            
            app_logger.info(f"✅ Added {len(chunks)} chunks to vector store")
            return vector_ids
        
        except Exception as e:
            app_logger.error(f"❌ Error adding documents: {str(e)}")
            app_logger.error(f"Traceback: {traceback.format_exc()}")
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
            # ✅ FIX: Check if index exists and has vectors
            if self.index is None:
                app_logger.warning("⚠️ FAISS index is None")
                return []
            
            if self.index.ntotal == 0:
                app_logger.warning("⚠️ Vector store is empty - no documents indexed yet")
                return []
            
            # Generate query embedding
            query_embedding = embedding_service.generate_query_embedding(query)
            query_vector = np.array([query_embedding], dtype='float32')
            
            # Search in FAISS
            distances, indices = self.index.search(query_vector, min(top_k * 3, self.index.ntotal))
            
            # Prepare results
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx == -1:  # FAISS returns -1 for empty slots
                    continue
                
                if idx not in self.document_map:
                    app_logger.warning(f"⚠️ Vector ID {idx} not in document map")
                    continue
                
                doc_info = self.document_map[idx]
                
                # Filter by file_ids if provided
                if file_ids and doc_info.get('file_id') not in file_ids:
                    continue
                
                # Convert L2 distance to similarity score (0-1)
                similarity = 1 / (1 + float(dist))
                
                results.append({
                    'file_id': doc_info.get('file_id'),
                    'chunk_id': doc_info.get('chunk_id'),
                    'chunk_index': doc_info.get('chunk_index'),
                    'content': doc_info.get('content'),
                    'page_number': doc_info.get('page_number'),
                    'filename': doc_info.get('filename'),
                    'relevance_score': similarity
                })
            
            # Return top_k results
            results = results[:top_k]
            
            if results:
                app_logger.info(f"✅ Found {len(results)} relevant chunks for query")
            else:
                app_logger.warning("⚠️ No relevant chunks found for query")
            
            return results
        
        except Exception as e:
            app_logger.error(f"❌ Search error: {str(e)}")
            app_logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    def delete_file_vectors(self, file_id: int):
        """
        Delete all vectors for a specific file
        NOTE: FAISS doesn't support deletion, so we rebuild the entire index
        """
        try:
            app_logger.info(f"Deleting vectors for file_id={file_id}")
            
            # Find vectors to keep (not matching file_id)
            vectors_to_keep = {}
            for vector_id, doc_info in self.document_map.items():
                if doc_info.get('file_id') != file_id:
                    vectors_to_keep[vector_id] = doc_info
            
            if len(vectors_to_keep) == len(self.document_map):
                app_logger.info(f"No vectors found for file_id {file_id}")
                return
            
            # Rebuild index with remaining vectors
            if len(vectors_to_keep) > 0:
                app_logger.info(f"Rebuilding index: {len(self.document_map)} → {len(vectors_to_keep)} vectors")
                
                # Get chunks from database to regenerate embeddings
                db = SessionLocal()
                try:
                    chunk_ids = [doc['chunk_id'] for doc in vectors_to_keep.values()]
                    chunks = db.query(Chunk).filter(Chunk.id.in_(chunk_ids)).all()
                    
                    # Recreate index
                    self._create_new_index()
                    
                    # Re-add chunks
                    chunk_data = []
                    for chunk in chunks:
                        chunk_data.append({
                            'file_id': chunk.file_id,
                            'chunk_id': chunk.id,
                            'chunk_index': chunk.chunk_index,
                            'content': chunk.content,
                            'page_number': chunk.page_number,
                            'filename': chunk.file.original_filename if chunk.file else 'Unknown'
                        })
                    
                    if chunk_data:
                        self.add_documents(chunk_data)
                        app_logger.info(f"✅ Rebuilt index with {len(chunk_data)} chunks")
                    
                finally:
                    db.close()
            else:
                # No vectors left, create empty index
                app_logger.info("No vectors remaining, creating empty index")
                self._create_new_index()
                self._save_index()
        
        except Exception as e:
            app_logger.error(f"❌ Error deleting file vectors: {str(e)}")


# Global instance
rag_service = RAGService()
