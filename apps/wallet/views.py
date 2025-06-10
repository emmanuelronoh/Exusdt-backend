from rest_framework import viewsets, generics
from .models import Balance, Transaction, Currency
from .serializers import BalanceSerializer, TransactionSerializer, CurrencySerializer
from rest_framework.decorators import action
from rest_framework.response import Response

class BalanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Balance.objects.all()
    serializer_class = BalanceSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        transaction = self.get_object()
        transaction.status = 'cancelled'
        transaction.save()
        return Response({'status': 'cancelled'})

class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

# You can create additional views for:
# - deposit-address
# - withdrawal-limits
# - portfolio-summary
# - settings
# - staking
# - transfer
# - exchange-rates
