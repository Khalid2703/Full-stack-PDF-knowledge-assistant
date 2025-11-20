"""
Enhanced chat schemas for V2 API with RAG modes and streaming
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class RAGMode(str, Enum):
    """RAG execution modes"""
    FAST = "fast"
    ACCURATE = "accurate"


class ChatRequestV2(BaseModel):
    """Enhanced chat request with RAG modes"""
    session_id: str
    message: str
    file_ids: Optional[List[int]] = None
    use_rag: bool = Field(default=True)
    rag_mode: RAGMode = Field(default=RAGMode.FAST)
    stream: bool = Field(default=False)
    include_citations: bool = Field(default=True)
    check_safety: bool = Field(default=True)


class SourceReferenceV2(BaseModel):
    """Enhanced source reference with traceability"""
    file_id: int
    filename: str
    chunk_index: int
    page_number: Optional[int]
    relevance_score: float
    rerank_score: Optional[float] = None
    content_preview: str
    rank: int
    original_rank: int
    reranked: bool


class TraceData(BaseModel):
    """Traceability data for RAG pipeline"""
    mode: str
    total_time: float
    retrieval_time: float
    rerank_time: Optional[float] = None
    initial_chunks_count: int
    final_chunks_count: int
    chunks_removed: int


class HeatmapData(BaseModel):
    """Heatmap visualization data"""
    mode: str
    total_time: float
    retrieval_stages: List[Dict]
    chunks: List[Dict]


class SafetyCheck(BaseModel):
    """Safety check results"""
    prompt_safe: bool
    answer_grounded: bool
    prompt_risk_level: str
    hallucination_warning: str
    confidence: float


class ChatResponseV2(BaseModel):
    """Enhanced chat response with full metadata"""
    message: str
    sources: List[SourceReferenceV2]
    session_id: str
    created_at: datetime
    trace_data: Optional[TraceData] = None
    heatmap_data: Optional[HeatmapData] = None
    safety_check: Optional[SafetyCheck] = None
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None


class StreamEvent(BaseModel):
    """SSE stream event"""
    type: str  # start, content, sources, citations, done, error
    content: Optional[str] = None
    data: Optional[Dict] = None
    message: Optional[str] = None
