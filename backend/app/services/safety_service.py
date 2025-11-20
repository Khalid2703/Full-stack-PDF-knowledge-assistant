"""
Safety service for prompt injection protection and hallucination detection
"""

import re
from typing import Dict, List, Tuple
from app.utils.logger import app_logger
from app.config import settings


class SafetyService:
    """Service for AI safety checks"""
    
    def __init__(self):
        """Initialize safety patterns"""
        # Prompt injection patterns
        self.injection_patterns = [
            r"ignore\s+(previous|above|all)\s+instructions",
            r"disregard\s+(previous|all)\s+(instructions|prompts)",
            r"forget\s+(everything|all|previous)",
            r"new\s+instructions?:",
            r"system\s*:\s*",
            r"admin\s+mode",
            r"developer\s+mode",
            r"you\s+are\s+now",
            r"act\s+as\s+if",
            r"pretend\s+(you|to)\s+are",
            r"\[SYSTEM\]",
            r"\[INST\]",
            r"<\|im_start\|>",
        ]
        
        self.injection_regex = re.compile(
            "|".join(self.injection_patterns),
            re.IGNORECASE
        )
        
        # Suspicious phrases for hallucination detection
        self.uncertain_phrases = [
            "i'm not sure",
            "i don't know",
            "i cannot find",
            "no information",
            "not mentioned",
            "unclear",
            "ambiguous",
        ]
        
        app_logger.info("✅ Safety service initialized")
    
    def check_prompt_injection(self, text: str) -> Tuple[bool, str]:
        """
        Check if text contains prompt injection attempts
        
        Args:
            text: Input text to check
        
        Returns:
            Tuple of (is_safe, reason)
        """
        if not settings.ENABLE_PROMPT_INJECTION_GUARD:
            return True, ""
        
        try:
            # Check for injection patterns
            match = self.injection_regex.search(text)
            if match:
                reason = f"Potential prompt injection detected: '{match.group()}'"
                app_logger.warning(f"🚨 {reason}")
                return False, reason
            
            # Check for excessive special characters
            special_char_ratio = len(re.findall(r'[^\w\s]', text)) / max(len(text), 1)
            if special_char_ratio > 0.3:
                reason = "Excessive special characters detected"
                app_logger.warning(f"🚨 {reason}")
                return False, reason
            
            # Check for repeating patterns (injection attempts)
            words = text.lower().split()
            if len(words) > 5:
                unique_ratio = len(set(words)) / len(words)
                if unique_ratio < 0.3:
                    reason = "Suspicious repeating patterns detected"
                    app_logger.warning(f"🚨 {reason}")
                    return False, reason
            
            return True, ""
            
        except Exception as e:
            app_logger.error(f"❌ Error in prompt injection check: {str(e)}")
            return True, ""  # Fail open for safety
    
    def sanitize_prompt(self, text: str) -> str:
        """
        Sanitize potentially unsafe prompts
        
        Args:
            text: Input text
        
        Returns:
            Sanitized text
        """
        # Remove potential injection markers
        text = re.sub(r'\[SYSTEM\]|\[INST\]|<\|im_start\|>', '', text, flags=re.IGNORECASE)
        
        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Trim whitespace
        text = text.strip()
        
        return text
    
    def check_hallucination(
        self,
        answer: str,
        sources: List[Dict],
        threshold: float = 0.3
    ) -> Tuple[bool, float, str]:
        """
        Check if answer might be hallucinated (not grounded in sources)
        
        Args:
            answer: Generated answer
            sources: Source documents used
            threshold: Confidence threshold (lower = stricter)
        
        Returns:
            Tuple of (is_grounded, confidence, explanation)
        """
        if not settings.ENABLE_HALLUCINATION_GUARD:
            return True, 1.0, ""
        
        try:
            # If no sources provided, flag as potential hallucination
            if not sources:
                return False, 0.0, "No sources provided for answer"
            
            # Check for uncertainty phrases
            answer_lower = answer.lower()
            uncertain_count = sum(
                1 for phrase in self.uncertain_phrases
                if phrase in answer_lower
            )
            
            if uncertain_count > 0:
                confidence = 0.5
                explanation = "Answer contains uncertainty phrases"
            else:
                confidence = 0.8
                explanation = "Answer appears confident"
            
            # Check source overlap (simplified heuristic)
            answer_words = set(answer.lower().split())
            source_words = set()
            for source in sources[:3]:  # Check top 3 sources
                content = source.get('content', '')
                source_words.update(content.lower().split())
            
            if source_words:
                overlap_ratio = len(answer_words & source_words) / len(answer_words)
                confidence = (confidence + overlap_ratio) / 2
                
                if overlap_ratio < 0.1:
                    explanation = f"Low overlap with sources ({overlap_ratio:.1%})"
            
            # Determine if grounded
            is_grounded = confidence >= threshold
            
            if not is_grounded:
                app_logger.warning(f"🚨 Potential hallucination detected: {explanation} (confidence: {confidence:.2f})")
            
            return is_grounded, confidence, explanation
            
        except Exception as e:
            app_logger.error(f"❌ Error in hallucination check: {str(e)}")
            return True, 0.5, ""  # Fail open with low confidence
    
    def validate_sources(self, sources: List[Dict]) -> Tuple[bool, str]:
        """
        Validate that sources are legitimate and relevant
        
        Args:
            sources: List of source documents
        
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            if not sources:
                return False, "No sources provided"
            
            # Check if sources have required fields
            for source in sources:
                if 'content' not in source or 'file_id' not in source:
                    return False, "Sources missing required fields"
                
                # Check content length
                if len(source.get('content', '')) < 10:
                    return False, "Source content too short"
            
            return True, "Sources validated"
            
        except Exception as e:
            app_logger.error(f"❌ Error validating sources: {str(e)}")
            return False, "Error during validation"
    
    def create_safe_context(self, sources: List[Dict], max_length: int = 4000) -> str:
        """
        Create a safe context string from sources
        
        Args:
            sources: List of source documents
            max_length: Maximum context length
        
        Returns:
            Safe context string
        """
        try:
            context_parts = []
            current_length = 0
            
            for i, source in enumerate(sources, 1):
                content = source.get('content', '')
                filename = source.get('filename', 'Unknown')
                page = source.get('page_number', 'N/A')
                
                # Sanitize content
                content = self.sanitize_prompt(content)
                
                # Create citation
                citation = f"\n[Source {i}: {filename}, Page {page}]\n{content}\n"
                
                # Check length
                if current_length + len(citation) > max_length:
                    break
                
                context_parts.append(citation)
                current_length += len(citation)
            
            return "\n".join(context_parts)
            
        except Exception as e:
            app_logger.error(f"❌ Error creating safe context: {str(e)}")
            return ""


# Global instance
safety_service = SafetyService()
