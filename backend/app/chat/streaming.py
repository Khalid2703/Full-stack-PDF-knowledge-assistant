"""
Server-Sent Events (SSE) streaming for real-time responses
"""

import json
import asyncio
from typing import AsyncGenerator, Dict, Any
from app.utils.logger import app_logger


class StreamingManager:
    """
    Manage SSE streaming for chat responses
    """
    
    @staticmethod
    async def stream_response(
        generator,
        include_metadata: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Stream response as SSE events
        
        Args:
            generator: Answer generator
            include_metadata: Include metadata in stream
        
        Yields:
            SSE formatted strings
        """
        try:
            # Send initial event
            yield StreamingManager._format_sse({
                "type": "start",
                "message": "Starting response generation..."
            })
            
            # Stream answer chunks
            async for chunk in StreamingManager._async_wrap(generator):
                if chunk:
                    yield StreamingManager._format_sse({
                        "type": "content",
                        "content": chunk
                    })
                    
                    # Small delay to prevent overwhelming client
                    await asyncio.sleep(0.01)
            
            # Send completion event
            yield StreamingManager._format_sse({
                "type": "done",
                "message": "Response generation complete"
            })
        
        except Exception as e:
            app_logger.error(f"Streaming error: {str(e)}")
            yield StreamingManager._format_sse({
                "type": "error",
                "message": str(e)
            })
    
    @staticmethod
    async def stream_with_sources(
        answer_generator,
        chunks: list,
        include_citations: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Stream response with source citations
        
        Args:
            answer_generator: Answer generator
            chunks: Source chunks
            include_citations: Include citation metadata
        
        Yields:
            SSE formatted strings with sources
        """
        try:
            # Send sources first
            yield StreamingManager._format_sse({
                "type": "sources",
                "data": {
                    "count": len(chunks),
                    "sources": [
                        {
                            "id": i + 1,
                            "filename": chunk["filename"],
                            "page": chunk.get("page_number"),
                            "relevance": chunk.get("relevance_score", 0)
                        }
                        for i, chunk in enumerate(chunks)
                    ]
                }
            })
            
            # Stream answer
            yield StreamingManager._format_sse({
                "type": "start",
                "message": "Generating answer..."
            })
            
            async for chunk in StreamingManager._async_wrap(answer_generator):
                if chunk:
                    yield StreamingManager._format_sse({
                        "type": "content",
                        "content": chunk
                    })
                    await asyncio.sleep(0.01)
            
            # Send citations if requested
            if include_citations:
                from app.chat.citation_engine import citation_engine
                # Note: Full answer needs to be assembled on client side
                yield StreamingManager._format_sse({
                    "type": "citations",
                    "data": {
                        "format": "numbered",
                        "citations": citation_engine.format_citations(chunks)
                    }
                })
            
            yield StreamingManager._format_sse({
                "type": "done",
                "message": "Complete"
            })
        
        except Exception as e:
            app_logger.error(f"Streaming with sources error: {str(e)}")
            yield StreamingManager._format_sse({
                "type": "error",
                "message": str(e)
            })
    
    @staticmethod
    def _format_sse(data: Dict[str, Any]) -> str:
        """
        Format data as SSE event
        
        Args:
            data: Data to send
        
        Returns:
            SSE formatted string
        """
        json_data = json.dumps(data)
        return f"data: {json_data}\n\n"
    
    @staticmethod
    async def _async_wrap(generator):
        """
        Wrap synchronous generator as async generator
        
        Args:
            generator: Synchronous generator
        
        Yields:
            Items from generator
        """
        for item in generator:
            yield item
            await asyncio.sleep(0)  # Allow other tasks to run


# Global instance
streaming_manager = StreamingManager()
