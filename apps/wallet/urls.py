from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BalanceViewSet, TransactionViewSet, CurrencyViewSet

router = DefaultRouter()
router.register(r'balances', BalanceViewSet, basename='balance')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'supported-currencies', CurrencyViewSet, basename='currency')

urlpatterns = [
    path('', include(router.urls)),
]
