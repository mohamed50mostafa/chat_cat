from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

urlpatterns = [
    # Authentication Endpoints
    path('api/register/', views.register_user, name='register'),
    path('api/login/', TokenObtainPairView.as_view(), name='login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Chat Engine & Channels Endpoints
    path('api/channels/create/', views.create_channel, name='create_channel'),
    path('api/channels/', views.get_channels, name='get_channels'),
    path('api/messages/send/', views.send_message, name='send_message'),
    path('api/channels/<int:channel_id>/messages/', views.get_messages, name='get_messages'),
]