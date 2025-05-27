from django.urls import path
from .views import (
    UserCreateView, UserDetailView, 
    SecurityEventListView, LoginView,
    SecurityQuestionListView, SetupSecurityQuestionView,
    VerifySecurityQuestionView,
    InitiatePasswordResetView, CompletePasswordResetView,
    RecoveryQuestionsView, VerifySecurityQuestionView
)

urlpatterns = [
    # Authentication
    path('register/', UserCreateView.as_view(), name='user-register'),
    path('login/', LoginView.as_view(), name='user-login'),
    
    # User Profile
    path('me/', UserDetailView.as_view(), name='user-detail'),
    
    # Security Features
    path('security-events/', SecurityEventListView.as_view(), name='security-events'),
    
    # Security Questions (Setup/Management)
    path('security-questions/', SecurityQuestionListView.as_view(), name='security-question-list'),
    path('setup-security-question/', SetupSecurityQuestionView.as_view(), name='setup-security-question'),
    path('verify-security-question/', VerifySecurityQuestionView.as_view(), name='verify-security-question'),
    
    # Password Recovery Flow
    path('recovery/initiate/', InitiatePasswordResetView.as_view(), name='initiate-password-reset'),
    path('recovery/questions/<str:exchange_code>/', RecoveryQuestionsView.as_view(), name='recovery-questions'),
    path('recovery/verify/', VerifySecurityQuestionView.as_view(), name='verify-recovery-questions'),
    path('recovery/complete/', CompletePasswordResetView.as_view(), name='complete-password-reset'),
]