import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Conversation
from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
            return
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"chat_{self.conversation_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,

        )
        print(self.room_group_name)
        print(self.scope["user"])
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(

            self.room_group_name,

            self.channel_name,

        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]

        saved_message = await self.save_message(message)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message":saved_message.content,
                "sender":saved_message.sender.username,
                "time":saved_message.created_at.strftime("%I:%M %p"),
            }
        )

    async def chat_message(self, event):
        
        await self.send(
            text_data=json.dumps(
                {
                    "message":event["message"],

                    "sender":event["sender"],

                    "time":event["time"]
                }
            )
        )

    @database_sync_to_async
    def save_message(self, message):
        conversation = Conversation.objects.get(
            id=self.conversation_id
        )

        return Message.objects.create(
            conversation=conversation,
            sender=self.scope["user"],
            content=message,
        )

