import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    """Pushes real-time notification events to the logged-in user.

    Pattern copied from chat.consumers.SidebarConsumer: each user joins a
    `user_<id>` channel group; views/services send events to that group via
    `channel_layer.group_send(..., {"type": "notify", "payload": ...})`.
    """

    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        self.group = f"user_{self.scope['user'].id}"

        await self.channel_layer.group_add(
            self.group,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group,
            self.channel_name,
        )

    async def notify(self, event):
        """Handle a `notify` group event by forwarding to the WebSocket."""
        await self.send(
            text_data=json.dumps(event["payload"]),
        )