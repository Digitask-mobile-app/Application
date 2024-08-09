import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from django.utils import timezone
from channels.db import database_sync_to_async
import asyncio

# class StatusConsumer(AsyncWebsocketConsumer):
#     online_users = {}

#     async def connect(self):
#         await self.accept()
#         self.user_id = self.scope['user'].id if self.scope['user'].is_authenticated else None
       
#         if self.user_id:
#             channel_layer = get_channel_layer()
#             await channel_layer.group_add(
#                 'status_updates',
#                 self.channel_name
#             )
#             StatusConsumer.online_users[self.user_id] = self.channel_name
#             await self.update_user_status(self.user_id, True)
#             await self.broadcast_status(self.user_id, 'online')
#             print(f"User {self.user_id} connected and status set to online.")
#         else:
#             print("Unauthenticated user tried to connect.")

#     async def disconnect(self, close_code):
#         if self.user_id in StatusConsumer.online_users:
#             del StatusConsumer.online_users[self.user_id]
#             await self.update_user_status(self.user_id, False)
#             await self.broadcast_status(self.user_id, 'offline')
#             print(f"User {self.user_id} disconnected and status set to offline.")

#     @database_sync_to_async
#     def update_user_status(self, user_id, online):
#         from accounts.models import User
#         try:
#             user = User.objects.get(id=user_id)
#             user.is_online = online
#             user.save()
#         except User.DoesNotExist:
#             print(f"User with ID {user_id} does not exist.")
#         except Exception as e:
#             print(f"Error updating user status: {e}")


#     async def receive(self, text_data):
#         print(f"Received WebSocket message: {text_data}")
#         data = json.loads(text_data)
#         user_id = data.get('userId')
#         status = data.get('status')

#         if user_id and status:
#             await self.broadcast_status(user_id, status)
#         else:
#             print(f"Invalid message received: {text_data}")

#     async def broadcast_status(self, user_id, status):
#         channel_layer = get_channel_layer()
#         await channel_layer.group_send(
#             'status_updates',
#             {
#                 'type': 'user_status',
#                 'user_id': user_id,
#                 'status': status
#             }
#         )
#         print(f"Broadcasting status: {status} user: {user_id}")

#     async def user_status(self, event):
#         await self.send(text_data=json.dumps({
#             'userId': event['user_id'],
#             'status': event['status']
#         }))
#         print(f"Status: {event['status']} user: {event['user_id']}")

# How to take arg from ws url ------------------------------------

# query_string = self.scope.get("query_string", b"").decode()
# query_params = parse_qs(query_string)
# email = query_params.get("email", [None])[0]

#------------------------------------------------------

#-----------------------------------------------
#group_senddeki typeda ise saldigimiz functionun adini yaziriq

#channel_layer = get_channel_layer()
#        await channel_layer.group_add(
#            "status",
#            self.channel_name
#        )

#---------------------------------
#        user = self.scope['user'] useri goturmek ucun
#--------------------------------------------

#  await self.channel_layer.group_send(
#                 "status",
#                 {
#                     "type": "broadcast_message",
#                     "text": 'text_data',
#                 },
#             )

#group_send ---------------------------------------
 

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
        print('connected userlist')

    async def disconnect(self, close_code):
        channel_layer = get_channel_layer()
        await channel_layer.group_discard(
            "status",
            self.channel_name
        )
        self.keep_sending = False
        print('disconnected userlist')

    

    async def send_online_users_periodically(self):
        while self.keep_sending:
            user_list = await self.get_online_users()
            await self.send_users(user_list)
            print('group message sent')
            
            print('group message sent2')
            await asyncio.sleep(10)

    async def send_users(self, message):
        print('ws222222222222222222222222222222')
        
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def receive(self, text_data):
        data = json.loads(text_data)
        print('---------------------------------------------------------------------------')
        await self.channel_layer.group_send(
                "status",
                {
                    "type": "send_users",
                    "text": 'text_data',
                },
            )
        print('riciverrrrrrrrr worksssssssssss')
        user_list = await self.get_online_users()
        await self.send_users(user_list)
        

    @database_sync_to_async
    def get_online_users(self):
        from accounts.models import User
        print('inuserssssssssssss')
        return list(User.objects.filter(is_online=True).values('id', 'username'))





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
            print(user.email + ' email istifadeci qosuldu')

        
        await self.broadcast_message({user.id:'online'})

    async def disconnect(self, close_code):
        user = self.scope['user']
        
        if user.is_authenticated:
            print(user.email + ' email istifadeci terk etdi')
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
            print(latitude,longitude)
            
            await self.update_user_location(user,latitude,longitude)
        else:
            print('location yoxdur')
        message = data.get('message', 'Bu ne ucun var bilmirem')
        await self.broadcast_message(message)
     

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
    def update_user_location(self,user,latitude,longitude):
        user.latitude = latitude
        user.longitude = longitude
        user.save()