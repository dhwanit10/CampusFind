from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        print("connected")
        await self.accept()

    async def disconnect(self, close_code):
        print("disconnected")

    async def receive(self, text_data):
        print("Received:", text_data)

        await self.send(
            text_data="Server received: " + text_data
        )