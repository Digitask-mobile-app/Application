from django.dispatch import receiver
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from accounts.models import User

@receiver(post_save, sender=User)
def user_status_update(sender, instance, **kwargs):
    from core.consumers import UserListConsumer
    print('yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy')
    print(kwargs,'-----------------------------------------------')
    if kwargs.get('update_fields') and 'is_online' in kwargs['update_fields']:
        online_users = User.objects.all().values('username', 'is_online')
        print(online_users)
        async_to_sync(UserListConsumer.send_users)({'data': online_users})
