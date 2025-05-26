from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import TradeDispute
from .serializers import TradeDisputeSerializer
from django.conf import settings
from django.db.models import Q
import hmac
import hashlib

class TradeDisputeCreateView(generics.CreateAPIView):
    queryset = TradeDispute.objects.all()
    serializer_class = TradeDisputeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        client_token = self.request.user.client_token
        hmac_key = settings.XUSDT_SETTINGS['USER_TOKEN_HMAC_KEY'].encode()
        initiator_token = hmac.new(hmac_key, client_token.encode(), hashlib.sha256).hexdigest()
        serializer.save(initiator_token=initiator_token)

class TradeDisputeDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = TradeDisputeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        client_token = self.request.user.client_token
        hmac_key = settings.XUSDT_SETTINGS['USER_TOKEN_HMAC_KEY'].encode()
        user_token = hmac.new(hmac_key, client_token.encode(), hashlib.sha256).hexdigest()
        
        return TradeDispute.objects.filter(
            Q(trade__buyer_token=user_token) |
            Q(trade__seller_token=user_token) |
            Q(initiator_token=user_token)
        )

class TradeDisputeListView(generics.ListAPIView):
    serializer_class = TradeDisputeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        client_token = self.request.user.client_token
        hmac_key = settings.XUSDT_SETTINGS['USER_TOKEN_HMAC_KEY'].encode()
        user_token = hmac.new(hmac_key, client_token.encode(), hashlib.sha256).hexdigest()
        
        return TradeDispute.objects.filter(
            Q(trade__buyer_token=user_token) |
            Q(trade__seller_token=user_token) |
            Q(initiator_token=user_token)
        ).order_by('-created_at')