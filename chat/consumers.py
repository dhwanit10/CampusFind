import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Conversation, Message, ConversationStatus
from .models import Message
from django.utils import timezone
from django.db.models import F

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
        self.user_group = f"user_{self.scope['user'].username}"

        await self.channel_layer.group_add(
            self.user_group,      
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

        await self.channel_layer.group_discard(
            self.user_group,
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

        await self.send_sidebar_update(saved_message)

    async def chat_message(self, event):
        
        await self.send(
            text_data=json.dumps(
                {
                    "type":"chat",

                    "message":event["message"],

                    "sender":event["sender"],

                    "time":event["time"]
                }
            )
        )

    async def send_sidebar_update(self, saved_message):

        sidebar = await self.get_sidebar_data() 

        for row in sidebar: 
            await self.channel_layer.group_send(    
                f"user_{row['username']}",  
                {   
                    "type": "sidebar_update",   
                    "conversation": row["conversation"],    
                    "last_message": row["last_message"],    
                    "time": row["time"],    
                    "unread": row["unread"],    
                }   
            )

    async def sidebar_update(self, event):

        await self.send(

            text_data=json.dumps({
                "type": "sidebar",
                "conversation": event["conversation"],
                "last_message": event["last_message"],
                "time": event["time"],
                "unread": event["unread"],
            })

    )
    # @database_sync_to_async
    # def save_message(self, message):
    #     conversation = Conversation.objects.get(
    #         id=self.conversation_id
    #     )
    #     conversation.updated_at = timezone.now()
    #     conversation.save(update_fields=["updated_at"])

    #     return Message.objects.create(
    #         conversation=conversation,
    #         sender=self.scope["user"],
    #         content=message,
    #     )

    @database_sync_to_async
    def save_message(self, message):
        conversation = Conversation.objects.get(
            id=self.conversation_id
        )
        conversation.updated_at = timezone.now()
        conversation.save(
            update_fields=["updated_at"]
        )

        new_message = Message.objects.create(
            conversation=conversation,
            sender=self.scope["user"],
            content=message,
        )

        ConversationStatus.objects.filter(
            conversation=conversation
        ).exclude(
            user=self.scope["user"]
        ).update(
            unread_count=F("unread_count") + 1
        )
        return new_message


    @database_sync_to_async
    def get_sidebar_data(self):
        conversation = Conversation.objects.get(
            id=self.conversation_id
        )

        data = []

        for user in conversation.participants.all():
            status = ConversationStatus.objects.get(
                conversation=conversation,
                user=user
            )
            other = conversation.participants.exclude(
                id=user.id
            ).first()

            last = conversation.messages.last()

            data.append({
                "username": user.username,
                "other": other.username,
                "last_message": last.content,
                "time": last.created_at.strftime("%I:%M %p"),
                "unread": status.unread_count,
                "conversation": conversation.id,
            })

        return data
