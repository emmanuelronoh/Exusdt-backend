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
    EscrowStatusView,
)

urlpatterns = [
    path('wallets/', EscrowWalletCreateView.as_view(), name='escrow-wallet-create'),
    path('wallets/<uuid:pk>/', EscrowWalletDetailView.as_view(), name='escrow-wallet-detail'),
    path('system-wallets/', SystemWalletListView.as_view(), name='system-wallet-list'),
    path('wallets/list/', EscrowWalletListView.as_view(), name='escrow-wallet-list'),
    path('fund/<uuid:escrow_id>/', EscrowFundView.as_view(), name='escrow-fund'),
    path('release/<uuid:escrow_id>/', EscrowReleaseView.as_view(), name='escrow-release'),
    path('dispute/<uuid:escrow_id>/', EscrowDisputeView.as_view(), name='escrow-dispute'),
    path('update/<uuid:escrow_id>/', EscrowUpdateView.as_view(), name='escrow-update'),
    path('status/<uuid:escrow_id>/', EscrowStatusView.as_view(), name='escrow-status'),
]