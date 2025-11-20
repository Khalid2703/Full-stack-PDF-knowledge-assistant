"""
Automation routes for Gmail, WhatsApp, and Push Notifications
DAY 2: Automation Features
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, EmailStr

from app.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.services.gmail_service import gmail_service
from app.services.whatsapp_service import whatsapp_service
from app.services.push_service import push_service
from app.utils.logger import app_logger


router = APIRouter(prefix="/automation", tags=["Automation"])


# Schemas
class EmailRequest(BaseModel):
    to_email: EmailStr
    subject: str
    body: str
    html_body: Optional[str] = None


class WhatsAppRequest(BaseModel):
    message: str
    to_number: Optional[str] = None


class PushNotificationRequest(BaseModel):
    title: str
    body: str
    user_ids: Optional[List[str]] = None
    segments: Optional[List[str]] = None


# Gmail Routes
@router.post("/email/send")
async def send_email(
    email_request: EmailRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Send an email via Gmail
    
    - Sends in background to avoid blocking
    - Supports plain text and HTML
    """
    try:
        def send_email_task():
            success = gmail_service.send_email(
                to_email=email_request.to_email,
                subject=email_request.subject,
                body=email_request.body,
                html_body=email_request.html_body
            )
            if success:
                app_logger.info(f"✅ Email sent to {email_request.to_email}")
            else:
                app_logger.error(f"❌ Failed to send email to {email_request.to_email}")
        
        background_tasks.add_task(send_email_task)
        
        return {
            "message": "Email queued for sending",
            "to": email_request.to_email
        }
    
    except Exception as e:
        app_logger.error(f"❌ Email error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue email"
        )


