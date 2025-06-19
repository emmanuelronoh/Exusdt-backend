from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import (
    SwapToken, SwapRoute, SwapQuote, SwapTransaction,
    SwapAllowance, SwapPrice, MarketStats
)
from .serializers import (
    TokenSerializer, RouteSerializer, QuoteSerializer,
    TransactionSerializer, AllowanceSerializer,
    PriceSerializer, MarketStatsSerializer
)
import uuid
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal
from django.db.models import Q

class TokenListView(APIView):
    def get(self, request):
        tokens = SwapToken.objects.filter(is_active=True)
        serializer = TokenSerializer(tokens, many=True)
        return Response(serializer.data)

class RouteListView(APIView):
    def get(self, request):
        token_in = request.query_params.get('token_in')
        token_out = request.query_params.get('token_out')
        
        routes = SwapRoute.objects.filter(is_active=True)
        
        if token_in:
            routes = routes.filter(token_in__symbol=token_in)
        if token_out:
            routes = routes.filter(token_out__symbol=token_out)
            
        serializer = RouteSerializer(routes, many=True)
        return Response(serializer.data)

class QuoteCreateView(APIView):
    def post(self, request):
        # Validate input
        token_in_symbol = request.data.get('token_in')
        token_out_symbol = request.data.get('token_out')
        amount_in = request.data.get('amount_in')
        
        try:
            token_in = SwapToken.objects.get(symbol=token_in_symbol, is_active=True)
            token_out = SwapToken.objects.get(symbol=token_out_symbol, is_active=True)
            amount_in = Decimal(amount_in)
            
            # Check if route exists
            route = SwapRoute.objects.filter(
                token_in=token_in,
                token_out=token_out,
                is_active=True,
                min_amount_in__lte=amount_in,
                max_amount_in__gte=amount_in
            ).first()
            
            if not route:
                return Response(
                    {'error': 'No available route for this swap'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Calculate swap (simplified - in real app use price oracles)
            # This is where you'd integrate with actual swap services
            rate = Decimal('1.0')  # Simplified - get actual rate from oracle
            amount_out = amount_in * rate * (1 - route.fee_percentage / 100)
            fee_amount = amount_in * route.fee_percentage / 100
            
            # Create and save quote
            quote = SwapQuote.objects.create(
                token_in=token_in,
                token_out=token_out,
                amount_in=amount_in,
                amount_out=amount_out,
                rate=rate,
                fee_amount=fee_amount,
                valid_until=timezone.now() + timedelta(minutes=5)
            )
            
            serializer = QuoteSerializer(quote)
            return Response(serializer.data)
            
        except SwapToken.DoesNotExist:
            return Response(
                {'error': 'Invalid token symbol'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid amount'},
                status=status.HTTP_400_BAD_REQUEST
            )

class ExecuteSwapView(APIView):
    def post(self, request):
        quote_id = request.data.get('quote_id')
        from_address = request.data.get('from_address')
        to_address = request.data.get('to_address')
        user_token = request.headers.get('X-User-Token')  # Get from auth
        
        try:
            quote = SwapQuote.objects.get(id=quote_id, valid_until__gte=timezone.now())
            
            # Create swap transaction
            swap = SwapTransaction.objects.create(
                user_token=user_token,
                quote=quote,
                from_address=from_address,
                to_address=to_address,
                status='pending'
            )
            
            # In a real app, here you'd interact with blockchain
            # For now, we'll simulate success
            swap.status = 'completed'
            swap.executed_at = timezone.now()
            swap.completed_at = timezone.now()
            swap.save()
            
            serializer = TransactionSerializer(swap)
            return Response(serializer.data)
            
        except SwapQuote.DoesNotExist:
            return Response(
                {'error': 'Invalid or expired quote'},
                status=status.HTTP_400_BAD_REQUEST
            )

class SwapStatusView(APIView):
    def get(self, request, tx_id):
        try:
            swap = SwapTransaction.objects.get(id=tx_id)
            serializer = TransactionSerializer(swap)
            return Response(serializer.data)
        except SwapTransaction.DoesNotExist:
            return Response(
                {'error': 'Swap not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class SwapHistoryView(APIView):
    def get(self, request):
        user_token = request.headers.get('X-User-Token')
        swaps = SwapTransaction.objects.filter(user_token=user_token).order_by('-created_at')
        serializer = TransactionSerializer(swaps, many=True)
        return Response(serializer.data)

class PriceListView(APIView):
    def get(self, request):
        token = request.query_params.get('token')
        prices = SwapPrice.objects.all()
        
        if token:
            prices = prices.filter(token__symbol=token)
            
        prices = prices.order_by('-timestamp')[:100]  # Limit to 100 most recent
        serializer = PriceSerializer(prices, many=True)
        return Response(serializer.data)

class MarketStatsView(APIView):
    def get(self, request):
        pair = request.query_params.get('pair')
        stats = MarketStats.objects.all()
        
        if pair:
            stats = stats.filter(token_pair=pair)
            
        serializer = MarketStatsSerializer(stats, many=True)
        return Response(serializer.data)

class AllowanceView(APIView):
    def get(self, request):
        user_token = request.headers.get('X-User-Token')
        token = request.query_params.get('token')
        
        allowances = SwapAllowance.objects.filter(user_token=user_token)
        
        if token:
            allowances = allowances.filter(token__symbol=token)
            
        serializer = AllowanceSerializer(allowances, many=True)
        return Response(serializer.data)

    def post(self, request):
        user_token = request.headers.get('X-User-Token')
        token_symbol = request.data.get('token')
        contract_address = request.data.get('contract_address')
        amount = request.data.get('amount')
        
        try:
            token = SwapToken.objects.get(symbol=token_symbol)
            amount = Decimal(amount)
            
            # Update or create allowance
            allowance, created = SwapAllowance.objects.update_or_create(
                user_token=user_token,
                token=token,
                contract_address=contract_address,
                defaults={'allowance_amount': amount}
            )
            
            serializer = AllowanceSerializer(allowance)
            return Response(serializer.data)
            
        except SwapToken.DoesNotExist:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid amount'},
                status=status.HTTP_400_BAD_REQUEST
            )