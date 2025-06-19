from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import (
    BridgeNetwork, BridgeToken, BridgeTokenNetwork,
    BridgeQuote, BridgeTransaction, BridgeFee, BridgeStats
)
from .serializers import (
    NetworkSerializer, TokenSerializer, TokenNetworkSerializer,
    QuoteSerializer, TransactionSerializer, FeeSerializer, StatsSerializer
)
import uuid
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal
from django.db.models import Q

class NetworkListView(APIView):
    def get(self, request):
        networks = BridgeNetwork.objects.filter(is_active=True)
        serializer = NetworkSerializer(networks, many=True)
        return Response(serializer.data)

class TokenListView(APIView):
    def get(self, request):
        network_id = request.query_params.get('network_id')
        
        tokens = BridgeToken.objects.filter(is_active=True)
        
        if network_id:
            tokens = tokens.filter(
                bridgetokennetwork__network_id=network_id,
                bridgetokennetwork__is_active=True
            ).distinct()
            
        serializer = TokenSerializer(tokens, many=True)
        return Response(serializer.data)

class TokenNetworkListView(APIView):
    def get(self, request, token_id):
        token_networks = BridgeTokenNetwork.objects.filter(
            token_id=token_id,
            is_active=True
        )
        serializer = TokenNetworkSerializer(token_networks, many=True)
        return Response(serializer.data)

class QuoteCreateView(APIView):
    def post(self, request):
        token_symbol = request.data.get('token')
        amount = request.data.get('amount')
        from_network_id = request.data.get('from_network')
        to_network_id = request.data.get('to_network')
        
        try:
            token = BridgeToken.objects.get(symbol=token_symbol, is_active=True)
            amount = Decimal(amount)
            from_network = BridgeNetwork.objects.get(id=from_network_id, is_active=True)
            to_network = BridgeNetwork.objects.get(id=to_network_id, is_active=True)
            
            # Check if token is available on both networks
            token_from = BridgeTokenNetwork.objects.filter(
                token=token,
                network=from_network,
                is_active=True
            ).first()
            
            token_to = BridgeTokenNetwork.objects.filter(
                token=token,
                network=to_network,
                is_active=True
            ).first()
            
            if not token_from or not token_to:
                return Response(
                    {'error': 'Token not available on one or both networks'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check min bridge amount
            if amount < token_from.min_bridge_amount:
                return Response(
                    {'error': f'Amount below minimum {token_from.min_bridge_amount}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get fee (simplified - in real app use more complex calculation)
            fee = BridgeFee.objects.filter(
                from_network=from_network,
                to_network=to_network,
                token=token
            ).first()
            
            if not fee:
                return Response(
                    {'error': 'No available bridge route'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            fee_amount = max(
                amount * fee.fee_percentage / 100,
                fee.min_fee
            )
            
            if fee.max_fee and fee_amount > fee.max_fee:
                fee_amount = fee.max_fee
            
            # Create quote
            quote = BridgeQuote.objects.create(
                token=token,
                amount=amount,
                from_network=from_network,
                to_network=to_network,
                fee_amount=fee_amount,
                estimated_time=30,  # Simplified - get actual estimate
                valid_until=timezone.now() + timedelta(minutes=5)
            )
            
            serializer = QuoteSerializer(quote)
            return Response(serializer.data)
            
        except (BridgeToken.DoesNotExist, BridgeNetwork.DoesNotExist):
            return Response(
                {'error': 'Invalid token or network'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid amount'},
                status=status.HTTP_400_BAD_REQUEST
            )

class InitiateBridgeView(APIView):
    def post(self, request):
        quote_id = request.data.get('quote_id')
        from_address = request.data.get('from_address')
        to_address = request.data.get('to_address')
        user_token = request.headers.get('X-User-Token')  # Get from auth
        
        try:
            quote = BridgeQuote.objects.get(id=quote_id, valid_until__gte=timezone.now())
            
            # Create bridge transaction
            bridge = BridgeTransaction.objects.create(
                user_token=user_token,
                quote=quote,
                from_address=from_address,
                to_address=to_address,
                status='pending'
            )
            
            # In a real app, here you'd interact with blockchain
            # For now, we'll simulate success
            bridge.status = 'completed'
            bridge.completed_at = timezone.now()
            bridge.save()
            
            serializer = TransactionSerializer(bridge)
            return Response(serializer.data)
            
        except BridgeQuote.DoesNotExist:
            return Response(
                {'error': 'Invalid or expired quote'},
                status=status.HTTP_400_BAD_REQUEST
            )

class BridgeStatusView(APIView):
    def get(self, request, id):
        try:
            bridge = BridgeTransaction.objects.get(id=id)
            serializer = TransactionSerializer(bridge)
            return Response(serializer.data)
        except BridgeTransaction.DoesNotExist:
            return Response(
                {'error': 'Bridge not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class BridgeHistoryView(APIView):
    def get(self, request):
        user_token = request.headers.get('X-User-Token')
        bridges = BridgeTransaction.objects.filter(user_token=user_token).order_by('-initiated_at')
        serializer = TransactionSerializer(bridges, many=True)
        return Response(serializer.data)

class EstimateTimeView(APIView):
    def get(self, request):
        from_network_id = request.query_params.get('from_network')
        to_network_id = request.query_params.get('to_network')
        
        try:
            from_network = BridgeNetwork.objects.get(id=from_network_id, is_active=True)
            to_network = BridgeNetwork.objects.get(id=to_network_id, is_active=True)
            
            # Simplified - in real app use historical data
            avg_time = 30  # minutes
            
            return Response({'estimated_time': avg_time})
            
        except BridgeNetwork.DoesNotExist:
            return Response(
                {'error': 'Invalid network'},
                status=status.HTTP_400_BAD_REQUEST
            )

class FeeListView(APIView):
    def get(self, request):
        from_network_id = request.query_params.get('from_network')
        to_network_id = request.query_params.get('to_network')
        token_symbol = request.query_params.get('token')
        
        fees = BridgeFee.objects.all()
        
        if from_network_id:
            fees = fees.filter(from_network_id=from_network_id)
        if to_network_id:
            fees = fees.filter(to_network_id=to_network_id)
        if token_symbol:
            fees = fees.filter(token__symbol=token_symbol)
            
        serializer = FeeSerializer(fees, many=True)
        return Response(serializer.data)

class StatsView(APIView):
    def get(self, request):
        stats = BridgeStats.objects.all()
        serializer = StatsSerializer(stats, many=True)
        return Response(serializer.data)