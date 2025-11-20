"""
LLM service using Google Gemini API (FREE)
Handles text generation, chat completions, and streaming
"""

import google.generativeai as genai
from typing import List, Dict, Generator, Optional
from app.utils.logger import app_logger
from app.config import settings
import time


class LLMService:
    """Service for LLM operations using Gemini"""
    
    def __init__(self):
        """Initialize Gemini LLM"""
        try:
            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not configured")
            
            # Configure Gemini API
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            # Initialize model
            self.model = genai.GenerativeModel(settings.LLM_MODEL)
            
            # Generation config
            self.generation_config = {
                "temperature": settings.LLM_TEMPERATURE,
                "max_output_tokens": settings.LLM_MAX_TOKENS,
                "top_p": 0.95,
                "top_k": 40
            }
            
            # Safety settings (minimal restrictions for business use)
            self.safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
            ]
            
            app_logger.info(f"✅ Gemini LLM service initialized")
            app_logger.info(f"   Model: {settings.LLM_MODEL}")
            app_logger.info(f"   Temperature: {settings.LLM_TEMPERATURE}")
            
        except Exception as e:
            app_logger.error(f"❌ Error initializing Gemini LLM: {str(e)}")
            raise
    
    def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        retry_count: int = 3
    ) -> str:
        """
        Generate a response using Gemini
        
        Args:
            prompt: User prompt
            context: Optional context from RAG
            retry_count: Number of retries on failure
        
        Returns:
            Generated response text
        """
        for attempt in range(retry_count):
            try:
                # Build full prompt with context
                if context:
                    full_prompt = f"""Context from documents:
{context}

User question: {prompt}

Please provide a detailed answer based on the context above. Include relevant details and cite sources when possible."""
                else:
                    full_prompt = prompt
                
                # Generate response
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=self.generation_config,
                    safety_settings=self.safety_settings
                )
                
                return response.text
                
            except Exception as e:
                app_logger.warning(f"Generation attempt {attempt + 1} failed: {str(e)}")
                if attempt < retry_count - 1:
                    time.sleep(1)
                else:
                    app_logger.error(f"❌ Failed to generate response after {retry_count} attempts")
                    return "I apologize, but I'm having trouble generating a response right now. Please try again."
    
    def generate_response_stream(
        self,
        prompt: str,
        context: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Generate streaming response using Gemini
        
        Args:
            prompt: User prompt
            context: Optional context from RAG
        
        Yields:
            Chunks of generated text
        """
        try:
            # Build full prompt with context
            if context:
                full_prompt = f"""Context from documents:
{context}

User question: {prompt}

Please provide a detailed answer based on the context above. Include relevant details and cite sources when possible."""
            else:
                full_prompt = prompt
            
            # Generate streaming response
            response = self.model.generate_content(
                full_prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings,
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            app_logger.error(f"❌ Streaming error: {str(e)}")
            yield "I apologize, but I encountered an error while generating the response."
    
    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        context: Optional[str] = None
    ) -> str:
        """
        Generate chat response with conversation history
        
        Args:
            messages: List of conversation messages [{"role": "user/assistant", "content": "..."}]
            context: Optional context from RAG
        
        Returns:
            Generated response text
        """
        try:
            # Start chat session
            chat = self.model.start_chat(history=[])
            
            # Add context as system message if provided
            if context:
                context_message = f"Context from documents:\n{context}\n\nPlease use this context to answer questions."
                chat.send_message(context_message)
            
            # Add conversation history (except last user message)
            for msg in messages[:-1]:
                if msg["role"] == "user":
                    chat.send_message(msg["content"])
            
            # Send final user message and get response
            last_message = messages[-1]["content"]
            response = chat.send_message(
                last_message,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            return response.text
            
        except Exception as e:
            app_logger.error(f"❌ Chat generation error: {str(e)}")
            return "I apologize, but I'm having trouble with the chat right now. Please try again."
    
    def generate_summary(self, text: str, max_length: int = 200) -> str:
        """
        Generate a concise summary of text
        
        Args:
            text: Text to summarize
            max_length: Maximum summary length
        
        Returns:
            Summary text
        """
        try:
            prompt = f"""Provide a concise summary of the following text in approximately {max_length} words:

{text}

Summary:"""
            
            response = self.model.generate_content(
                prompt,
                generation_config={"temperature": 0.3, "max_output_tokens": max_length * 2}
            )
            
            return response.text
            
        except Exception as e:
            app_logger.error(f"❌ Summary generation error: {str(e)}")
            return text[:max_length] + "..."
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        Extract key terms from text
        
        Args:
            text: Input text
            max_keywords: Maximum number of keywords
        
        Returns:
            List of keywords
        """
        try:
            prompt = f"""Extract the {max_keywords} most important keywords or key phrases from this text.
Return only the keywords, separated by commas:

{text}

Keywords:"""
            
            response = self.model.generate_content(
                prompt,
                generation_config={"temperature": 0.1, "max_output_tokens": 200}
            )
            
            # Parse keywords
            keywords = [k.strip() for k in response.text.split(",")]
            return keywords[:max_keywords]
            
        except Exception as e:
            app_logger.error(f"❌ Keyword extraction error: {str(e)}")
            return []


# Global instance
llm_service = LLMService()
