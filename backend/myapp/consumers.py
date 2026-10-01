import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer


class NotificationConsumer(AsyncWebsocketConsumer):
    """Broadcasts notifications to all connected clients."""

    async def connect(self):
        await self.channel_layer.group_add("notifications", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("notifications", self.channel_name)

    async def notify(self, event):
        await self.send(text_data=json.dumps({
            "type": "notify",
            "message": event["message"],
        }))


def broadcast_notification(message: str):
    """Send a notification to all connected WebSocket clients."""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "notifications",
        {"type": "notify", "message": message},
    )
