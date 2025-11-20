"""
WhatsApp automation service using ***REMOVED***
Send WhatsApp messages with answers and notifications
"""

from typing import Dict, Optional, List
from datetime import datetime
import os
from app.utils.logger import app_logger


class WhatsAppService:
    """
    WhatsApp automation using ***REMOVED*** API
    """
    
    def __init__(self):
        """Initialize WhatsApp service"""
        self.account_sid = os.getenv("***REMOVED***_ACCOUNT_SID")
        self.***REMOVED*** = os.getenv("***REMOVED***_***REMOVED***")
        self.from_number = os.getenv("***REMOVED***_WHATSAPP_NUMBER", "whatsapp:+14155238886")  # ***REMOVED*** sandbox
        
        self.client = None
        self.enabled = False
        
        if self.account_sid and self.***REMOVED***:
            try:
                from ***REMOVED***.rest import Client
                self.client = Client(self.account_sid, self.***REMOVED***)
                self.enabled = True
                app_logger.info("WhatsApp service initialized successfully")
            except ImportError:
                app_logger.warning("***REMOVED*** library not installed. Run: pip install ***REMOVED***")
            except Exception as e:
                app_logger.error(f"Failed to initialize WhatsApp service: {str(e)}")
        else:
            app_logger.warning("WhatsApp service not configured. Set ***REMOVED*** credentials")
    
    def send_message(
        self,
        to_number: str,
        message: str,
        media_url: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Send WhatsApp message
        
        Args:
            to_number: Recipient WhatsApp number (format: whatsapp:+1234567890)
            message: Message text
            media_url: Optional media URL
        
        Returns:
            Status dictionary
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "WhatsApp service not configured"
            }
        
        # Ensure number has whatsapp: prefix
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"
        
        try:
            # Send message
            params = {
                "from_": self.from_number,
                "to": to_number,
                "body": message
            }
            
            if media_url:
                params["media_url"] = [media_url]
            
            message_obj = self.client.messages.create(**params)
            
            app_logger.info(f"WhatsApp message sent to {to_number}, SID: {message_obj.sid}")
            
            return {
                "success": True,
                "message_sid": message_obj.sid,
                "to": to_number,
                "status": message_obj.status,
                "sent_at": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            app_logger.error(f"Failed to send WhatsApp message: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_rag_answer(
        self,
        to_number: str,
        question: str,
        answer: str,
        sources: List[Dict]
    ) -> Dict[str, any]:
        """
        Send RAG answer via WhatsApp
        
        Args:
            to_number: Recipient WhatsApp number
            question: User question
            answer: Generated answer
            sources: Source citations
        
        Returns:
            Status dictionary
        """
        # Format message for WhatsApp (max 1600 chars)
        message = f"""*Regnova Knowledge Assistant*

*Question:*
{question[:200]}

*Answer:*
{answer[:800]}

*Sources:*
"""
        
        for i, source in enumerate(sources[:3]):  # Limit to 3 sources
            message += f"\n{i+1}. {source['filename']}"
            if source.get('page_number'):
                message += f" (p.{source['page_number']})"
        
        message += f"\n\n_Generated at {datetime.utcnow().strftime('%H:%M UTC')}_"
        
        return self.send_message(to_number, message)
    
    def send_notification(
        self,
        to_number: str,
        notification_type: str,
        message: str
    ) -> Dict[str, any]:
        """
        Send notification via WhatsApp
        
        Args:
            to_number: Recipient number
            notification_type: Type of notification
            message: Notification message
        
        Returns:
            Status dictionary
        """
        formatted_message = f"""*Regnova Notification*

*Type:* {notification_type}

{message}

_Sent at {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}_
"""
        
        return self.send_message(to_number, formatted_message)
    
    def send_bulk_messages(
        self,
        recipients: List[str],
        message: str
    ) -> Dict[str, any]:
        """
        Send bulk messages to multiple recipients
        
        Args:
            recipients: List of WhatsApp numbers
            message: Message to send
        
        Returns:
            Status dictionary with results
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "WhatsApp service not configured"
            }
        
        results = {
            "total": len(recipients),
            "sent": 0,
            "failed": 0,
            "details": []
        }
        
        for number in recipients:
            result = self.send_message(number, message)
            
            if result["success"]:
                results["sent"] += 1
            else:
                results["failed"] += 1
            
            results["details"].append({
                "number": number,
                "success": result["success"],
                "error": result.get("error")
            })
        
        results["success"] = results["sent"] > 0
        
        app_logger.info(f"Bulk WhatsApp: {results['sent']}/{results['total']} sent successfully")
        
        return results
    
    def get_message_status(self, message_sid: str) -> Dict[str, any]:
        """
        Get status of sent message
        
        Args:
            message_sid: Message SID from ***REMOVED***
        
        Returns:
            Status dictionary
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "WhatsApp service not configured"
            }
        
        try:
            message = self.client.messages(message_sid).fetch()
            
            return {
                "success": True,
                "sid": message.sid,
                "status": message.status,
                "to": message.to,
                "from": message.from_,
                "date_sent": message.date_sent.isoformat() if message.date_sent else None,
                "error_code": message.error_code,
                "error_message": message.error_message
            }
        
        except Exception as e:
            app_logger.error(f"Failed to get message status: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# Global instance
whatsapp_service = WhatsAppService()
