"""
Answer generation using dual LLM support
Primary: OpenAI GPT-4o-mini (fast, high-quality)
Fallback: Google Gemini (free tier)
"""

from typing import List, Dict, Optional, Tuple
import time
from app.utils.logger import app_logger
from app.config import settings
from app.services.llm_service import llm_service


class AnswerGenerator:
    """
    Answer generation using LLM service with intelligent fallback
    Uses OpenAI GPT-4o-mini as primary, Gemini as fallback
    """
    
    def __init__(self):
        """Initialize answer generator with LLM service"""
        # Check if we have any LLM available
        self.llm_available = llm_service.use_openai or (llm_service.gemini_model is not None)
        
        if self.llm_available:
            if llm_service.use_openai:
                app_logger.info("✅ Answer Generator initialized with OpenAI GPT-4o-mini (PRIMARY)")
            else:
                app_logger.info(f"✅ Answer Generator initialized with Gemini (FALLBACK)")
        else:
            app_logger.warning("⚠️ No LLM available - will use template-based answers only")
    
    def generate_answer(
        self,
        query: str,
        context: str,
        chunks: List[Dict],
        use_citations: bool = True
    ) -> Tuple[str, Dict]:
        """
        Generate conversational answer with proper context
        
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
            "model_used": "unknown",
            "tokens_used": 0,
            "generation_time": 0,
            "chunks_used": len(chunks)
        }
        
        # Try LLM generation if available
        if self.llm_available:
            try:
                app_logger.info("🤖 Using LLM service to generate answer")
                answer, meta = self._generate_with_llm(
                    query, context, chunks, use_citations
                )
                metadata.update(meta)
                metadata["generation_time"] = time.time() - start_time
                app_logger.info(f"✅ LLM answer generated successfully in {metadata['generation_time']:.2f}s")
                return answer, metadata
            except Exception as e:
                error_msg = str(e)
                app_logger.error(f"❌ LLM generation failed: {error_msg}", exc_info=True)
                
                # Check if it's a quota/rate limit error
                if any(keyword in error_msg.lower() for keyword in ['quota', '429', 'rate limit', 'insufficient_quota']):
                    app_logger.warning("💡 LLM quota/rate limit exceeded")
                
                app_logger.info("📝 Falling back to template-based answer generation")
        else:
            app_logger.info("⚠️ No LLM available. Using template-based answer generation")
        
        # Fallback to smart template
        app_logger.info("📝 Generating template-based answer...")
        answer, meta = self._generate_smart_template(query, context, chunks, use_citations)
        metadata.update(meta)
        metadata["generation_time"] = time.time() - start_time
        app_logger.info(f"✅ Template answer generated in {metadata['generation_time']:.2f}s")
        return answer, metadata
    
    def _generate_with_llm(
        self,
        query: str,
        context: str,
        chunks: List[Dict],
        use_citations: bool
    ) -> Tuple[str, Dict]:
        """Generate answer using LLM service (OpenAI or Gemini)"""
        
        # Build context with source labels
        formatted_context = []
        for i, chunk in enumerate(chunks[:10], 1):
            filename = chunk.get('filename', 'Unknown')
            page = chunk.get('page_number', 'N/A')
            content = chunk.get('content', '')
            formatted_context.append(
                f"[Source {i}] - {filename} (Page {page})\n{content}\n"
            )
        
        context_text = "\n---\n".join(formatted_context)
        
        # Build prompt with instructions
        if use_citations:
            prompt = f"""Based on the following context from documents, answer the user's question.

IMPORTANT INSTRUCTIONS:
1. Answer based ONLY on the provided context
2. Be conversational and helpful
3. Cite sources using [Source N] format
4. If context doesn't have the answer, say so clearly
5. Provide specific details, numbers, and quotes when available
6. Keep responses focused and well-structured
7. Use bullet points for lists
8. Bold important terms with **text**

AVAILABLE CONTEXT:
{context_text}

USER QUESTION: {query}

Please provide a detailed, conversational answer with proper source citations."""
        else:
            prompt = f"""Based on the following context, answer the user's question clearly and concisely.

CONTEXT:
{context_text}

QUESTION: {query}

Provide a clear, detailed answer based on the context above."""
        
        try:
            # Use llm_service to generate response
            answer = llm_service.generate_response(
                prompt=prompt,
                context=context_text
            )
            
            # Determine which model was used
            model_name = "openai-gpt-4o-mini" if llm_service.use_openai else f"gemini-{settings.LLM_MODEL}"
            
            metadata = {
                "model_used": model_name,
                "tokens_used": len(answer.split()),  # Approximate
            }
            
            app_logger.info(f"✅ LLM answer generated: {len(answer)} chars using {model_name}")
            return answer, metadata
        
        except Exception as e:
            app_logger.error(f"LLM API error: {str(e)}")
            raise
    
    def _generate_smart_template(
        self,
        query: str,
        context: str,
        chunks: List[Dict],
        use_citations: bool
    ) -> Tuple[str, Dict]:
        """
        Smart template-based answer generation
        Used as fallback when LLM is unavailable or fails
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
        
        Yields:
            Chunks of text as they're generated
        """
        if not self.llm_available:
            # Non-streaming fallback
            answer, _ = self._generate_smart_template(query, context, chunks, use_citations)
            # Simulate streaming by yielding words
            words = answer.split()
            for word in words:
                yield word + " "
                time.sleep(0.02)  # Small delay for effect
            return
        
        # Build context with source labels
        formatted_context = []
        for i, chunk in enumerate(chunks[:10], 1):
            filename = chunk.get('filename', 'Unknown')
            content = chunk.get('content', '')
            formatted_context.append(f"[Source {i}] {filename}\n{content}\n")
        
        context_text = "\n---\n".join(formatted_context)
        
        # Build prompt
        prompt = f"""Based on the following context, answer the user's question with proper citations.

CONTEXT:
{context_text}

QUESTION: {query}

Provide a detailed answer with [Source N] citations."""
        
        try:
            # Use llm_service streaming
            for chunk in llm_service.generate_response_stream(
                prompt=prompt,
                context=context_text
            ):
                yield chunk
        
        except Exception as e:
            app_logger.error(f"Streaming error: {str(e)}")
            # Fallback to template
            answer, _ = self._generate_smart_template(query, context, chunks, use_citations)
            words = answer.split()
            for word in words:
                yield word + " "
                time.sleep(0.02)


# Global instance
answer_generator = AnswerGenerator()
