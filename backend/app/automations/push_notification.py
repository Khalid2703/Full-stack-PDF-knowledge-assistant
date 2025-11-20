"""
Push notification service for web and mobile
Supports Web Push API and OneSignal integration
"""

from typing import Dict, List, Optional
from datetime import datetime
import os
import json
from app.utils.logger import app_logger


class PushNotificationService:
    """
    Push notification service for web and mobile apps
    """
    
    def __init__(self):
        """Initialize push notification service"""
        self.onesignal_app_id = os.getenv("ONESIGNAL_APP_ID")
        self.onesignal_api_key = os.getenv("ONESIGNAL_API_KEY")
        
        self.enabled = False
        
        if self.onesignal_app_id and self.onesignal_api_key:
            try:
                import requests
                self.requests = requests
                self.enabled = True
                app_logger.info("Push notification service initialized (OneSignal)")
            except ImportError:
                app_logger.warning("Requests library required for push notifications")
        else:
            app_logger.warning("Push notification not configured. Set ONESIGNAL credentials")
    
    def send_notification(
        self,
        user_ids: List[str],
        title: str,
        message: str,
        data: Optional[Dict] = None,
        url: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Send push notification via OneSignal
        
        Args:
            user_ids: List of user IDs or device IDs
            title: Notification title
            message: Notification message
            data: Additional data payload
            url: URL to open on click
        
        Returns:
            Status dictionary
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "Push notification service not configured"
            }
        
        try:
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Basic {self.onesignal_api_key}"
            }
            
            payload = {
                "app_id": self.onesignal_app_id,
                "include_external_user_ids": user_ids,
                "headings": {"en": title},
                "contents": {"en": message}
            }
            
            if data:
                payload["data"] = data
            
            if url:
                payload["url"] = url
            
            response = self.requests.post(
                "https://onesignal.com/api/v1/notifications",
                headers=headers,
                json=payload
            )
            
            result = response.json()
            
            if response.status_code == 200:
                app_logger.info(f"Push notification sent to {len(user_ids)} users")
                return {
                    "success": True,
                    "notification_id": result.get("id"),
                    "recipients": result.get("recipients", 0),
                    "sent_at": datetime.utcnow().isoformat()
                }
            else:
                app_logger.error(f"Push notification failed: {result}")
                return {
                    "success": False,
                    "error": result.get("errors", ["Unknown error"])[0]
                }
        
        except Exception as e:
            app_logger.error(f"Push notification error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_to_all(
        self,
        title: str,
        message: str,
        data: Optional[Dict] = None,
        url: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Send push notification to all subscribed users
        
        Args:
            title: Notification title
            message: Notification message
            data: Additional data payload
            url: URL to open on click
        
        Returns:
            Status dictionary
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "Push notification service not configured"
            }
        
        try:
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Basic {self.onesignal_api_key}"
            }
            
            payload = {
                "app_id": self.onesignal_app_id,
                "included_segments": ["All"],
                "headings": {"en": title},
                "contents": {"en": message}
            }
            
            if data:
                payload["data"] = data
            
            if url:
                payload["url"] = url
            
            response = self.requests.post(
                "https://onesignal.com/api/v1/notifications",
                headers=headers,
                json=payload
            )
            
            result = response.json()
            
            if response.status_code == 200:
                app_logger.info("Push notification sent to all users")
                return {
                    "success": True,
                    "notification_id": result.get("id"),
                    "recipients": result.get("recipients", 0)
                }
            else:
                return {
                    "success": False,
                    "error": result.get("errors", ["Unknown error"])[0]
                }
        
        except Exception as e:
            app_logger.error(f"Push notification error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_rag_answer_notification(
        self,
        user_ids: List[str],
        question: str,
        session_id: str
    ) -> Dict[str, any]:
        """
        Send notification when RAG answer is ready
        
        Args:
            user_ids: List of user IDs
            question: Question that was answered
            session_id: Chat session ID
        
        Returns:
            Status dictionary
        """
        title = "Answer Ready"
        message = f"Your question '{question[:50]}...' has been answered"
        
        data = {
            "type": "rag_answer",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        url = f"/chat/{session_id}"
        
        return self.send_notification(user_ids, title, message, data, url)
    
    def send_file_processed_notification(
        self,
        user_ids: List[str],
        filename: str,
        file_id: int
    ) -> Dict[str, any]:
        """
        Send notification when file is processed
        
        Args:
            user_ids: List of user IDs
            filename: Name of processed file
            file_id: File ID
        
        Returns:
            Status dictionary
        """
        title = "File Processed"
        message = f"'{filename}' has been processed and is ready for search"
        
        data = {
            "type": "file_processed",
            "file_id": file_id,
            "filename": filename
        }
        
        url = f"/files/{file_id}"
        
        return self.send_notification(user_ids, title, message, data, url)
    
    def send_report_ready_notification(
        self,
        user_ids: List[str],
        report_title: str,
        download_url: str
    ) -> Dict[str, any]:
        """
        Send notification when report is ready
        
        Args:
            user_ids: List of user IDs
            report_title: Title of the report
            download_url: URL to download report
        
        Returns:
            Status dictionary
        """
        title = "Report Ready"
        message = f"Your report '{report_title}' is ready for download"
        
        data = {
            "type": "report_ready",
            "report_title": report_title
        }
        
        return self.send_notification(user_ids, title, message, data, download_url)
    
    def get_notification_status(self, notification_id: str) -> Dict[str, any]:
        """
        Get status of sent notification
        
        Args:
            notification_id: Notification ID from OneSignal
        
        Returns:
            Status dictionary
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "Push notification service not configured"
            }
        
        try:
            headers = {
                "Authorization": f"Basic {self.onesignal_api_key}"
            }
            
            response = self.requests.get(
                f"https://onesignal.com/api/v1/notifications/{notification_id}",
                headers=headers,
                params={"app_id": self.onesignal_app_id}
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "id": result.get("id"),
                    "successful": result.get("successful", 0),
                    "failed": result.get("failed", 0),
                    "converted": result.get("converted", 0),
                    "remaining": result.get("remaining", 0)
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to fetch notification status"
                }
        
        except Exception as e:
            app_logger.error(f"Error getting notification status: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# Global instance
push_notification_service = PushNotificationService()
