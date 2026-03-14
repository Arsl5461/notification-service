"""
Firebase Cloud Messaging: send to a topic (broadcast by location).
One topic per location = one API call delivers to all workers at that location.
"""
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

_firebase_app = None


def get_firebase_app():
    global _firebase_app
    if _firebase_app is not None:
        return _firebase_app
    try:
        import firebase_admin
        from firebase_admin import credentials
        from app.config import get_settings
        settings = get_settings()
        if settings.firebase_credentials_path and os.path.isfile(settings.firebase_credentials_path):
            cred = credentials.Certificate(settings.firebase_credentials_path)
        elif settings.firebase_credentials_base64:
            import base64
            import json
            data = base64.b64decode(settings.firebase_credentials_base64)
            cred = credentials.Certificate(json.loads(data))
        else:
            logger.warning("Firebase credentials not configured; notifications will be no-ops.")
            return None
        _firebase_app = firebase_admin.initialize_app(cred)
        return _firebase_app
    except Exception as e:
        logger.warning("Firebase init failed: %s", e)
        return None


def send_to_topic(topic: str, title: str, body: str) -> tuple[bool, Optional[str]]:
    """
    Send a notification to all devices subscribed to the given FCM topic.
    Returns (success, error_message).
    """
    app = get_firebase_app()
    if not app:
        return False, "Firebase not configured"
    try:
        from firebase_admin import messaging
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            topic=topic,
        )
        messaging.send(message)
        return True, None
    except Exception as e:
        logger.exception("FCM send failed: %s", e)
        return False, str(e)
