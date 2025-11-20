"""
Enhanced Chat V2 API with RAG modes, streaming, and safety checks
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import uuid
import traceback
from datetime import datetime

from app.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.models.chat import Chat
from app.schemas.chat_v2 import (
    ChatRequestV2, ChatResponseV2, SourceReferenceV2,
    TraceData, HeatmapData, SafetyCheck
)

# Import chat modules
from app.chat.rag_pipeline import rag_pipeline, RAGMode
from app.chat.answer_generator import answer_generator
from app.chat.citation_engine import citation_engine
from app.chat.streaming import streaming_manager

# Import safety modules
from app.safety.prompt_guard import prompt_guard
from app.safety.hallucination_guard import hallucination_guard

from app.utils.logger import app_logger


router = APIRouter(prefix="/chat/v2", tags=["Chat V2"])


@router.post("/message", response_model=ChatResponseV2)
async def send_message_v2(
    request: ChatRequestV2,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enhanced chat endpoint with RAG modes and safety checks
    
    Features:
    - Dual RAG modes (fast/accurate)
    - Prompt injection protection
    - Hallucination detection
    - Source-grounded citations
    - Full traceability
    """
    try:
        # Validate session_id
        if not request.session_id:
            request.session_id = str(uuid.uuid4())
        
        # Step 1: Safety check - Prompt injection
        if request.check_safety:
            is_safe, prompt_details = prompt_guard.check_prompt(request.message)
            
            if not is_safe:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Prompt blocked: {prompt_details['blocked_reason']}"
                )
            
            # Wrap prompt with safety instructions
            safe_prompt = prompt_guard.add_safety_wrapper(request.message)
        else:
            safe_prompt = request.message
            prompt_details = {"is_safe": True, "risk_level": "none"}
        
        # Store user message
        user_message = Chat(
            user_id=current_user.id,
            session_id=request.session_id,
            role="user",
            content=request.message
        )
        db.add(user_message)
        db.commit()
        
        # Step 2: RAG Retrieval
        if request.use_rag:
            app_logger.info(f"RAG Pipeline: Mode={request.rag_mode}, User={current_user.email}")
            
            # Retrieve relevant chunks
            chunks, trace_data = rag_pipeline.retrieve(
                query=safe_prompt,
                mode=request.rag_mode,
                file_ids=request.file_ids
            )
            
            if not chunks:
                answer_text = "I don't have any relevant information to answer this question. Please upload relevant documents first."
                sources = []
                trace_data_obj = None
                heatmap_data_obj = None
                hall_details = {"is_grounded": True, "confidence": 1.0, "warning_level": "none"}
                gen_metadata = {"model_used": "none", "tokens_used": 0}
            else:
                # Build context
                context = rag_pipeline.build_context(chunks)
                
                # Step 3: Generate answer
                answer_text, gen_metadata = answer_generator.generate_answer(
                    query=request.message,
                    context=context,
                    chunks=chunks,
                    use_citations=request.include_citations
                )
                
                # Step 4: Add/verify citations
                if request.include_citations:
                    answer_text = citation_engine.add_citations(answer_text, chunks, auto_cite=True)
                    citation_report = citation_engine.verify_citations(answer_text, chunks)
                    app_logger.info(f"Citations: {citation_report['total_citations']} total, "
                                  f"{citation_report['valid_citations']} valid")
                
                # Step 5: Hallucination check
                if request.check_safety:
                    is_grounded, hall_details = hallucination_guard.check_answer(
                        answer=answer_text,
                        source_chunks=chunks,
                        query=request.message
                    )
                    
                    if not is_grounded:
                        app_logger.warning(f"Hallucination detected: {hall_details}")
                        answer_text = hallucination_guard.add_disclaimer(answer_text, hall_details)
                else:
                    hall_details = {"is_grounded": True, "confidence": 1.0, "warning_level": "none"}
                
                # Prepare sources
                sources = [
                    SourceReferenceV2(
                        file_id=chunk["file_id"],
                        filename=chunk["filename"],
                        chunk_index=chunk["chunk_index"],
                        page_number=chunk.get("page_number"),
                        relevance_score=chunk["relevance_score"],
                        rerank_score=chunk.get("rerank_score"),
                        content_preview=chunk["content"][:200] + "...",
                        rank=chunk.get("trace", {}).get("rank", 0),
                        original_rank=chunk.get("trace", {}).get("original_rank", 0),
                        reranked=chunk.get("trace", {}).get("reranked", False)
                    )
                    for chunk in chunks
                ]
                
                # Prepare trace data
                trace_data_obj = TraceData(
                    mode=trace_data["mode"],
                    total_time=trace_data["total_time"],
                    retrieval_time=trace_data.get("retrieval_time", 0),
                    rerank_time=trace_data.get("rerank_time"),
                    initial_chunks_count=trace_data.get("initial_chunks_count", 0),
                    final_chunks_count=trace_data.get("final_chunks_count", 0),
                    chunks_removed=trace_data.get("chunks_removed", 0)
                )
                
                # Prepare heatmap data
                heatmap_data_obj = HeatmapData(**rag_pipeline.generate_heatmap_data(chunks, trace_data))
        
        else:
            answer_text = "RAG is disabled. Please enable RAG to get context-based answers."
            sources = []
            trace_data_obj = None
            heatmap_data_obj = None
            hall_details = {"is_grounded": True, "confidence": 1.0, "warning_level": "none"}
            gen_metadata = {"model_used": "none", "tokens_used": 0}
        
        # Store assistant message
        assistant_message = Chat(
            user_id=current_user.id,
            session_id=request.session_id,
            role="assistant",
            content=answer_text,
            sources=[{"file_id": s.file_id, "relevance": s.relevance_score} for s in sources],
            relevance_scores=[s.relevance_score for s in sources]
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)
        
        # Prepare safety check
        safety_check_obj = SafetyCheck(
            prompt_safe=prompt_details["is_safe"],
            answer_grounded=hall_details.get("is_grounded", True),
            prompt_risk_level=prompt_details.get("risk_level", "low"),
            hallucination_warning=hall_details.get("warning_level", "none"),
            confidence=hall_details.get("confidence", 1.0)
        )
        
        # Return response
        return ChatResponseV2(
            message=answer_text,
            sources=sources,
            session_id=request.session_id,
            created_at=assistant_message.created_at,
            trace_data=trace_data_obj,
            heatmap_data=heatmap_data_obj,
            safety_check=safety_check_obj if request.check_safety else None,
            model_used=gen_metadata.get("model_used"),
            tokens_used=gen_metadata.get("tokens_used", 0)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e) if str(e) else type(e).__name__
        app_logger.error(f"Chat V2 error: {error_msg}", exc_info=True)
        app_logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {error_msg}"
        )


