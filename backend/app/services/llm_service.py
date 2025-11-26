"""
LLM service supporting both OpenAI and Google Gemini
Primary: OpenAI GPT-4o-mini
Fallback: Google Gemini
"""

import google.generativeai as genai
from openai import OpenAI
from typing import List, Dict, Generator, Optional
from app.utils.logger import app_logger
from app.config import settings
import time


class LLMService:
    """Service for LLM operations with dual provider support"""
    
    def __init__(self):
        """Initialize LLM services (OpenAI primary, Gemini fallback)"""
        self.openai_client = None
        self.gemini_model = None
        self.use_openai = False
        
        # Try OpenAI first
        if settings.OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
                # Test the connection
                self.openai_client.models.list()
                self.use_openai = True
                app_logger.info("✅ OpenAI GPT-4o-mini service initialized (PRIMARY)")
                app_logger.info("   Model: gpt-4o-mini")
                app_logger.info(f"   Temperature: {settings.LLM_TEMPERATURE}")
            except Exception as e:
                app_logger.warning(f"⚠️ OpenAI initialization failed: {str(e)}")
                self.openai_client = None
        
        # Fallback to Gemini
        if not self.use_openai:
            try:
                if not settings.GEMINI_API_KEY:
                    raise ValueError("Neither OPENAI_API_KEY nor GEMINI_API_KEY configured")
                
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel(settings.LLM_MODEL)
                
                self.gemini_config = {
                    "temperature": settings.LLM_TEMPERATURE,
                    "max_output_tokens": settings.LLM_MAX_TOKENS,
                    "top_p": 0.95,
                    "top_k": 40
                }
                
                self.safety_settings = [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
                ]
                
                app_logger.info("✅ Gemini LLM service initialized (FALLBACK)")
                app_logger.info(f"   Model: {settings.LLM_MODEL}")
                app_logger.info(f"   Temperature: {settings.LLM_TEMPERATURE}")
                
            except Exception as e:
                app_logger.error(f"❌ Error initializing LLM services: {str(e)}")
                raise
    
    def _build_system_prompt(self) -> str:
        """Build comprehensive system prompt for structured responses"""
        return """You are Regnova, an intelligent AI assistant powered by advanced language models. 

Your responses should be:
- **Well-structured** with clear sections using markdown headers (##, ###)
- **Formatted** with bullet points, numbered lists, and **bold** for emphasis
- **Concise** paragraphs (2-3 sentences maximum per paragraph)
- **Professional** yet approachable in tone
- **Accurate** with proper citations when using provided context

When answering:
1. Use ## for main sections, ### for subsections
2. Use bullet points (•) for non-sequential items
3. Use numbered lists (1., 2., 3.) for sequential steps
4. Use **bold** for key terms and important information
5. Use code blocks (```) for technical content
6. Always cite sources from the context when applicable

Example response format:
## Overview
Brief introduction to the topic.

### Key Points
• **First Point**: Explanation here
• **Second Point**: Details here

### Detailed Analysis
1. First step or concept
2. Second step or concept

**Important**: Always maintain this structure for readability."""
    
    def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        retry_count: int = 3
    ) -> str:
        """
        Generate a response using OpenAI (primary) or Gemini (fallback)
        
        Args:
            prompt: User prompt
            context: Optional context from RAG
            retry_count: Number of retries on failure
        
        Returns:
            Generated response text
        """
        # Try OpenAI first
        if self.use_openai and self.openai_client:
            for attempt in range(retry_count):
                try:
                    return self._generate_openai(prompt, context)
                except Exception as e:
                    app_logger.warning(f"OpenAI attempt {attempt + 1} failed: {str(e)}")
                    if attempt < retry_count - 1:
                        time.sleep(1)
                    else:
                        app_logger.warning("Falling back to Gemini after OpenAI failures")
                        self.use_openai = False
        
        # Fallback to Gemini
        return self._generate_gemini(prompt, context)
    
    def _generate_openai(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate response using OpenAI"""
        messages = [
            {"role": "system", "content": self._build_system_prompt()}
        ]
        
        if context:
            messages.append({
                "role": "system",
                "content": f"Here is relevant context from the user's documents:\n\n{context}\n\nUse this context to answer the user's question accurately."
            })
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS
        )
        
        return response.choices[0].message.content
    
    def _generate_gemini(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate response using Gemini"""
        system_prompt = self._build_system_prompt()
        
        if context:
            full_prompt = f"""{system_prompt}

Context from documents:
{context}

User question: {prompt}

Please provide a detailed, well-formatted answer based on the context above."""
        else:
            full_prompt = f"{system_prompt}\n\nUser question: {prompt}"
        
        response = self.gemini_model.generate_content(
            full_prompt,
            generation_config=self.gemini_config,
            safety_settings=self.safety_settings
        )
        
        return response.text
    
    def generate_response_stream(
        self,
        prompt: str,
        context: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Generate streaming response
        
        Args:
            prompt: User prompt
            context: Optional context from RAG
        
        Yields:
            Response chunks
        """
        if self.use_openai and self.openai_client:
            try:
                yield from self._stream_openai(prompt, context)
                return
            except Exception as e:
                app_logger.warning(f"OpenAI streaming failed: {str(e)}, falling back to Gemini")
        
        # Fallback to Gemini streaming
        yield from self._stream_gemini(prompt, context)
    
    def _stream_openai(self, prompt: str, context: Optional[str] = None) -> Generator[str, None, None]:
        """Stream response using OpenAI"""
        messages = [
            {"role": "system", "content": self._build_system_prompt()}
        ]
        
        if context:
            messages.append({
                "role": "system",
                "content": f"Context from documents:\n\n{context}"
            })
        
        messages.append({"role": "user", "content": prompt})
        
        stream = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def _stream_gemini(self, prompt: str, context: Optional[str] = None) -> Generator[str, None, None]:
        """Stream response using Gemini"""
        system_prompt = self._build_system_prompt()
        
        if context:
            full_prompt = f"""{system_prompt}

Context: {context}

Question: {prompt}"""
        else:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = self.gemini_model.generate_content(
            full_prompt,
            generation_config=self.gemini_config,
            safety_settings=self.safety_settings,
            stream=True
        )
        
        for chunk in response:
            if hasattr(chunk, 'text'):
                yield chunk.text


# Global instance
llm_service = LLMService()
