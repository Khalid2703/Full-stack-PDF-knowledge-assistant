"""
Hallucination detection and prevention
Verifies that generated answers are grounded in source documents
"""

from typing import List, Dict, Tuple
import re
from app.utils.logger import app_logger


class HallucinationGuard:
    """
    Detect and prevent hallucinated information in answers
    """
    
    def __init__(self):
        """Initialize hallucination guard"""
        self.confidence_threshold = 0.5
        self.min_source_coverage = 0.3
    
    def check_answer(
        self,
        answer: str,
        source_chunks: List[Dict],
        query: str
    ) -> Tuple[bool, Dict]:
        """
        Check if answer is grounded in source chunks
        
        Args:
            answer: Generated answer
            source_chunks: Source chunks used for generation
            query: Original query
        
        Returns:
            Tuple of (is_grounded, details)
        """
        details = {
            "is_grounded": True,
            "confidence": 0.0,
            "source_coverage": 0.0,
            "unsupported_claims": [],
            "supported_claims": [],
            "warning_level": "none"  # none, low, medium, high
        }
        
        if not answer or not source_chunks:
            details["is_grounded"] = False
            details["warning_level"] = "high"
            return False, details
        
        # Extract claims from answer
        claims = self._extract_claims(answer)
        
        # Check each claim against sources
        supported_count = 0
        unsupported_claims = []
        
        for claim in claims:
            is_supported, support_score = self._check_claim_support(
                claim, source_chunks
            )
            
            if is_supported:
                supported_count += 1
                details["supported_claims"].append({
                    "claim": claim,
                    "support_score": support_score
                })
            else:
                unsupported_claims.append({
                    "claim": claim,
                    "support_score": support_score
                })
        
        # Calculate metrics
        total_claims = len(claims)
        if total_claims > 0:
            details["source_coverage"] = supported_count / total_claims
        else:
            details["source_coverage"] = 1.0  # No claims to verify
        
        details["unsupported_claims"] = unsupported_claims
        
        # Calculate confidence
        details["confidence"] = self._calculate_confidence(
            answer, source_chunks, details["source_coverage"]
        )
        
        # Determine if answer is grounded
        is_grounded = (
            details["source_coverage"] >= self.min_source_coverage and
            details["confidence"] >= self.confidence_threshold
        )
        
        details["is_grounded"] = is_grounded
        
        # Set warning level
        if not is_grounded:
            if details["confidence"] < 0.3:
                details["warning_level"] = "high"
            elif details["source_coverage"] < 0.3:
                details["warning_level"] = "high"
            elif details["confidence"] < 0.5:
                details["warning_level"] = "medium"
            else:
                details["warning_level"] = "low"
        
        # Log warnings
        if not is_grounded:
            app_logger.warning(
                f"Hallucination detected. Coverage: {details['source_coverage']:.2f}, "
                f"Confidence: {details['confidence']:.2f}, "
                f"Unsupported claims: {len(unsupported_claims)}"
            )
        
        return is_grounded, details
    
    def _extract_claims(self, answer: str) -> List[str]:
        """
        Extract factual claims from answer
        
        Args:
            answer: Generated answer
        
        Returns:
            List of claims
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', answer)
        
        # Filter out very short sentences and questions
        claims = [
            s.strip()
            for s in sentences
            if len(s.strip()) > 20 and '?' not in s
        ]
        
        return claims
    
    def _check_claim_support(
        self,
        claim: str,
        source_chunks: List[Dict]
    ) -> Tuple[bool, float]:
        """
        Check if claim is supported by source chunks
        
        Args:
            claim: Factual claim to verify
            source_chunks: Source documents
        
        Returns:
            Tuple of (is_supported, support_score)
        """
        claim_words = set(claim.lower().split())
        
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
            'to', 'for', 'of', 'is', 'are', 'was', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did'
        }
        claim_words = claim_words - stop_words
        
        if not claim_words:
            return True, 1.0  # No content words to verify
        
        # Check overlap with each source
        max_overlap = 0.0
        
        for chunk in source_chunks:
            chunk_words = set(chunk['content'].lower().split())
            overlap = len(claim_words & chunk_words)
            overlap_ratio = overlap / len(claim_words)
            
            if overlap_ratio > max_overlap:
                max_overlap = overlap_ratio
        
        # Claim is supported if >30% of content words found in sources
        is_supported = max_overlap >= 0.3
        
        return is_supported, max_overlap
    
    def _calculate_confidence(
        self,
        answer: str,
        source_chunks: List[Dict],
        source_coverage: float
    ) -> float:
        """
        Calculate overall confidence score
        
        Args:
            answer: Generated answer
            source_chunks: Source chunks
            source_coverage: Coverage of claims by sources
        
        Returns:
            Confidence score (0 to 1)
        """
        # Factor 1: Source coverage (weight: 0.4)
        coverage_score = source_coverage * 0.4
        
        # Factor 2: Answer length vs context length (weight: 0.2)
        answer_words = len(answer.split())
        context_words = sum(len(chunk['content'].split()) for chunk in source_chunks)
        
        if context_words > 0:
            length_ratio = min(answer_words / context_words, 1.0)
            length_score = (1.0 - abs(0.3 - length_ratio)) * 0.2
        else:
            length_score = 0.0
        
        # Factor 3: Presence of citations (weight: 0.2)
        citation_pattern = r'\[Source \d+\]'
        citations = re.findall(citation_pattern, answer)
        citation_score = min(len(citations) / 3, 1.0) * 0.2
        
        # Factor 4: Specificity indicators (weight: 0.2)
        # Presence of numbers, dates, names indicates specificity
        specificity_indicators = len(re.findall(r'\d+', answer))
        specificity_score = min(specificity_indicators / 5, 1.0) * 0.2
        
        # Total confidence
        confidence = (
            coverage_score +
            length_score +
            citation_score +
            specificity_score
        )
        
        return min(confidence, 1.0)
    
    def add_disclaimer(self, answer: str, details: Dict) -> str:
        """
        Add disclaimer to answer if confidence is low
        
        Args:
            answer: Generated answer
            details: Check details
        
        Returns:
            Answer with disclaimer if needed
        """
        if details["warning_level"] == "high":
            disclaimer = "\n\n⚠️ **Note**: This answer may not be fully supported by the provided sources. Please verify critical information."
            return answer + disclaimer
        
        elif details["warning_level"] == "medium":
            disclaimer = "\n\n**Note**: Some parts of this answer may go beyond the provided sources."
            return answer + disclaimer
        
        return answer
    
    def get_unsupported_segments(
        self,
        answer: str,
        source_chunks: List[Dict]
    ) -> List[str]:
        """
        Identify specific segments of answer that lack source support
        
        Args:
            answer: Generated answer
            source_chunks: Source chunks
        
        Returns:
            List of unsupported text segments
        """
        unsupported = []
        
        sentences = re.split(r'[.!?]+', answer)
        
        for sentence in sentences:
            if len(sentence.strip()) < 20:
                continue
            
            is_supported, score = self._check_claim_support(sentence, source_chunks)
            
            if not is_supported:
                unsupported.append(sentence.strip())
        
        return unsupported


# Global instance
hallucination_guard = HallucinationGuard()
