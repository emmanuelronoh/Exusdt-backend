from django.urls import path
from .views import (
    EscrowWalletCreateView, 
    EscrowWalletDetailView,
    SystemWalletListView,
    EscrowWalletListView,
    EscrowReleaseView
)

urlpatterns = [
    path('wallets/', EscrowWalletCreateView.as_view(), name='escrow-wallet-create'),
    path('wallets/<uuid:pk>/', EscrowWalletDetailView.as_view(), name='escrow-wallet-detail'),
    path('system-wallets/', SystemWalletListView.as_view(), name='system-wallet-list'),
    path('wallets/list/', EscrowWalletListView.as_view(), name='escrow-wallet-list'),
    path("release/<uuid:escrow_id>/", EscrowReleaseView.as_view(), name="escrow-release"),
]