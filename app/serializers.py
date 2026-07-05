from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Channel, Message

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ['id', 'name', 'created_at'] 

class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'user', 'sender_username', 'channel', 'content', 'created_at']
        read_only_fields = ['user', 'channel']