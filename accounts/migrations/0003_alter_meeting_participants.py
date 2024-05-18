# Generated by Django 5.0.4 on 2024-05-18 14:30

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_meeting'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='participants',
            field=models.ManyToManyField(related_name='meetings', to=settings.AUTH_USER_MODEL),
        ),
    ]
