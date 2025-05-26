from rest_framework import authentication, exceptions
from django.conf import settings
from datetime import timezone
from .models import AnonymousUser


class ClientTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        client_token = request.headers.get('X-Client-Token')
        if not client_token:
            return None

        try:
            user = AnonymousUser.objects.get(client_token=client_token)
            user.last_active = timezone.now()
            user.save()
        except AnonymousUser.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid client token')

        return (user, None)