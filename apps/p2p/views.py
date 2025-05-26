from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import P2PListing, P2PTrade
from .serializers import P2PListingSerializer, P2PTradeSerializer
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
import hmac
import hashlib

class P2PListingListView(generics.ListCreateAPIView):
    serializer_class = P2PListingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return P2PListing.objects.filter(
            status=1,  # Active
            expires_at__gt=timezone.now()
        ).order_by('-created_at')

    def perform_create(self, serializer):
        client_token = self.request.user.client_token
        hmac_key = settings.XUSDT_SETTINGS['USER_TOKEN_HMAC_KEY'].encode()
        seller_token = hmac.new(hmac_key, client_token.encode(), hashlib.sha256).hexdigest()
        serializer.save(seller_token=seller_token)

class P2PListingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = P2PListingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return P2PListing.objects.filter(expires_at__gt=timezone.now())

class P2PTradeCreateView(generics.CreateAPIView):
    queryset = P2PTrade.objects.all()
    serializer_class = P2PTradeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        client_token = self.request.user.client_token
        hmac_key = settings.XUSDT_SETTINGS['USER_TOKEN_HMAC_KEY'].encode()
        buyer_token = hmac.new(hmac_key, client_token.encode(), hashlib.sha256).hexdigest()
        trade = serializer.save(buyer_token=buyer_token)
        trade.calculate_fee()
        trade.save()

class P2PTradeDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = P2PTradeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        client_token = self.request.user.client_token
        hmac_key = settings.XUSDT_SETTINGS['USER_TOKEN_HMAC_KEY'].encode()
        user_token = hmac.new(hmac_key, client_token.encode(), hashlib.sha256).hexdigest()
        return P2PTrade.objects.filter(
            Q(buyer_token=user_token) | 
            Q(seller_token=user_token)
        )