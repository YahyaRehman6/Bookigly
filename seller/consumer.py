from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
import json


class Notification_Consumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        hotel = self.scope['url_route']['kwargs']['hotel']
        await get_channel_layer().group_add(str(hotel), self.channel_name)

        # message = {
        #     "type":"noti.app",
        #     "text":json.dumps({"message":"Reservation is received"})
        #     }
        # await get_channel_layer().group_send(hotel,message)

    async def noti_app(self, text):
        await self.send(text_data=text['text'])

    async def disconnect(self, code):
        print("Disconnect..", code)
