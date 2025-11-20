"""
Push notification service using OneSignal and Web Push
"""

from onesignal_sdk.client import Client as OneSignalClient
from pywebpush import webpush, WebPushException
from typing import List, Optional, Dict
from app.utils.logger import app_logger
from app.config import settings
import json


class PushNotificationService:
    """Service for push notifications"""
    
    def __init__(self):
        """Initialize push notification services"""
        # OneSignal setup
        if settings.ONESIGNAL_APP_ID and settings.ONESIGNAL_REST_API_KEY:
            try:
                self.onesignal_client = OneSignalClient(
                    app_id=settings.ONESIGNAL_APP_ID,
                    rest_api_key=settings.ONESIGNAL_REST_API_KEY
                )
                app_logger.info("✅ OneSignal service initialized")
            except Exception as e:
                app_logger.error(f"❌ OneSignal initialization failed: {str(e)}")
                self.onesignal_client = None
        else:
            app_logger.warning("⚠️ OneSignal credentials not configured")
            self.onesignal_client = None
        
        # Web Push VAPID setup
        self.vapid_public_key = settings.VAPID_PUBLIC_KEY
        self.vapid_private_key = settings.VAPID_PRIVATE_KEY
        self.vapid_email = settings.VAPID_ADMIN_EMAIL
        
        if all([self.vapid_public_key, self.vapid_private_key, self.vapid_email]):
            app_logger.info("✅ Web Push VAPID configured")
        else:
            app_logger.warning("⚠️ Web Push VAPID not configured")
    
    def send_onesignal_notification(
        self,
        heading: str,
        content: str,
        user_ids: Optional[List[str]] = None,
        segments: Optional[List[str]] = None,
        data: Optional[Dict] = None
    ) -> bool:
        """
        Send notification via OneSignal
        
        Args:
            heading: Notification heading
            content: Notification content
            user_ids: Optional list of specific user IDs
            segments: Optional list of segments (e.g., ["All"])
            data: Optional additional data
        
        Returns:
            True if successful
        """
        if not self.onesignal_client:
            app_logger.error("❌ OneSignal not initialized")
            return False
        
        try:
            notification = {
                "headings": {"en": heading},
                "contents": {"en": content}
            }
            
            # Target specific users or segments
            if user_ids:
                notification["include_player_ids"] = user_ids
            elif segments:
                notification["included_segments"] = segments
            else:
                notification["included_segments"] = ["All"]
            
            # Add custom data
            if data:
                notification["data"] = data
            
            # Send notification
            response = self.onesignal_client.send_notification(notification)
            
            app_logger.info(f"✅ OneSignal notification sent: {response}")
            return True
            
        except Exception as e:
            app_logger.error(f"❌ OneSignal send failed: {str(e)}")
            return False
    
    def send_web_push(
        self,
        subscription_info: Dict,
        title: str,
        body: str,
        data: Optional[Dict] = None
    ) -> bool:
        """
        Send Web Push notification
        
        Args:
            subscription_info: Push subscription object from browser
            title: Notification title
            body: Notification body
            data: Optional additional data
        
        Returns:
            True if successful
        """
        if not all([self.vapid_public_key, self.vapid_private_key, self.vapid_email]):
            app_logger.error("❌ VAPID not configured")
            return False
        
        try:
            # Prepare notification payload
            payload = {
                "title": title,
                "body": body,
                "icon": "/icon.png",
                "badge": "/badge.png"
            }
            
            if data:
                payload["data"] = data
            
            # Send push notification
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=self.vapid_private_key,
                vapid_claims={
                    "sub": f"mailto:{self.vapid_email}"
                }
            )
            
            app_logger.info("✅ Web Push notification sent")
            return True
            
        except WebPushException as e:
            app_logger.error(f"❌ Web Push failed: {str(e)}")
            return False
    
    def notify_file_processed(
        self,
        user_id: str,
        filename: str,
        status: str
    ) -> bool:
        """
        Notify user about file processing status
        
        Args:
            user_id: User ID
            filename: Processed filename
            status: Processing status
        
        Returns:
            True if successful
        """
        heading = "File Processing Update"
        content = f"File '{filename}' has been {status}"
        
        data = {
            "type": "file_processed",
            "filename": filename,
            "status": status
        }
        
        return self.send_onesignal_notification(
            heading=heading,
            content=content,
            user_ids=[user_id],
            data=data
        )
    
    def notify_chat_response(
        self,
        user_id: str,
        session_id: str,
        preview: str
    ) -> bool:
        """
        Notify user about new chat response
        
        Args:
            user_id: User ID
            session_id: Chat session ID
            preview: Response preview
        
        Returns:
            True if successful
        """
        heading = "New Chat Response"
        content = preview[:100] + "..." if len(preview) > 100 else preview
        
        data = {
            "type": "chat_response",
            "session_id": session_id
        }
        
        return self.send_onesignal_notification(
            heading=heading,
            content=content,
            user_ids=[user_id],
            data=data
        )
    
    def notify_system_alert(
        self,
        alert_type: str,
        message: str,
        segments: Optional[List[str]] = None
    ) -> bool:
        """
        Send system-wide alert
        
        Args:
            alert_type: Type of alert
            message: Alert message
            segments: Optional user segments
        
        Returns:
            True if successful
        """
        heading = f"System Alert: {alert_type}"
        
        data = {
            "type": "system_alert",
            "alert_type": alert_type
        }
        
        return self.send_onesignal_notification(
            heading=heading,
            content=message,
            segments=segments or ["All"],
            data=data
        )


# Global instance
push_service = PushNotificationService()
