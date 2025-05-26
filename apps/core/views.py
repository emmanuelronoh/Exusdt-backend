import uuid

from django.conf import settings
from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
import random

from .models import AnonymousUser, SecurityEvent
from .serializers import UserSerializer, SecurityEventSerializer, LoginSerializer


# ---------------------------------------------------------------------------
# User – Create + Detail
# ---------------------------------------------------------------------------

class UserCreateView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Creates an anonymous user and returns:
        {
          "exchange_code": "EX-12345",
          "trust_score": 100,
          "last_active": null,
          "created_at": "2025-05-26T23:01:05Z",
          "client_token": "..."
        }
    """

    queryset = AnonymousUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    # ------------------------------------------------------------------ #
    # Helpers                                                            #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _generate_exchange_code() -> str:
        prefix = settings.XUSDT_SETTINGS["EXCHANGE_CODE_PREFIX"]  # e.g. "EX-"
        total  = settings.XUSDT_SETTINGS["EXCHANGE_CODE_LENGTH"]  # e.g. 8

        if total <= len(prefix):
            raise ValueError(
                "EXCHANGE_CODE_LENGTH must be greater than the length of "
                "EXCHANGE_CODE_PREFIX"
            )

        random_len = total - len(prefix)
        digits     = "".join(random.choices("0123456789", k=random_len))
        return f"{prefix}{digits}"

    # ------------------------------------------------------------------ #
    # Main hook                                                          #
    # ------------------------------------------------------------------ #
    def perform_create(self, serializer):
        # --- 1. generate a UNIQUE exchange code ------------------------
        max_attempts = 5
        for _ in range(max_attempts):
            code = self._generate_exchange_code()
            if not AnonymousUser.objects.filter(exchange_code=code).exists():
                break
        else:
            raise RuntimeError("Could not generate a unique exchange_code")

        # --- 2. save user ---------------------------------------------
        user: AnonymousUser = serializer.save(exchange_code=code)

        # --- 3. log security event ------------------------------------
        SecurityEvent.log_event(
            event_type=1,  # Login / registration
            actor_token=user.client_token,
            ip_address=self.request.META.get("REMOTE_ADDR", ""),
            details={"action": "user_created"},
        )


class UserDetailView(generics.RetrieveAPIView):
    """
    GET /api/auth/me/
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# ---------------------------------------------------------------------------
# SecurityEvent list (admin-only)
# ---------------------------------------------------------------------------

class SecurityEventListView(generics.ListAPIView):
    """
    GET /api/security-events/
    """

    serializer_class = SecurityEventSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        if self.request.user.is_staff:
            return SecurityEvent.objects.all()
        return SecurityEvent.objects.filter(actor_token=self.request.user.client_token)

class LoginView(generics.GenericAPIView):
    """
    POST /api/auth/login/
    """
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        # log security event
        SecurityEvent.log_event(
            event_type=1,
            actor_token=user.client_token,
            ip_address=request.META.get("REMOTE_ADDR", ""),
            details={"action": "login"},
        )

        # return token & minimal public info
        return Response(
            {
                "exchange_code": user.exchange_code,
                "client_token": user.client_token,
                "trust_score": user.trust_score,
            },
            status=status.HTTP_200_OK,
        )