import uuid
from rest_framework import serializers
from .models import AnonymousUser, SecurityEvent
from django.contrib.auth.hashers import make_password



class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model  = AnonymousUser
        fields = [
            'exchange_code', 'password',
            'trust_score', 'last_active',
            'created_at', 'client_token'
        ]
        extra_kwargs = {
            'exchange_code': {'read_only': True},
            'client_token':  {'read_only': True},
        }

    def create(self, validated_data):
        raw_password = validated_data.pop('password')

        user = AnonymousUser(**validated_data)

        user.set_password(raw_password)

        user.save()

        return user


class SecurityEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityEvent
        fields = ['event_type', 'created_at']
        read_only_fields = fields

class LoginSerializer(serializers.Serializer):
    exchange_code = serializers.CharField(max_length=8)
    password      = serializers.CharField(write_only=True)

    def validate(self, attrs):
        exchange_code = attrs.get("exchange_code")
        password      = attrs.get("password")

        try:
            user = AnonymousUser.objects.get(exchange_code=exchange_code)
        except AnonymousUser.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials")

        # rotate salt => new client_token
        user.rotate_session_salt()

        attrs["user"] = user
        return attrs