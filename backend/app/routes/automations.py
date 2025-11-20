"""
Automation routes for Gmail, WhatsApp, and Push Notifications
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.schemas.automation import (
    EmailRequest, EmailRAGRequest,
    WhatsAppRequest, WhatsAppRAGRequest,
    PushNotificationRequest, NotificationResponse,
    BulkNotificationRequest, BulkNotificationResponse
)

from app.automations.gmail_service import gmail_service
from app.automations.whatsapp_service import whatsapp_service
from app.automations.push_notification import push_notification_service

from app.utils.logger import app_logger


router = APIRouter(prefix="/automations", tags=["Automations"])


# ============= EMAIL ROUTES =============

@router.post("/email/send", response_model=NotificationResponse)
async def send_email(
    request: EmailRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Send email via Gmail SMTP
    
    Requires:
    - GMAIL_EMAIL
    - GMAIL_APP_PASSWORD (App-specific password from Google)
    """
    try:
        result = gmail_service.send_email(
            to_email=request.to_email,
            subject=request.subject,
            body=request.body,
            body_html=request.body_html
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to send email")
            )
        
        return NotificationResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Email error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/email/send-rag-answer", response_model=NotificationResponse)
async def send_rag_answer_email(
    request: EmailRAGRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Send RAG-generated answer via email
    Includes formatted answer with sources
    """
    try:
        result = gmail_service.send_rag_answer(
            to_email=request.to_email,
            question=request.question,
            answer=request.answer,
            sources=request.sources,
            user_name=request.user_name or current_user.name
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to send email")
            )
        
        return NotificationResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"RAG email error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============= WHATSAPP ROUTES =============

@router.post("/whatsapp/send", response_model=NotificationResponse)
async def send_whatsapp(
    request: WhatsAppRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Send WhatsApp message via ***REMOVED***
    
    Requires:
    - ***REMOVED***_ACCOUNT_SID
    - ***REMOVED***_***REMOVED***
    - ***REMOVED***_WHATSAPP_NUMBER (default: ***REMOVED*** sandbox)
    
    Number format: whatsapp:+1234567890 or +1234567890
    """
    try:
        result = whatsapp_service.send_message(
            to_number=request.to_number,
            message=request.message,
            media_url=request.media_url
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to send WhatsApp message")
            )
        
        return NotificationResponse(
            success=result["success"],
            message=f"Message sent to {result['to']}",
            notification_id=result.get("message_sid")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"WhatsApp error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/whatsapp/send-rag-answer", response_model=NotificationResponse)
async def send_rag_answer_whatsapp(
    request: WhatsAppRAGRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Send RAG answer via WhatsApp
    Formatted for mobile viewing
    """
    try:
        result = whatsapp_service.send_rag_answer(
            to_number=request.to_number,
            question=request.question,
            answer=request.answer,
            sources=request.sources
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to send WhatsApp message")
            )
        
        return NotificationResponse(
            success=result["success"],
            message=f"RAG answer sent to {result['to']}",
            notification_id=result.get("message_sid")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"WhatsApp RAG error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/whatsapp/status/{message_sid}")
async def get_whatsapp_status(
    message_sid: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get status of sent WhatsApp message
    """
    try:
        result = whatsapp_service.get_message_status(message_sid)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Message not found")
            )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"WhatsApp status error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============= PUSH NOTIFICATION ROUTES =============

@router.post("/push/send", response_model=NotificationResponse)
async def send_push_notification(
    request: PushNotificationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Send push notification via OneSignal
    
    Requires:
    - ONESIGNAL_APP_ID
    - ONESIGNAL_API_KEY
    
    user_ids: List of OneSignal player IDs or external user IDs
    """
    try:
        result = push_notification_service.send_notification(
            user_ids=request.user_ids,
            title=request.title,
            message=request.message,
            data=request.data,
            url=request.url
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to send push notification")
            )
        
        return NotificationResponse(
            success=result["success"],
            message=f"Notification sent to {result.get('recipients', 0)} users",
            notification_id=result.get("notification_id")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Push notification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/push/send-all", response_model=NotificationResponse)
async def send_push_to_all(
    title: str,
    message: str,
    data: dict = None,
    url: str = None,
    current_user: User = Depends(get_current_user)
):
    """
    Send push notification to all subscribed users
    Use with caution - sends to entire user base
    """
    try:
        result = push_notification_service.send_to_all(
            title=title,
            message=message,
            data=data,
            url=url
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to send push notification")
            )
        
        return NotificationResponse(
            success=result["success"],
            message=f"Notification sent to {result.get('recipients', 0)} users",
            notification_id=result.get("notification_id")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Push to all error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/push/status/{notification_id}")
async def get_push_status(
    notification_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get status of sent push notification
    """
    try:
        result = push_notification_service.get_notification_status(notification_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Notification not found")
            )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Push status error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============= BULK OPERATIONS =============

@router.post("/bulk/send", response_model=BulkNotificationResponse)
async def send_bulk_notifications(
    request: BulkNotificationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Send bulk notifications via multiple channels
    
    Supported types: email, whatsapp, push
    """
    try:
        if request.notification_type == "whatsapp":
            result = whatsapp_service.send_bulk_messages(
                recipients=request.recipients,
                message=request.message
            )
        elif request.notification_type == "email":
            results = {
                "total": len(request.recipients),
                "sent": 0,
                "failed": 0,
                "details": []
            }
            
            for email in request.recipients:
                email_result = gmail_service.send_email(
                    to_email=email,
                    subject=request.title or "Notification",
                    body=request.message
                )
                
                if email_result["success"]:
                    results["sent"] += 1
                else:
                    results["failed"] += 1
                
                results["details"].append({
                    "recipient": email,
                    "success": email_result["success"],
                    "error": email_result.get("error")
                })
            
            results["success"] = results["sent"] > 0
            result = results
        
        elif request.notification_type == "push":
            push_result = push_notification_service.send_notification(
                user_ids=request.recipients,
                title=request.title or "Notification",
                message=request.message,
                data=request.data
            )
            
            result = {
                "success": push_result["success"],
                "total": len(request.recipients),
                "sent": push_result.get("recipients", 0),
                "failed": len(request.recipients) - push_result.get("recipients", 0),
                "details": [{"success": push_result["success"]}]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid notification type: {request.notification_type}"
            )
        
        return BulkNotificationResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Bulk notification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
