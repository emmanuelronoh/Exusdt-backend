#core/urls.py
from django.urls import path
from .views import UserCreateView, UserDetailView, SecurityEventListView, LoginView


urlpatterns = [
    path('register/',  UserCreateView.as_view(), name='user-register'),
    path('login/',     LoginView.as_view(),      name='user-login'),   # NEW
    path('me/',        UserDetailView.as_view(), name='user-detail'),
    path('security-events/', SecurityEventListView.as_view(), name='security-events'),
]
