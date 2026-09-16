import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PostConsumer(AsyncWebsocketConsumer):
    """Handles real-time updates for a specific post (likes and comments)."""

    async def connect(self):
        self.post_id = self.scope['url_route']['kwargs']['post_id']
        self.group = f"post_{self.post_id}"

        # Join post group
        await self.channel_layer.group_add(
            self.group,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave post group
        await self.channel_layer.group_discard(
            self.group,
            self.channel_name
        )

    async def post_update(self, event):
        """Handle broadcasted post update event."""
        await self.send(text_data=json.dumps(event))
