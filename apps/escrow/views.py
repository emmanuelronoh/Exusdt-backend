from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import EscrowWallet, SystemWallet
from .serializers import EscrowWalletSerializer, SystemWalletSerializer
from django.conf import settings
import hmac
import hashlib

class EscrowWalletCreateView(generics.CreateAPIView):
    queryset = EscrowWallet.objects.all()
    serializer_class = EscrowWalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        client_token = self.request.user.client_token
        user_token = EscrowWallet.generate_user_token(client_token)
        serializer.save(user_token=user_token)

class EscrowWalletDetailView(generics.RetrieveAPIView):
    serializer_class = EscrowWalletSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        client_token = self.request.user.client_token
        user_token = EscrowWallet.generate_user_token(client_token)
        return EscrowWallet.objects.filter(user_token=user_token)

class SystemWalletListView(generics.ListAPIView):
    queryset = SystemWallet.objects.all()
    serializer_class = SystemWalletSerializer
    permission_classes = [permissions.IsAdminUser]