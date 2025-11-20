"""
Enhanced RAG Pipeline with Fast and Accurate modes
Supports dual retrieval strategies with configurable parameters
"""

from typing import List, Dict, Optional, Tuple
from enum import Enum
import traceback
import time
from app.services.rag_service import rag_service
from app.services.embedding_service import embedding_service
from app.utils.logger import app_logger


class RAGMode(str, Enum):
    """RAG execution modes"""
    FAST = "fast"           # Quick retrieval, fewer chunks, basic ranking
    ACCURATE = "accurate"   # Deep retrieval, more chunks, reranking


class RAGPipeline:
    """
    Enhanced RAG pipeline with multiple modes and traceability
    """
    
    def __init__(self):
        """Initialize RAG pipeline"""
        self.mode_configs = {
            RAGMode.FAST: {
                "top_k": 5,
                "use_reranking": False,
                "chunk_overlap": 100,
                "retrieval_timeout": 2.0,
                "min_relevance_score": 0.3
            },
            RAGMode.ACCURATE: {
                "top_k": 15,
                "use_reranking": True,
                "chunk_overlap": 200,
                "retrieval_timeout": 10.0,
                "min_relevance_score": 0.2,
                "rerank_top_k": 5
            }
        }
    
    def retrieve(
        self,
        query: str,
        mode: RAGMode = RAGMode.FAST,
        file_ids: Optional[List[int]] = None,
        custom_config: Optional[Dict] = None
    ) -> Tuple[List[Dict], Dict]:
        """
        Retrieve relevant chunks with traceability
        
        Args:
            query: User query
            mode: RAG mode (fast or accurate)
            file_ids: Optional file IDs to filter
            custom_config: Override default config
        
        Returns:
            Tuple of (chunks, trace_data)
        """
        start_time = time.time()
        
        # Get configuration
        config = self.mode_configs[mode].copy()
        if custom_config:
            config.update(custom_config)
        
        trace_data = {
            "mode": mode,
            "query": query,
            "config": config,
            "timestamps": {
                "start": start_time
            }
        }
        
        try:
            # Step 1: Initial retrieval
            app_logger.info(f"RAG Pipeline: {mode} mode - Retrieving {config['top_k']} chunks")
            
            retrieval_start = time.time()
            chunks = rag_service.search(
                query=query,
                top_k=config['top_k'],
                file_ids=file_ids
            )
            retrieval_time = time.time() - retrieval_start
            
            trace_data["timestamps"]["retrieval_end"] = time.time()
            trace_data["retrieval_time"] = retrieval_time
            trace_data["initial_chunks_count"] = len(chunks)
            
            # Step 2: Filter by relevance threshold
            filtered_chunks = [
                chunk for chunk in chunks
                if chunk['relevance_score'] >= config['min_relevance_score']
            ]
            
            trace_data["filtered_chunks_count"] = len(filtered_chunks)
            trace_data["chunks_removed"] = len(chunks) - len(filtered_chunks)
            
            # Step 3: Apply reranking if in accurate mode
            if config.get('use_reranking') and len(filtered_chunks) > 0:
                from app.chat.reranker import reranker
                
                rerank_start = time.time()
                reranked_chunks = reranker.rerank(
                    query=query,
                    chunks=filtered_chunks,
                    top_k=config.get('rerank_top_k', 5)
                )
                rerank_time = time.time() - rerank_start
                
                trace_data["timestamps"]["rerank_end"] = time.time()
                trace_data["rerank_time"] = rerank_time
                trace_data["final_chunks_count"] = len(reranked_chunks)
                
                final_chunks = reranked_chunks
            else:
                final_chunks = filtered_chunks[:config.get('rerank_top_k', 5)]
                trace_data["final_chunks_count"] = len(final_chunks)
            
            # Add traceability data to each chunk
            for i, chunk in enumerate(final_chunks):
                chunk['trace'] = {
                    'rank': i + 1,
                    'original_rank': chunks.index(chunk) + 1 if chunk in chunks else -1,
                    'mode': mode,
                    'reranked': config.get('use_reranking', False)
                }
            
            total_time = time.time() - start_time
            trace_data["timestamps"]["end"] = time.time()
            trace_data["total_time"] = total_time
            trace_data["success"] = True
            
            app_logger.info(f"RAG Pipeline: Retrieved {len(final_chunks)} chunks in {total_time:.2f}s")
            
            return final_chunks, trace_data
        
        except Exception as e:
            trace_data["success"] = False
            error_msg = str(e) if str(e) else type(e).__name__
            trace_data["error"] = error_msg
            trace_data["timestamps"]["end"] = time.time()
            trace_data["total_time"] = time.time() - start_time
            
            app_logger.error(f"RAG Pipeline error: {error_msg}", exc_info=True)
            app_logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def build_context(self, chunks: List[Dict], max_tokens: int = 4000) -> str:
        """
        Build context string from retrieved chunks
        
        Args:
            chunks: List of chunk dictionaries
            max_tokens: Maximum context length (approximate)
        
        Returns:
            Formatted context string
        """
        context_parts = []
        total_chars = 0
        max_chars = max_tokens * 4  # Rough estimate: 1 token ≈ 4 chars
        
        for i, chunk in enumerate(chunks):
            chunk_text = f"""
--- Source {i+1}: {chunk['filename']} (Page {chunk.get('page_number', 'N/A')}) ---
{chunk['content']}
---
"""
            chunk_chars = len(chunk_text)
            
            if total_chars + chunk_chars > max_chars:
                app_logger.warning(f"Context limit reached, using {i} chunks")
                break
            
            context_parts.append(chunk_text)
            total_chars += chunk_chars
        
        return "\n".join(context_parts)
    
    def generate_heatmap_data(self, chunks: List[Dict], trace_data: Dict) -> Dict:
        """
        Generate traceability heatmap data for visualization
        
        Args:
            chunks: Retrieved chunks
            trace_data: Trace data from retrieval
        
        Returns:
            Heatmap data structure
        """
        heatmap = {
            "mode": trace_data["mode"],
            "total_time": trace_data["total_time"],
            "retrieval_stages": [
                {
                    "stage": "initial_retrieval",
                    "time": trace_data.get("retrieval_time", 0),
                    "chunks_count": trace_data.get("initial_chunks_count", 0)
                },
                {
                    "stage": "filtering",
                    "time": 0.01,  # Minimal time
                    "chunks_count": trace_data.get("filtered_chunks_count", 0)
                }
            ],
            "chunks": []
        }
        
        # Add reranking stage if used
        if trace_data["config"].get("use_reranking"):
            heatmap["retrieval_stages"].append({
                "stage": "reranking",
                "time": trace_data.get("rerank_time", 0),
                "chunks_count": trace_data.get("final_chunks_count", 0)
            })
        
        # Add chunk-level data
        for chunk in chunks:
            heatmap["chunks"].append({
                "file_id": chunk["file_id"],
                "filename": chunk["filename"],
                "chunk_index": chunk["chunk_index"],
                "relevance_score": chunk["relevance_score"],
                "rank": chunk.get("trace", {}).get("rank", 0),
                "original_rank": chunk.get("trace", {}).get("original_rank", 0),
                "reranked": chunk.get("trace", {}).get("reranked", False),
                "page_number": chunk.get("page_number")
            })
        
        return heatmap


# Global instance
rag_pipeline = RAGPipeline()
