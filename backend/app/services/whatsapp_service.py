"""
WhatsApp automation service using ***REMOVED***
"""

from ***REMOVED***.rest import Client
from typing import Optional
from app.utils.logger import app_logger
from app.config import settings


class WhatsAppService:
    """Service for WhatsApp automation via ***REMOVED***"""
    
    def __init__(self):
        """Initialize ***REMOVED*** client"""
        self.account_sid = settings.***REMOVED***_ACCOUNT_SID
        self.***REMOVED*** = settings.***REMOVED***_***REMOVED***
        self.from_number = settings.***REMOVED***_WHATSAPP_FROM
        self.to_number = settings.***REMOVED***_WHATSAPP_TO
        
        if self.account_sid and self.***REMOVED***:
            try:
                self.client = Client(self.account_sid, self.***REMOVED***)
                app_logger.info("✅ WhatsApp service initialized")
            except Exception as e:
                app_logger.error(f"❌ Failed to initialize ***REMOVED*** client: {str(e)}")
                self.client = None
        else:
            app_logger.warning("⚠️ ***REMOVED*** credentials not configured")
            self.client = None
    
    def send_message(
        self,
        message: str,
        to_number: Optional[str] = None,
        media_url: Optional[str] = None
    ) -> bool:
        """
        Send a WhatsApp message
        
        Args:
            message: Message text
            to_number: Optional recipient number (defaults to configured number)
            media_url: Optional media URL to send
        
        Returns:
            True if successful
        """
        if not self.client:
            app_logger.error("❌ WhatsApp service not initialized")
            return False
        
        try:
            recipient = to_number or self.to_number
            
            # Ensure proper WhatsApp format
            if not recipient.startswith('whatsapp:'):
                recipient = f'whatsapp:{recipient}'
            
            params = {
                'from_': self.from_number,
                'body': message,
                'to': recipient
            }
            
            # Add media if provided
            if media_url:
                params['media_url'] = [media_url]
            
            # Send message
            message_obj = self.client.messages.create(**params)
            
            app_logger.info(f"✅ WhatsApp message sent: {message_obj.sid}")
            return True
            
        except Exception as e:
            app_logger.error(f"❌ Failed to send WhatsApp message: {str(e)}")
            return False
    
    def send_document_notification(
        self,
        filename: str,
        status: str,
        details: Optional[str] = None
    ) -> bool:
        """
        Send notification about document processing
        
        Args:
            filename: Name of processed file
            status: Processing status
            details: Optional additional details
        
        Returns:
            True if successful
        """
        message = f"""
📄 *Document Update*

File: {filename}
Status: {status}
"""
        
        if details:
            message += f"\nDetails: {details}"
        
        message += "\n\n_Sent by Regnova Knowledge Assistant_"
        
        return self.send_message(message)
    
    def send_chat_summary(
        self,
        session_id: str,
        message_count: int,
        summary: str
    ) -> bool:
        """
        Send chat session summary
        
        Args:
            session_id: Chat session ID
            message_count: Number of messages
            summary: Brief summary
        
        Returns:
            True if successful
        """
        message = f"""
💬 *Chat Summary*

Session: {session_id[:8]}...
Messages: {message_count}

Summary: {summary}

_Sent by Regnova Knowledge Assistant_
"""
        
        return self.send_message(message)
    
    def send_alert(
        self,
        alert_type: str,
        alert_message: str
    ) -> bool:
        """
        Send an alert notification
        
        Args:
            alert_type: Type of alert
            alert_message: Alert message
        
        Returns:
            True if successful
        """
        message = f"""
🚨 *{alert_type}*

{alert_message}

_Sent by Regnova Knowledge Assistant_
"""
        
        return self.send_message(message)


# Global instance
whatsapp_service = WhatsAppService()
