from django.urls import path
from .views import (
    P2PListingListView,
    P2PListingDetailView,
    P2PTradeCreateView,
    P2PTradeDetailView
)

urlpatterns = [
    path('listings/', P2PListingListView.as_view(), name='p2p-listing-list'),
    path('listings/<uuid:pk>/', P2PListingDetailView.as_view(), name='p2p-listing-detail'),
    path('trades/', P2PTradeCreateView.as_view(), name='p2p-trade-create'),
    path('trades/<uuid:pk>/', P2PTradeDetailView.as_view(), name='p2p-trade-detail'),
]