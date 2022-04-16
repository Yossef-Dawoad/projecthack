import json
from channels.generic.websocket import AsyncWebsocketConsumer


class VideoHandlerConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    async def connect(self):
        self.roomName = "video_pool"
        await self.channel_layer.group_add( #create video_pool group
            self.roomName,
            self.channel_name
        )
        await self.accept()


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.roomName,
            self.channel_name
        )



    async def receive(self, text_data=None, bytes_data=None):
        await self.channel_layer.group_send(
            self.roomName,{
                'type':'videoStream',
                'data':bytes_data}
        )

    async def videoStream(self, event):
        image_bytes = event['data']
        await self.send(bytes_data=image_bytes)