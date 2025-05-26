from rest_framework import serializers
from .models import TradeDispute

class TradeDisputeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradeDispute
        fields = [
            'id', 'trade', 'initiator_token', 'evidence_hashes',
            'resolution', 'created_at', 'resolved_at'
        ]
        read_only_fields = ['id', 'created_at', 'resolved_at']