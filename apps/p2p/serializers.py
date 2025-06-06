from rest_framework import serializers
from .models import P2PListing, P2PTrade


class P2PListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = P2PListing
        fields = [
            'id',
            'seller_token',
            'crypto_type',
            'crypto_currency',
            'crypto_amount',
            'fiat_currency',
            'fiat_amount',
            'payment_method',
            'description',
            'instructions_enc',
            'status',
            'created_at',
            'expires_at'
        ]
        read_only_fields = [
            'id',
            'seller_token',
            'status',
            'created_at',
            'expires_at'
        ]
        extra_kwargs = {
            'crypto_type': {'required': True},
            'crypto_currency': {'required': True},
            'crypto_amount': {'required': True},
            'fiat_currency': {'required': True},
            'fiat_amount': {'required': True},
            'payment_method': {'required': True},
        }


class P2PTradeCreateSerializer(serializers.ModelSerializer):
    listing = serializers.PrimaryKeyRelatedField(
        queryset=P2PListing.objects.filter(status=1),
        help_text="UUID of the listing being traded"
    )

    class Meta:
        model = P2PTrade
        fields = ['id', 'listing', 'escrow_tx_hash', 'payment_proof_hash']
        extra_kwargs = {
            'escrow_tx_hash': {'required': True},
        }


class P2PTradeSerializer(serializers.ModelSerializer):
    listing = P2PListingSerializer(read_only=True)
    role = serializers.SerializerMethodField()

    class Meta:
        model = P2PTrade
        fields = [
            'id',
            'listing',
            'escrow_tx_hash',
            'payment_proof_hash',
            'status',
            'fee_amount',
            'created_at',
            'updated_at',
            'completed_at',
            'buyer_token',
            'seller_token',
            'role'
        ]
        read_only_fields = fields

    def get_role(self, obj):
        request = self.context.get('request')
        if request:
            user_token = request.headers.get('X-USER-TOKEN')
            if user_token == obj.buyer_token:
                return 'buyer'
            elif user_token == obj.seller_token:
                return 'seller'
        return 'unknown'
