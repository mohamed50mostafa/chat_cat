from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
import pusher

from .models import Channel, Message
from .serializers import ChannelSerializer, MessageSerializer, UserSerializer

import environ
env = environ.Env()

# ثم داخل إعدادات Pusher:
app_id=env('PUSHER_APP_ID')
# ... وهكذا مع الباقي

# Initialize Pusher client securely
pusher_client = pusher.Pusher(
    app_id=env('PUSHER_APP_ID'),
    key=env('PUSHER_KEY'),
    secret=env('PUSHER_SECRET'),
    cluster=env('PUSHER_CLUSTER'),
    ssl=True
)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '').strip()

    if not username or not password:
        return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username is already taken."}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password)
    return Response(
        {"message": "User registered successfully.", "user": UserSerializer(user).data}, 
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_channel(request):
    channel_name = request.data.get('name', '').strip()

    if not channel_name:
        return Response({"error": "Please specify a name for the public channel."}, status=status.HTTP_400_BAD_REQUEST)

    if Channel.objects.filter(name=channel_name).exists():
        return Response({"error": "A channel with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)
        
    channel = Channel.objects.create(name=channel_name)
    return Response(ChannelSerializer(channel).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_channels(request):
    channel_name = request.query_params.get('name', '').strip()
    
    if channel_name:
        channels = Channel.objects.filter(name__icontains=channel_name).order_by('-created_at')
    else:
        channels = Channel.objects.all().order_by('-created_at')
        
    serializer = ChannelSerializer(channels, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    channel_id = request.data.get('channel_id')
    content = request.data.get('message', '').strip()

    if not content or not channel_id:
        return Response({"error": "Message and channel_id are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        channel = Channel.objects.get(id=channel_id)
    except Channel.DoesNotExist:
        return Response({"error": "The requested channel does not exist."}, status=status.HTTP_404_NOT_FOUND)

    # Create the message instance
    message = Message.objects.create(user=request.user, channel=channel, content=content)

    # Trigger Pusher real-time event
    pusher_client.trigger(
        f'public-chat-{channel_id}',
        'new-message',
        {
            'id': message.id,
            'username': request.user.username,
            'message': content,
            'created_at': message.created_at.strftime("%Y-%m-%d %H:%M")
        }
    )

    return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages(request, channel_id):
    try:
        channel = Channel.objects.get(id=channel_id)
    except Channel.DoesNotExist:
        return Response({"error": "The requested channel does not exist."}, status=status.HTTP_404_NOT_FOUND)

    # Optimization: Added select_related('user') to optimize DB queries (Prevents N+1 issue)
    messages = Message.objects.filter(channel=channel).select_related('user').order_by('created_at')
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)