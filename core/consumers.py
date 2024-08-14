import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from django.utils import timezone
from channels.db import database_sync_to_async
import asyncio
import json


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        channel_layer = get_channel_layer()

        await channel_layer.group_add(
            "notification",
            self.channel_name
        )
        await self.channel_layer.group_send(
            'notification',
            {
                'type': 'notification_message',
                'message': {'data': 'group send workinggggggggggggggggggggggggggggggg'}
            }
        )

    async def disconnect(self, close_code):
        channel_layer = get_channel_layer()
        await channel_layer.group_discard(
            "notification",
            self.channel_name
        )

    async def notification_message(self, event):
        user = self.scope['user']
        message = event['message']
        if user.is_authenticated:
            message = await self.get_notifications(user)
            print(
                message, '-----------------------------------------------------------------------------')
            print(
                message, '-----------------------------------------------------------------------------')
            await self.send(text_data=json.dumps({
                'message': message
            }))

    @database_sync_to_async
    def get_notifications(self, user):
        from accounts.models import Notification

        notifications = Notification.objects.filter(
            users=user).order_by('-created_at')

        response_data = []

        for notification in notifications:
            response_data.append({
                'id': notification.id,
                'message': notification.message,
                'user_email': notification.user_email,
                'created_at': notification.created_at.isoformat(),
                'read_by': notification.is_read_by(user),
            })
        return response_data

###########################################################################


class UserListConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        channel_layer = get_channel_layer()
        await channel_layer.group_add(
            "status",
            self.channel_name
        )

        self.keep_sending = True
        asyncio.create_task(self.send_online_users_periodically())

    async def disconnect(self, close_code):
        channel_layer = get_channel_layer()
        await channel_layer.group_discard(
            "status",
            self.channel_name
        )
        self.keep_sending = False

    async def send_online_users_periodically(self):
        while self.keep_sending:
            user_list = await self.get_online_users()
            await self.send_users(user_list)
            await self.channel_layer.group_send(
                "status",
                {
                    "type": "status_message",  # Handler olarak kullanılacak tür
                    "message": user_list,
                },
            )

            await asyncio.sleep(8)

    async def receive(self, text_data):
        data = json.loads(text_data)

        user_list = await self.get_online_users()
        await self.send_users(user_list)

    async def send_users(self, message):
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def status_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def get_online_users(self):
        from accounts.models import User

        return {str(user.id): {'status':'online','location':{'latitude':user.latitude,'longitude':user.longitude},'user':{'email':user.email}} if user.is_online else {'status':'offline'} for user in User.objects.all()}


class StatusConsumer(AsyncWebsocketConsumer):
    online_users = {}

    async def connect(self):
        await self.accept()
        user = self.scope['user']
        channel_layer = get_channel_layer()
        await channel_layer.group_add(
            "status",
            self.channel_name
        )

        if user.is_authenticated:
            await self.update_user_status(user, True)
            print(
                user.email + ' email istifadeci qosuldu ++++++++++++++++++++++++++++++++++')

        await self.broadcast_message({user.id: 'online'})

    async def disconnect(self, close_code):
        user = self.scope['user']

        if user.is_authenticated:
            print(
                user.email + ' email istifadeci terk etdi ++++++++++++++++++++++++++++++++++')
            await self.update_user_status(user, False)
        channel_layer = get_channel_layer()
        await channel_layer.group_discard(
            "status",
            self.channel_name
        )

    async def receive(self, text_data):

        data = json.loads(text_data)
        user = self.scope['user']
        location = data.get('location', {})

        if location is not None and user.is_authenticated:
            latitude = location.get('latitude')
            longitude = location.get('longitude')
            print(latitude, longitude,
                  '++++++++++++++++++++++++++++++++++++++++++++++')

            await self.update_user_location(user, latitude, longitude)
        else:
            print('location yoxdur')
        message = data.get('message', 'Bu ne ucun var bilmirem')
        await self.broadcast_message(message)

    async def status_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def broadcast_message(self, message):
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def update_user_status(self, user, is_online):
        user.is_online = is_online
        user.timestamp = timezone.now()
        user.save()

    @database_sync_to_async
    def update_user_location(self, user, latitude, longitude):
        user.latitude = latitude
        user.longitude = longitude
        user.save()


# await self.channel_layer.group_send(
#                     "status",
#                     {
#                         "type": "status_message",  # Handler olarak kullanılacak tür
#                         "message": {'------------------------------------------------': '----------------------------------------------'},
#                     },
#                 )

    # async def status_message(self, event):
    #     message = event['message']
    #     await self.send(text_data=json.dumps({
    #         'message': message
    #     }))
