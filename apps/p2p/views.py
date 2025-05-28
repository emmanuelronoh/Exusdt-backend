from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import P2PListing, P2PTrade
from .serializers import P2PListingSerializer, P2PTradeSerializer
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from rest_framework import serializers
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
        # Validate required fields first
        required_fields = ['escrow_address', 'usdt_amount', 'fiat_price', 'payment_method']
        for field in required_fields:
            if field not in serializer.validated_data:
                raise serializers.ValidationError({field: "This field is required"})

        # Generate seller token
        client_token = self.request.user.client_token
        hmac_key = settings.XUSDT_SETTINGS['USER_TOKEN_HMAC_KEY'].encode()
        seller_token = hmac.new(hmac_key, client_token.encode(), hashlib.sha256).hexdigest()
        
        # Save with additional data
        serializer.save(
            seller_token=seller_token,
            status=1  # Active
        )

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
        # Validate the listing first
        listing = serializer.validated_data['listing']
        
        # Prevent users from trading with themselves
        client_token = self.request.user.client_token
        hmac_key = settings.XUSDT_SETTINGS['USER_TOKEN_HMAC_KEY'].encode()
        user_token = hmac.new(hmac_key, client_token.encode(), hashlib.sha256).hexdigest()
        
        if user_token == listing.seller_token:
            raise serializers.ValidationError({
                'listing': 'You cannot create a trade with your own listing'
            })

        # Check if listing is active
        if listing.status != 1 or listing.expires_at < timezone.now():
            raise serializers.ValidationError({
                'listing': 'This listing is not available for trading'
            })

        # Generate buyer token
        buyer_token = user_token
        
        # Create and save the trade
        trade = serializer.save(
            buyer_token=buyer_token,
            seller_token=listing.seller_token
        )
        
        # Calculate and save fee
        trade.calculate_fee()
        trade.save()

        # Update listing status if needed
        if listing.status == 1:  # Active
            listing.status = 3   # Reserved
            listing.save()

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