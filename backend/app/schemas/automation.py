"""
Schemas for automation services
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime


class EmailRequest(BaseModel):
    """Request to send email"""
    to_email: EmailStr
    subject: str
    body: str
    body_html: Optional[str] = None


class EmailRAGRequest(BaseModel):
    """Request to send RAG answer via email"""
    to_email: EmailStr
    question: str
    answer: str
    sources: List[Dict]
    user_name: Optional[str] = None


class WhatsAppRequest(BaseModel):
    """Request to send WhatsApp message"""
    to_number: str  # Format: whatsapp:+1234567890 or +1234567890
    message: str
    media_url: Optional[str] = None


class WhatsAppRAGRequest(BaseModel):
    """Request to send RAG answer via WhatsApp"""
    to_number: str
    question: str
    answer: str
    sources: List[Dict]


class PushNotificationRequest(BaseModel):
    """Request to send push notification"""
    user_ids: List[str]
    title: str
    message: str
    data: Optional[Dict] = None
    url: Optional[str] = None


class NotificationResponse(BaseModel):
    """Response for automation requests"""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    sent_at: Optional[datetime] = None
    notification_id: Optional[str] = None


class BulkNotificationRequest(BaseModel):
    """Request to send bulk notifications"""
    recipients: List[str]  # Email addresses, phone numbers, or user IDs
    notification_type: str  # email, whatsapp, push
    title: Optional[str] = None
    message: str
    data: Optional[Dict] = None


class BulkNotificationResponse(BaseModel):
    """Response for bulk notifications"""
    success: bool
    total: int
    sent: int
    failed: int
    details: List[Dict]
