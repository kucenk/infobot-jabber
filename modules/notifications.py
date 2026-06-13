"""
Notification manager for alerts
"""

import logging

logger = logging.getLogger(__name__)


class NotificationManager:
    """Manage and send notifications"""
    
    def __init__(self, bot):
        self.bot = bot
        self.alert_cache = {}
    
    async def send_notification(self, room_jid: str, message: str, alert_type: str = 'info'):
        """Send notification to room"""
        try:
            self.bot.send_message(
                mto=room_jid,
                mbody=message,
                mtype='groupchat'
            )
            logger.info(f"✅ Notification sent to {room_jid}")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
