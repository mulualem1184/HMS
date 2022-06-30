from django.utils import timezone
from django.utils.timesince import timesince as timesince_
from rest_framework import serializers

from .models import *


class NotificationSerializer(serializers.ModelSerializer):
    created_date =  serializers.SerializerMethodField('timesince')
    
    class Meta:
        model = Notification
        fields = ['tag', 'noti', 'desc', 'link', 'sender', 'created_date']

    
    def timesince(self, noti):
        return str(timesince_(noti.created_date, timezone.now()))
