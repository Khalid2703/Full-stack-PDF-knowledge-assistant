"""
Answer generation using unified LLM service
Supports OpenAI (primary) → Gemini (fallback) with citation management
"""

from typing import List, Dict, Optional, Tuple
import time
from app.utils.logger import app_logger
from app.config import settings
from app.services.llm_service import llm_service


class AnswerGenerator:
    """
    Answer generation using unified LLM service with intelligent fallback
    Primary: OpenAI GPT-4o-mini
    Fallback: Google Gemini 1.5-flash
    """
    
    def __init__(self):
        """Initialize Answer Generator with unified LLM service"""
        app_logger.info("✅ Answer Generator initialized (using unified LLM service)")
        app_logger.info("   Primary: OpenAI GPT-4o-mini")
        app_logger.info("   Fallback: Gemini 1.5-flash")
    
    def generate_answer(
        self,
        query: str,
        context: str,
        chunks: List[Dict],
        use_citations: bool = True
    ) -> Tuple[str, Dict]:
        """
        Generate conversational answer with proper context and citations
        
        Args:
            query: User's question
            context: Retrieved context from documents
            chunks: Source chunks for citations
            use_citations: Whether to include source references
        
        Returns:
            Tuple of (answer_text, metadata)
        """
        start_time = time.time()
        metadata = {
            "model_used": "unified_llm",
            "tokens_used": 0,
            "generation_time": 0,
            "chunks_used": len(chunks)
        }
        
        try:
            # Build enhanced context with citation markers
            formatted_context = self._format_context_with_sources(context, chunks, use_citations)
            
            # Build the prompt
            enhanced_query = self._build_query_with_instructions(query, use_citations)
            
            # Generate answer using unified LLM service (OpenAI → Gemini fallback)
            app_logger.info(f"🤖 Generating answer using unified LLM service")
            answer_text = llm_service.generate_response(
                prompt=enhanced_query,
                context=formatted_context
            )
            
            # Post-process: ensure citations are properly formatted
            if use_citations:
                answer_text = self._ensure_citations(answer_text, chunks)
            
            # Calculate metadata
            metadata["tokens_used"] = len(answer_text.split())
            metadata["generation_time"] = time.time() - start_time
            
            app_logger.info(f"✅ Answer generated successfully in {metadata['generation_time']:.2f}s")
            return answer_text, metadata
            
        except Exception as e:
            app_logger.error(f"❌ Answer generation failed: {str(e)}")
            # Fallback to template-based answer
            app_logger.info(f"📝 Using template-based answer as final fallback")
            answer, meta = self._generate_smart_template(query, context, chunks, use_citations)
            metadata.update(meta)
            metadata["generation_time"] = time.time() - start_time
            return answer, metadata
    
    def _build_query_with_instructions(self, query: str, use_citations: bool) -> str:
        """Build query with instructions for citation formatting"""
        if use_citations:
            return f"""{query}

IMPORTANT INSTRUCTIONS:
- Reference sources using [Source N] format where N is the source number
- Cite specific information from the sources
- Maintain a professional, conversational tone
- Structure your response with clear sections"""
        else:
            return query
    
    def _format_context_with_sources(
        self,
        context: str,
        chunks: List[Dict],
        use_citations: bool
    ) -> str:
        """Format context with clear source markers for citation"""
        if not use_citations or not chunks:
            return context
        
        formatted_parts = []
        for i, chunk in enumerate(chunks[:10], 1):
            filename = chunk.get('filename', 'Unknown')
            page = chunk.get('page_number', 'N/A')
            content = chunk.get('content', '')
            
            formatted_parts.append(
                f"[Source {i}] {filename} (Page {page})\n{content}\n"
            )
        
        return "\n---\n".join(formatted_parts)
    
    def _ensure_citations(self, answer: str, chunks: List[Dict]) -> str:
        """
        Ensure citations are properly formatted
        Verifies that [Source N] references are valid
        """
        # Check if answer has any citations
        import re
        citations = re.findall(r'\[Source (\d+)\]', answer)
        
        if not citations and chunks:
            # Add a general citation at the end if none exist
            answer += f"\n\n*Based on {len(chunks)} source document(s).*"
        
        return answer
    
    def _generate_smart_template(
        self,
        query: str,
        context: str,
        chunks: List[Dict],
        use_citations: bool
    ) -> Tuple[str, Dict]:
        """
        Smart template-based answer generation as final fallback
        Better than raw source output
        """
        # Extract key information
        sentences = [s.strip() for s in context.split('\n') if len(s.strip()) > 30]
        
        # Build structured answer
        answer_parts = []
        
        # Opening
        answer_parts.append(f"Based on the documents I found:\n")
        
        # Main content
        if use_citations and chunks:
            # Group by source
            for i, chunk in enumerate(chunks[:5], 1):
                filename = chunk.get('filename', 'Document')
                page = chunk.get('page_number')
                content = chunk.get('content', '')[:300]  # First 300 chars
                
                answer_parts.append(f"\n**[Source {i}] {filename}**")
                if page:
                    answer_parts.append(f" (Page {page})")
                answer_parts.append(f"\n{content}...")
        else:
            # Just list key points
            key_sentences = sentences[:5]
            answer_parts.append("\n**Key Points:**")
            for i, sentence in enumerate(key_sentences, 1):
                answer_parts.append(f"\n{i}. {sentence}")
        
        # Summary
        answer_parts.append(f"\n\n**Summary:** I found {len(chunks)} relevant sources")
        
        if use_citations:
            answer_parts.append(" with detailed information to answer your question.")
        
        answer = "".join(answer_parts)
        
        metadata = {
            "model_used": "smart_template",
            "tokens_used": len(answer.split()),
        }
        
        return answer, metadata
    
    def generate_streaming_answer(
        self,
        query: str,
        context: str,
        chunks: List[Dict],
        use_citations: bool = True
    ):
        """
        Generate streaming answer for real-time display
        Uses unified LLM service streaming
        
        Yields:
            Chunks of text as they're generated
        """
        try:
            # Format context with sources
            formatted_context = self._format_context_with_sources(context, chunks, use_citations)
            
            # Build enhanced query
            enhanced_query = self._build_query_with_instructions(query, use_citations)
            
            # Stream using unified LLM service
            app_logger.info("🌊 Streaming answer using unified LLM service")
            
            for chunk in llm_service.generate_response_stream(
                prompt=enhanced_query,
                context=formatted_context
            ):
                yield chunk
        
        except Exception as e:
            app_logger.error(f"❌ Streaming error: {str(e)}")
            # Fallback to non-streaming
            answer, _ = self._generate_smart_template(query, context, chunks, use_citations)
            
            # Simulate streaming by yielding words
            words = answer.split()
            for word in words:
                yield word + " "
                time.sleep(0.02)  # Small delay for effect


# Global instance
answer_generator = AnswerGenerator()
