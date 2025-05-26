from rest_framework import serializers
from .models import EscrowWallet, SystemWallet

class EscrowWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = EscrowWallet
        fields = ['address', 'balance_commitment', 'created_at', 'last_used']
        read_only_fields = fields

class SystemWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemWallet
        fields = ['address', 'current_balance', 'collected_fees', 'last_swept_at']
        read_only_fields = fields