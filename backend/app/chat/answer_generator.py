"""
Answer generation using Google Gemini API (FREE)
Optimized for conversational, context-aware responses
"""

from typing import List, Dict, Optional, Tuple
import time
from app.utils.logger import app_logger
from app.config import settings

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    app_logger.warning("google-generativeai not installed")


class AnswerGenerator:
    """
    Answer generation using Gemini API with intelligent fallback
    """
    
    def __init__(self):
        """Initialize Gemini AI"""
        self.gemini_available = False
        self.model = None
        
        if GEMINI_AVAILABLE and settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.model = genai.GenerativeModel(
                    model_name=settings.LLM_MODEL or 'gemini-1.5-pro',
                    generation_config={
                        'temperature': 0.3,
                        'max_output_tokens': 2048,
                    }
                )
                self.gemini_available = True
                app_logger.info("✅ Gemini AI initialized successfully")
            except Exception as e:
                app_logger.error(f"❌ Gemini initialization failed: {str(e)}")
        else:
            app_logger.warning("⚠️ Gemini API key not configured")
    
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
            "model_used": "gemini" if self.gemini_available else "template",
            "tokens_used": 0,
            "generation_time": 0,
            "chunks_used": len(chunks)
        }
        
        # Prioritize Gemini - try it first
        if self.gemini_available:
            try:
                app_logger.info(f"🤖 Using Gemini AI to generate answer (model: {settings.LLM_MODEL})")
                answer, meta = self._generate_with_gemini(
                    query, context, chunks, use_citations
                )
                metadata.update(meta)
                metadata["generation_time"] = time.time() - start_time
                app_logger.info(f"✅ Gemini answer generated successfully in {metadata['generation_time']:.2f}s")
                return answer, metadata
            except Exception as e:
                error_msg = str(e)
                app_logger.error(f"❌ Gemini generation failed: {error_msg}")
                
                # If it's a quota error, provide helpful message
                if 'quota' in error_msg.lower() or '429' in error_msg:
                    app_logger.error(f"💡 Gemini quota exceeded. Check usage at: https://ai.dev/usage?tab=rate-limit")
                    app_logger.info(f"📝 Falling back to template-based answer generation")
                else:
                    app_logger.warning(f"⚠️ Falling back to template-based answer generation")
        else:
            app_logger.info(f"⚠️ Gemini not available. Using template-based answer generation")
        
        # Fallback to smart template
        app_logger.info(f"📝 Generating template-based answer...")
        answer, meta = self._generate_smart_template(query, context, chunks, use_citations)
        metadata.update(meta)
        metadata["generation_time"] = time.time() - start_time
        app_logger.info(f"✅ Template answer generated in {metadata['generation_time']:.2f}s")
        return answer, metadata
    
    def _generate_with_gemini(
        self,
        query: str,
        context: str,
        chunks: List[Dict],
        use_citations: bool
    ) -> Tuple[str, Dict]:
        """Generate answer using Gemini with optimized prompt"""
        
        # Build comprehensive prompt
        system_instructions = """You are an intelligent AI assistant helping users understand their documents.

CRITICAL RULES:
1. Answer based ONLY on the provided context
2. Be conversational and helpful
3. Cite sources using [Source N] format
4. If context doesn't have the answer, say so clearly
5. Provide specific details, numbers, and quotes when available
6. Keep responses focused and well-structured
7. Use bullet points for lists
8. Bold important terms with **text**"""

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
        
        # Build final prompt
        if use_citations:
            prompt = f"""{system_instructions}

AVAILABLE CONTEXT:
{context_text}

USER QUESTION: {query}

INSTRUCTIONS:
- Provide a detailed, conversational answer
- Reference sources as [Source 1], [Source 2], etc.
- Include specific details from the documents
- Structure your answer clearly
- If multiple sources are relevant, synthesize the information

ANSWER:"""
        else:
            prompt = f"""{system_instructions}

CONTEXT:
{context_text}

QUESTION: {query}

Provide a clear, detailed answer based on the context above."""
        
        try:
            response = self.model.generate_content(prompt)
            answer = response.text
            
            metadata = {
                "model_used": "gemini-1.5-pro",
                "tokens_used": len(answer.split()),  # Approximate
            }
            
            app_logger.info(f"✅ Gemini answer generated: {len(answer)} chars")
            return answer, metadata
        
        except Exception as e:
            app_logger.error(f"Gemini API error: {str(e)}")
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
        
        Yields:
            Chunks of text as they're generated
        """
        if not self.gemini_available:
            # Non-streaming fallback
            answer, _ = self._generate_smart_template(query, context, chunks, use_citations)
            # Simulate streaming by yielding words
            words = answer.split()
            for word in words:
                yield word + " "
                time.sleep(0.02)  # Small delay for effect
            return
        
        # Build Gemini prompt (same as non-streaming)
        system_instructions = """You are a helpful AI assistant. Answer based on the provided context.
Use [Source N] citations. Be conversational and detailed."""
        
        formatted_context = []
        for i, chunk in enumerate(chunks[:10], 1):
            filename = chunk.get('filename', 'Unknown')
            content = chunk.get('content', '')
            formatted_context.append(f"[Source {i}] {filename}\n{content}\n")
        
        context_text = "\n---\n".join(formatted_context)
        
        prompt = f"""{system_instructions}

CONTEXT:
{context_text}

QUESTION: {query}

Provide a detailed answer with citations."""
        
        try:
            response = self.model.generate_content(
                prompt,
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        
        except Exception as e:
            app_logger.error(f"Streaming error: {str(e)}")
            yield f"\n\nError: {str(e)}"


# Global instance
answer_generator = AnswerGenerator()
