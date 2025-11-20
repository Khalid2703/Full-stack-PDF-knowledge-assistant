"""
Enhanced chat routes with SSE streaming, RAG modes, and safety features
DAY 2: Advanced Chat System
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional, AsyncGenerator
import json
import uuid
from datetime import datetime

from app.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.models.chat import Chat
from app.models.file import File as FileModel
from app.schemas.chat import ChatRequest, ChatResponse, ChatHistory, SourceReference
from app.services.rag_service import rag_service
from app.services.llm_service import llm_service
from app.services.reranking_service import reranking_service
from app.services.safety_service import safety_service
from app.services.gmail_service import gmail_service
from app.services.whatsapp_service import whatsapp_service
from app.services.push_service import push_service
from app.utils.logger import app_logger
from app.config import settings


router = APIRouter(prefix="/chat", tags=["Chat"])


async def generate_sse_response(
    query: str,
    context: str,
    session_id: str,
    user_id: int,
    sources: List[dict],
    db: Session
) -> AsyncGenerator[str, None]:
    """
    Generate Server-Sent Events stream for chat response
    
    Args:
        query: User query
        context: RAG context
        session_id: Chat session ID
        user_id: User ID
        sources: Retrieved sources
        db: Database session
    
    Yields:
        SSE formatted messages
    """
    try:
        # Send sources first
        yield f"data: {json.dumps({'type': 'sources', 'data': sources})}\n\n"
        
        # Stream response chunks
        full_response = ""
        for chunk in llm_service.generate_response_stream(query, context):
            full_response += chunk
            yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
        
        # Check for hallucination
        is_grounded, confidence, explanation = safety_service.check_hallucination(
            answer=full_response,
            sources=sources
        )
        
        # Send completion metadata
        metadata = {
            'type': 'complete',
            'is_grounded': is_grounded,
            'confidence': confidence,
            'explanation': explanation
        }
        yield f"data: {json.dumps(metadata)}\n\n"
        
        # Store complete response in database
        assistant_message = Chat(
            user_id=user_id,
            session_id=session_id,
            role="assistant",
            content=full_response,
            sources=[{"file_id": s["file_id"], "relevance": s["relevance_score"]} for s in sources],
            relevance_scores=[s["relevance_score"] for s in sources]
        )
        db.add(assistant_message)
        db.commit()
        
    except Exception as e:
        app_logger.error(f"❌ Streaming error: {str(e)}")
        error_msg = {"type": "error", "message": "An error occurred while generating the response"}
        yield f"data: {json.dumps(error_msg)}\n\n"


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a chat message with RAG-powered response (non-streaming)
    
    - Retrieves relevant chunks from vector store
    - Optionally reranks results
    - Checks for prompt injection
    - Generates contextual response
    - Validates answer groundedness
    - Stores conversation history
    """
    try:
        # Validate session_id
        if not request.session_id:
            request.session_id = str(uuid.uuid4())
        
        # Safety check: Prompt injection
        is_safe, reason = safety_service.check_prompt_injection(request.message)
        if not is_safe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsafe input detected: {reason}"
            )
        
        # Sanitize prompt
        safe_message = safety_service.sanitize_prompt(request.message)
        
        # Store user message
        user_message = Chat(
            user_id=current_user.id,
            session_id=request.session_id,
            role="user",
            content=safe_message
        )
        db.add(user_message)
        db.commit()
        
        # Retrieve relevant chunks if RAG enabled
        sources = []
        context = ""
        
        if request.use_rag:
            app_logger.info(f"🔍 RAG Mode: {settings.RAG_MODE}")
            
            # Determine top_k based on mode
            top_k = settings.RAG_TOP_K if settings.RAG_MODE == "accurate" else 3
            
            # Search vector store
            relevant_chunks = rag_service.search(
                query=safe_message,
                top_k=top_k * 2 if settings.RAG_RERANK else top_k,  # Get more for reranking
                file_ids=request.file_ids
            )
            
            # Rerank if enabled (accurate mode)
            if settings.RAG_RERANK and settings.RAG_MODE == "accurate":
                app_logger.info("🔄 Reranking results...")
                relevant_chunks = reranking_service.rerank(
                    query=safe_message,
                    documents=relevant_chunks,
                    top_k=top_k
                )
            
            # Build safe context
            context = safety_service.create_safe_context(relevant_chunks)
            
            # Prepare sources for response
            for chunk in relevant_chunks:
                sources.append(SourceReference(
                    file_id=chunk['file_id'],
                    filename=chunk['filename'],
                    chunk_index=chunk['chunk_index'],
                    page_number=chunk.get('page_number'),
                    relevance_score=chunk.get('final_score', chunk['relevance_score']),
                    content_preview=chunk['content'][:200] + "..."
                ))
        
        # Generate response
        assistant_message_content = llm_service.generate_response(
            prompt=safe_message,
            context=context if context else None
        )
        
        # Check for hallucination
        if context:
            is_grounded, confidence, explanation = safety_service.check_hallucination(
                answer=assistant_message_content,
                sources=[{"content": s.content_preview} for s in sources]
            )
            
            if not is_grounded:
                app_logger.warning(f"⚠️ Low groundedness: {explanation}")
                # Optionally add disclaimer
                assistant_message_content += f"\n\n_Note: This answer may not be fully supported by the provided sources. Confidence: {confidence:.1%}_"
        
        # Store assistant message
        assistant_message = Chat(
            user_id=current_user.id,
            session_id=request.session_id,
            role="assistant",
            content=assistant_message_content,
            sources=[{"file_id": s.file_id, "relevance": s.relevance_score} for s in sources],
            relevance_scores=[s.relevance_score for s in sources]
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)
        
        # Optional: Send notification (async in production)
        if current_user.email:
            try:
                push_service.notify_chat_response(
                    user_id=str(current_user.id),
                    session_id=request.session_id,
                    preview=assistant_message_content[:100]
                )
            except:
                pass  # Don't fail if notification fails
        
        return ChatResponse(
            message=assistant_message_content,
            sources=sources,
            session_id=request.session_id,
            created_at=assistant_message.created_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"❌ Chat error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


@router.post("/message/stream")
async def send_message_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a chat message with SSE streaming response
    
    Returns:
        StreamingResponse with Server-Sent Events
    """
    try:
        # Validate session_id
        if not request.session_id:
            request.session_id = str(uuid.uuid4())
        
        # Safety check
        is_safe, reason = safety_service.check_prompt_injection(request.message)
        if not is_safe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsafe input detected: {reason}"
            )
        
        safe_message = safety_service.sanitize_prompt(request.message)
        
        # Store user message
        user_message = Chat(
            user_id=current_user.id,
            session_id=request.session_id,
            role="user",
            content=safe_message
        )
        db.add(user_message)
        db.commit()
        
        # Retrieve sources
        sources = []
        context = ""
        
        if request.use_rag:
            top_k = settings.RAG_TOP_K if settings.RAG_MODE == "accurate" else 3
            relevant_chunks = rag_service.search(
                query=safe_message,
                top_k=top_k * 2 if settings.RAG_RERANK else top_k,
                file_ids=request.file_ids
            )
            
            if settings.RAG_RERANK and settings.RAG_MODE == "accurate":
                relevant_chunks = reranking_service.rerank(
                    query=safe_message,
                    documents=relevant_chunks,
                    top_k=top_k
                )
            
            context = safety_service.create_safe_context(relevant_chunks)
            
            sources = [
                {
                    "file_id": chunk['file_id'],
                    "filename": chunk['filename'],
                    "chunk_index": chunk['chunk_index'],
                    "page_number": chunk.get('page_number'),
                    "relevance_score": chunk.get('final_score', chunk['relevance_score']),
                    "content_preview": chunk['content'][:200] + "..."
                }
                for chunk in relevant_chunks
            ]
        
        # Return streaming response
        return StreamingResponse(
            generate_sse_response(
                query=safe_message,
                context=context,
                session_id=request.session_id,
                user_id=current_user.id,
                sources=sources,
                db=db
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"❌ Streaming setup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize streaming response"
        )


@router.get("/history/{session_id}", response_model=ChatHistory)
async def get_chat_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history for a specific session"""
    messages = db.query(Chat).filter(
        Chat.session_id == session_id,
        Chat.user_id == current_user.id
    ).order_by(Chat.created_at).all()
    
    if not messages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    from app.schemas.chat import ChatMessage
    return ChatHistory(
        session_id=session_id,
        messages=[ChatMessage(role=msg.role, content=msg.content) for msg in messages],
        created_at=messages[0].created_at
    )


@router.get("/sessions")
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all chat sessions for current user"""
    sessions = db.query(Chat.session_id, Chat.created_at).filter(
        Chat.user_id == current_user.id
    ).group_by(Chat.session_id, Chat.created_at).order_by(Chat.created_at.desc()).all()
    
    session_list = []
    for session_id, created_at in sessions:
        first_msg = db.query(Chat).filter(
            Chat.session_id == session_id,
            Chat.role == "user"
        ).order_by(Chat.created_at).first()
        
        session_list.append({
            "session_id": session_id,
            "created_at": created_at,
            "preview": first_msg.content[:100] if first_msg else ""
        })
    
    return {"sessions": session_list}


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a chat session and all its messages"""
    db.query(Chat).filter(
        Chat.session_id == session_id,
        Chat.user_id == current_user.id
    ).delete()
    
    db.commit()
    app_logger.info(f"Deleted chat session: {session_id}")
    return {"message": "Session deleted successfully"}


@router.post("/export/{session_id}")
async def export_chat(
    session_id: str,
    format: str = Query("json", regex="^(json|pdf|email)$"),
    email: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export chat history in various formats
    
    Args:
        session_id: Chat session ID
        format: Export format (json, pdf, email)
        email: Optional email address for sending export
    
    Returns:
        Exported data or confirmation
    """
    messages = db.query(Chat).filter(
        Chat.session_id == session_id,
        Chat.user_id == current_user.id
    ).order_by(Chat.created_at).all()
    
    if not messages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    if format == "json":
        # Return JSON export
        export_data = {
            "session_id": session_id,
            "user": current_user.name,
            "exported_at": datetime.utcnow().isoformat(),
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        }
        return export_data
    
    elif format == "email" and email:
        # Send via email
        chat_content = "\n\n".join([
            f"{msg.role.upper()}: {msg.content}"
            for msg in messages
        ])
        
        success = gmail_service.send_email(
            to_email=email,
            subject=f"Regnova Chat Export - {session_id[:8]}",
            body=f"Chat Session Export\n\n{chat_content}"
        )
        
        if success:
            return {"message": f"Chat exported and sent to {email}"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send email"
            )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid export format or missing email"
        )


@router.get("/traceability/{session_id}")
async def get_traceability_data(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get traceability heatmap data for a chat session
    Shows source document usage and relevance scores
    """
    messages = db.query(Chat).filter(
        Chat.session_id == session_id,
        Chat.user_id == current_user.id,
        Chat.role == "assistant"
    ).all()
    
    if not messages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No assistant messages found"
        )
    
    # Aggregate source usage
    source_usage = {}
    for msg in messages:
        if msg.sources:
            for source in msg.sources:
                file_id = source.get('file_id')
                if file_id:
                    if file_id not in source_usage:
                        source_usage[file_id] = {
                            'count': 0,
                            'total_relevance': 0.0,
                            'messages': []
                        }
                    source_usage[file_id]['count'] += 1
                    source_usage[file_id]['total_relevance'] += source.get('relevance', 0.0)
                    source_usage[file_id]['messages'].append(msg.id)
    
    # Get file details
    heatmap_data = []
    for file_id, usage in source_usage.items():
        file = db.query(FileModel).filter(FileModel.id == file_id).first()
        if file:
            heatmap_data.append({
                'file_id': file_id,
                'filename': file.original_filename,
                'usage_count': usage['count'],
                'avg_relevance': usage['total_relevance'] / usage['count'],
                'message_ids': usage['messages']
            })
    
    # Sort by usage
    heatmap_data.sort(key=lambda x: x['usage_count'], reverse=True)
    
    return {
        "session_id": session_id,
        "total_messages": len(messages),
        "sources_used": len(heatmap_data),
        "heatmap": heatmap_data
    }
