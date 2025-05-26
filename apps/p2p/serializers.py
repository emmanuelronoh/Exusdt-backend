from rest_framework import serializers
from .models import P2PListing, P2PTrade
from django.conf import settings

class P2PListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = P2PListing
        fields = [
            'id', 'usdt_amount', 'fiat_price', 'payment_method', 
            'status', 'created_at', 'expires_at'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'expires_at']

class P2PTradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = P2PTrade
        fields = [
            'id', 'listing', 'escrow_tx_hash', 'payment_proof_hash',
            'status', 'fee_amount', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'fee_amount', 'created_at', 'updated_at']