@router.post("/email/send-report")
async def send_report_email(
    to_email: EmailStr,
    session_id: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a formatted report via email
    
    - Generates report from user's data
    - Sends with professional formatting
    """
    try:
        from app.models.file import File as FileModel
        from app.models.chunk import Chunk
        from datetime import datetime
        
        # Gather report data
        files = db.query(FileModel).filter(FileModel.user_id == current_user.id).all()
        total_chunks = db.query(Chunk).join(FileModel).filter(
            FileModel.user_id == current_user.id
        ).count()
        
        report_data = {
            "title": "Regnova Knowledge Base Report",
            "date": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
            "summary": f"Report for {current_user.name} ({current_user.email})",
            "file_count": len(files),
            "chunk_count": total_chunks
        }
        
        def send_report_task():
            success = gmail_service.send_report(
                to_email=to_email,
                report_data=report_data
            )
            if success:
                app_logger.info(f"✅ Report sent to {to_email}")
        
        if background_tasks:
            background_tasks.add_task(send_report_task)
        else:
            send_report_task()
        
        return {
            "message": "Report queued for sending",
            "to": to_email,
            "report_data": report_data
        }
    
    except Exception as e:
        app_logger.error(f"❌ Report email error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send report"
        )


# WhatsApp Routes
@router.post("/whatsapp/send")
async def send_whatsapp_message(
    whatsapp_request: WhatsAppRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Send a WhatsApp message via ***REMOVED***
    
    - Supports text messages
    - Can target specific numbers
    """
    try:
        def send_whatsapp_task():
            success = whatsapp_service.send_message(
                message=whatsapp_request.message,
                to_number=whatsapp_request.to_number
            )
            if success:
                app_logger.info("✅ WhatsApp message sent")
        
        background_tasks.add_task(send_whatsapp_task)
        
        return {
            "message": "WhatsApp message queued",
            "content": whatsapp_request.message[:50] + "..."
        }
    
    except Exception as e:
        app_logger.error(f"❌ WhatsApp error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue WhatsApp message"
        )


@router.post("/whatsapp/notify-upload")
async def notify_file_upload_whatsapp(
    filename: str,
    status: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Send WhatsApp notification about file upload
    """
    try:
        def notify_task():
            whatsapp_service.send_document_notification(
                filename=filename,
                status=status
            )
        
        background_tasks.add_task(notify_task)
        
        return {"message": "WhatsApp notification queued"}
    
    except Exception as e:
        app_logger.error(f"❌ WhatsApp notification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue notification"
        )


# Push Notification Routes
@router.post("/push/send")
async def send_push_notification(
    push_request: PushNotificationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Send a push notification via OneSignal
    
    - Supports targeting specific users or segments
    - Includes custom data payload
    """
    try:
        def send_push_task():
            success = push_service.send_onesignal_notification(
                heading=push_request.title,
                content=push_request.body,
                user_ids=push_request.user_ids,
                segments=push_request.segments
            )
            if success:
                app_logger.info("✅ Push notification sent")
        
        background_tasks.add_task(send_push_task)
        
        return {
            "message": "Push notification queued",
            "title": push_request.title
        }
    
    except Exception as e:
        app_logger.error(f"❌ Push notification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue push notification"
        )


@router.post("/push/notify-chat")
async def notify_chat_response_push(
    session_id: str,
    preview: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Send push notification about new chat response
    """
    try:
        def notify_task():
            push_service.notify_chat_response(
                user_id=str(current_user.id),
                session_id=session_id,
                preview=preview
            )
        
        background_tasks.add_task(notify_task)
        
        return {"message": "Chat notification queued"}
    
    except Exception as e:
        app_logger.error(f"❌ Chat notification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue notification"
        )


# Combined Automation Route
@router.post("/notify-all")
async def notify_all_channels(
    title: str,
    message: str,
    email_address: Optional[EmailStr] = None,
    include_whatsapp: bool = False,
    include_push: bool = False,
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user)
):
    """
    Send notification across all configured channels
    
    - Email (if address provided)
    - WhatsApp (if enabled)
    - Push (if enabled)
    """
    results = {
        "email": False,
        "whatsapp": False,
        "push": False
    }
    
    try:
        # Email
        if email_address:
            def email_task():
                results["email"] = gmail_service.send_notification(
                    to_email=email_address,
                    notification_type=title,
                    message=message
                )
            
            if background_tasks:
                background_tasks.add_task(email_task)
            else:
                email_task()
        
        # WhatsApp
        if include_whatsapp:
            def whatsapp_task():
                results["whatsapp"] = whatsapp_service.send_alert(
                    alert_type=title,
                    alert_message=message
                )
            
            if background_tasks:
                background_tasks.add_task(whatsapp_task)
            else:
                whatsapp_task()
        
        # Push
        if include_push:
            def push_task():
                results["push"] = push_service.send_onesignal_notification(
                    heading=title,
                    content=message,
                    user_ids=[str(current_user.id)]
                )
            
            if background_tasks:
                background_tasks.add_task(push_task)
            else:
                push_task()
        
        return {
            "message": "Notifications queued for all requested channels",
            "channels": results
        }
    
    except Exception as e:
        app_logger.error(f"❌ Multi-channel notification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue notifications"
        )


@router.get("/status")
async def get_automation_status(
    current_user: User = Depends(get_current_user)
):
    """
    Check status of automation services
    """
    from app.config import settings
    
    status = {
        "gmail": {
            "configured": bool(settings.GMAIL_EMAIL and settings.GMAIL_APP_PASSWORD),
            "email": settings.GMAIL_EMAIL if settings.GMAIL_EMAIL else None
        },
        "whatsapp": {
            "configured": bool(settings.***REMOVED***_ACCOUNT_SID and settings.***REMOVED***_***REMOVED***),
            "from_number": settings.***REMOVED***_WHATSAPP_FROM if settings.***REMOVED***_WHATSAPP_FROM else None
        },
        "push": {
            "onesignal_configured": bool(settings.ONESIGNAL_APP_ID and settings.ONESIGNAL_REST_API_KEY),
            "webpush_configured": bool(settings.VAPID_PUBLIC_KEY and settings.VAPID_PRIVATE_KEY)
        }
    }
    
    return status
