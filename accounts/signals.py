from django.dispatch import receiver
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from accounts.models import Notification
from channels.layers import get_channel_layer


@receiver(post_save, sender=Notification)
def user_status_update(sender, instance, created, **kwargs):

    if created:
        channel_layer = get_channel_layer()
        print(created)
        async_to_sync(channel_layer.group_send)(
            'notification',
            {
                'type': 'notification_message',
                'message': {'data': 'group send workinggggggggggggggggggggggggggggggg'}
            }
        )
