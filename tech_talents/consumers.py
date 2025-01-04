import json
from channels.generic.websocket import AsyncWebsocketConsumer

class QueueStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept the WebSocket connection
        await self.accept()

        # Add the user to a group (optional, if broadcasting to a group)
        self.group_name = f"queue_updates"
        await self.channel_layer.group_add(self.group_name, self.channel_name)

    async def disconnect(self, close_code):
        # Remove the user from the group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        # Handle incoming messages (if any, optional)
        pass

    async def send_queue_update(self, event):
        # Send queue update to the client
        await self.send(text_data=json.dumps(event['data']))
