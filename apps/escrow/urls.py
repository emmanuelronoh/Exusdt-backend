from django.urls import path
from .views import (
    EscrowWalletCreateView, 
    EscrowWalletDetailView,
    SystemWalletListView,
    EscrowWalletListView,
    EscrowReleaseView,
    EscrowFundView,
    EscrowDisputeView,
    EscrowUpdateView,
)

urlpatterns = [
    path('api/escrow/wallets/', EscrowWalletCreateView.as_view(), name='escrow-wallet-create'),
    path('api/escrow/wallets/<uuid:pk>/', EscrowWalletDetailView.as_view(), name='escrow-wallet-detail'),
    path('api/escrow/system-wallets/', SystemWalletListView.as_view(), name='system-wallet-list'),
    path('api/escrow/wallets/list/', EscrowWalletListView.as_view(), name='escrow-wallet-list'),
    path('api/escrow/fund/<uuid:escrow_id>/', EscrowFundView.as_view(), name='escrow-fund'),
    path('api/escrow/release/<uuid:escrow_id>/', EscrowReleaseView.as_view(), name='escrow-release'),
    path('api/escrow/dispute/<uuid:escrow_id>/', EscrowDisputeView.as_view(), name='escrow-dispute'),
    path('api/escrow/update/<uuid:escrow_id>/', EscrowUpdateView.as_view(), name='escrow-update'),
]