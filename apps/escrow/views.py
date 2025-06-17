from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import EscrowWallet, SystemWallet
from .serializers import EscrowWalletSerializer, SystemWalletSerializer
from django.conf import settings
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .services import release_to, wait_for_deposit
from decimal import Decimal
from .services import create_escrow_wallet
import hmac
import hashlib

class EscrowWalletCreateView(generics.CreateAPIView):
    queryset = EscrowWallet.objects.all()
    serializer_class = EscrowWalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        client_token = self.request.user.client_token
        user_token = EscrowWallet.generate_user_token(client_token)
        
        # Create and save the escrow wallet with all fields at once
        escrow_wallet = create_escrow_wallet()
        escrow_wallet.user_token = user_token
        escrow_wallet.status = 'created'
        escrow_wallet.save()
        
        # Return the created instance through the serializer
        serializer.instance = escrow_wallet

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

class EscrowWalletListView(generics.ListAPIView):
    serializer_class = EscrowWalletSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        client_token = self.request.user.client_token
        user_token = EscrowWallet.generate_user_token(client_token)
        return EscrowWallet.objects.filter(user_token=user_token)

class EscrowFundView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, escrow_id):
        escrow = get_object_or_404(EscrowWallet, id=escrow_id)
        
        # Verify user owns this escrow
        client_token = request.user.client_token
        user_token = EscrowWallet.generate_user_token(client_token)
        if escrow.user_token != user_token:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        
        # Start monitoring for deposit
        try:
            min_amount = Decimal(request.data.get('min_amount', 0))
            wait_for_deposit(escrow, min_amount)
            return Response({"status": "waiting_for_deposit"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class EscrowStatusView(APIView):
    def get(self, request, escrow_id):
        escrow = get_object_or_404(EscrowWallet, id=escrow_id)
        # Return only status or full serialized data based on your needs
        return Response({
            "id": str(escrow.id),
            "status": escrow.status  # assuming you have a `status` field
        }, status=status.HTTP_200_OK)
    
    
class EscrowReleaseView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, escrow_id):
        escrow = get_object_or_404(EscrowWallet, id=escrow_id)
        
        # Verify user owns this escrow
        client_token = request.user.client_token
        user_token = EscrowWallet.generate_user_token(client_token)
        if escrow.user_token != user_token:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        
        if escrow.status != "funded":
            return Response(
                {"error": "Escrow not in fundable state"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not escrow.buyer_address:
            return Response(
                {"error": "Buyer address not set"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            tx_hash = release_to(
                buyer_addr=escrow.buyer_address,
                wallet=escrow,
                amount=escrow.amount,
                fee=Decimal(settings.ESCROW_FEE_PERCENT) * escrow.amount
            )
            
            return Response(
                {"tx_hash": tx_hash, "status": "released"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": f"Release failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class EscrowDisputeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, escrow_id):
        escrow = get_object_or_404(EscrowWallet, id=escrow_id)
        
        # Verify user owns this escrow
        client_token = request.user.client_token
        user_token = EscrowWallet.generate_user_token(client_token)
        if escrow.user_token != user_token:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        
        if escrow.status != "funded":
            return Response(
                {"error": "Only funded escrows can be disputed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        escrow.status = "disputed"
        escrow.save(update_fields=["status"])
        
        # Here you would typically notify admins via email or other channel
        # and potentially freeze the funds
        
        return Response(
            {"status": "disputed", "message": "Dispute opened successfully"},
            status=status.HTTP_200_OK
        )

class EscrowUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def patch(self, request, escrow_id):
        escrow = get_object_or_404(EscrowWallet, id=escrow_id)
        
        # Verify user owns this escrow
        client_token = request.user.client_token
        user_token = EscrowWallet.generate_user_token(client_token)
        if escrow.user_token != user_token:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        
        if escrow.status != "created":
            return Response(
                {"error": "Can only update escrow in created state"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update buyer/seller addresses
        buyer_address = request.data.get('buyer_address')
        seller_address = request.data.get('seller_address')
        
        if buyer_address:
            escrow.buyer_address = buyer_address
        if seller_address:
            escrow.seller_address = seller_address
        
        escrow.save(update_fields=["buyer_address", "seller_address"])
        
        return Response(
            EscrowWalletSerializer(escrow).data,
            status=status.HTTP_200_OK
        )