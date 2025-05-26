from rest_framework import serializers
from .models import AnonymousUser, SecurityEvent
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnonymousUser
        fields = ['exchange_code', 'trust_score', 'last_active', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True},
            'exchange_code': {'read_only': True},
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super().create(validated_data)

class SecurityEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityEvent
        fields = ['event_type', 'created_at']
        read_only_fields = fields