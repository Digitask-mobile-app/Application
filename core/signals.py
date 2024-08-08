from django.dispatch import receiver
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from accounts.models import User
from channels.layers import get_channel_layer
import json

@receiver(post_save, sender=User)
def user_status_update(sender, instance, **kwargs):
    from core.consumers import UserListConsumer
    print('yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy')
    print(kwargs,'-----------------------------------------------')
    print(kwargs.get('updated_fields'))
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
            'status',  # WebSocket grubu
            {
                'type': 'send_users',  # Consumer metodunu belirtir
                'message': {'data': 'group send workinggggggggggggggggggggggggggggggg'}
            }
        )
    print('group message senttttttttttttttttttt')
    if kwargs.get('update_fields') and 'is_online' in kwargs['update_fields']:
        online_users = User.objects.all().values('username', 'is_online')
        print(online_users)
        async_to_sync(UserListConsumer.send_users)({'message': online_users})

def send_users_custom(self, message):
        self.send(text_data=json.dumps({
            'message': message
        }))