@router.post("/message/stream")
async def send_message_stream(
    request: ChatRequestV2,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Streaming chat endpoint with SSE
    
    Returns Server-Sent Events stream with:
    - Sources
    - Answer chunks (streamed)
    - Citations
    - Completion status
    """
    try:
        # Validate session_id
        if not request.session_id:
            request.session_id = str(uuid.uuid4())
        
        # Safety check
        if request.check_safety:
            is_safe, prompt_details = prompt_guard.check_prompt(request.message)
            if not is_safe:
                async def error_stream():
                    yield f"data: {{'type': 'error', 'message': '{prompt_details['blocked_reason']}'}}\n\n"
                
                return StreamingResponse(error_stream(), media_type="text/event-stream")
        
        # Store user message
        user_message = Chat(
            user_id=current_user.id,
            session_id=request.session_id,
            role="user",
            content=request.message
        )
        db.add(user_message)
        db.commit()
        
        # Retrieve chunks
        if request.use_rag:
            chunks, trace_data = rag_pipeline.retrieve(
                query=request.message,
                mode=request.rag_mode,
                file_ids=request.file_ids
            )
            
            context = rag_pipeline.build_context(chunks)
            
            # Generate streaming answer
            answer_gen = answer_generator.generate_streaming_answer(
                query=request.message,
                context=context,
                chunks=chunks,
                use_citations=request.include_citations
            )
            
            # Stream with sources
            return StreamingResponse(
                streaming_manager.stream_with_sources(
                    answer_generator=answer_gen,
                    chunks=chunks,
                    include_citations=request.include_citations
                ),
                media_type="text/event-stream"
            )
        
        else:
            async def no_rag_stream():
                yield f"data: {{'type': 'content', 'content': 'RAG is disabled'}}\n\n"
                yield f"data: {{'type': 'done'}}\n\n"
            
            return StreamingResponse(no_rag_stream(), media_type="text/event-stream")
    
    except Exception as e:
        app_logger.error(f"Streaming error: {str(e)}")
        
        async def error_stream():
            yield f"data: {{'type': 'error', 'message': '{str(e)}'}}\n\n"
        
        return StreamingResponse(error_stream(), media_type="text/event-stream")


@router.get("/heatmap/{session_id}")
async def get_session_heatmap(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get traceability heatmap data for a chat session
    Useful for visualizing RAG pipeline performance
    """
    # Get last message from session
    last_message = db.query(Chat).filter(
        Chat.session_id == session_id,
        Chat.user_id == current_user.id,
        Chat.role == "assistant"
    ).order_by(Chat.created_at.desc()).first()
    
    if not last_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Return heatmap data (stored in sources field as metadata)
    return {
        "session_id": session_id,
        "sources": last_message.sources,
        "relevance_scores": last_message.relevance_scores,
        "created_at": last_message.created_at
    }
