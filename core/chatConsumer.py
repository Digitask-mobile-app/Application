import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from django.utils import timezone
from channels.db import database_sync_to_async
import asyncio
import json
from asgiref.sync import sync_to_async
from .utils import slugify

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        channel_layer = get_channel_layer()

        user = self.scope['user']
        await self.send(text_data=json.dumps({
                'email': user.email
            }))
        self.user_email = self.scope['user'].email
        if user.is_authenticated:
    
            rooms = await database_sync_to_async(lambda: [x.name for x in user.member_rooms.all()])()
            
            for room_name in rooms: 

                group_name = f'room_{slugify(room_name)}'
                await channel_layer.group_add(
                    group_name,
                    self.channel_name
                )
        else:
    
            await self.send(text_data=json.dumps({
                'message': 'user auth deyil'
            }))
            await self.close()


    async def disconnect(self, close_code):
        channel_layer = get_channel_layer()
        user = self.scope['user']
 
        if user.is_authenticated:
            rooms = await database_sync_to_async(lambda: [x.name for x in user.member_rooms.all()])()
   
            for room_name in rooms:
                group_name = f'room_{slugify(room_name)}'
                await channel_layer.group_discard(
                    group_name,
                    self.channel_name
                )

    async def receive(self, text_data):
        from accounts.models import  Message, Room
        text_data_json = json.loads(text_data)
        room = text_data_json['room']
        content = text_data_json['content']
        user = self.scope['user']
       
   
        room = await database_sync_to_async(Room.objects.get)(id=room)
        message = await database_sync_to_async(Message.objects.create)(user=user, room=room, content=content)

        if message.user.email == self.user_email:
            typeM = 'sent'
        else:
            typeM = 'received'
     
        await self.channel_layer.group_send(
            f'room_{slugify(room.name)}',
            {
                'type': 'chat_message',
                'id':message.id,
                'content': message.content,
                'timestamp':message.timestamp.isoformat(),
                'room':room.id,
                'typeM':typeM,
                'user': {
                    'first_name':message.user.first_name,
                    'last_name':message.user.last_name,
                    'email':message.user.email,
                },
            }
        )
       


    async def chat_message(self, event):
        content = event['content']
        user = event['user']
        timestamp = event['timestamp']
        room = event['room']
        typeM = event['typeM']
        id = event['id']

        await self.send(text_data=json.dumps({
            'id':id,
            'content': content,
            'user': user,
            'timestamp':timestamp,
            'room':room,
            'typeM':typeM
        }))

    async def chat_email(self, event):
        email = event['email']

        await self.send(text_data=json.dumps({
            'email':email
        }))
