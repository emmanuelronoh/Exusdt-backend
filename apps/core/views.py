from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import AnonymousUser, SecurityEvent
from .serializers import UserSerializer, SecurityEventSerializer
import uuid
import hashlib
from django.conf import settings
from django.utils import timezone

class UserCreateView(generics.CreateAPIView):
    queryset = AnonymousUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        # Generate exchange code
        prefix = settings.XUSDT_SETTINGS['EXCHANGE_CODE_PREFIX']
        code_length = settings.XUSDT_SETTINGS['EXCHANGE_CODE_LENGTH']
        random_code = str(uuid.uuid4().int)[:code_length]
        exchange_code = f"{prefix}{random_code}"
        
        # Save user with generated exchange code
        user = serializer.save(exchange_code=exchange_code)
        
        # Log security event
        SecurityEvent.log_event(
            event_type=1,  # Login
            actor_token=user.client_token,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            details={'action': 'user_created'}
        )

class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class SecurityEventListView(generics.ListAPIView):
    serializer_class = SecurityEventSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        # Only show events for the current user unless admin
        if self.request.user.is_staff:
            return SecurityEvent.objects.all()
        return SecurityEvent.objects.filter(actor_token=self.request.user.client_token)