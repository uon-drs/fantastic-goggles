from rest_framework.authentication import BaseAuthentication
from rest_framework.request import HttpRequest
from rest_framework.exceptions import AuthenticationFailed
from keycloak import KeycloakOpenID
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth import get_user_model
from django.conf import settings
from jwcrypto.jwt import JWTExpired


class OIDCAuthenticationAsync(BaseAuthentication):
    async def authenticate(self, request: HttpRequest) -> tuple[AbstractBaseUser, None]:
        """Asynchronously authenticate a user using the OIDC protocol.

        Args:
            request (HttpRequest): The request to authenticate.

        Returns:
            tuple[AbstractBaseUser, None]: A tuple with the authenticated user.
        """
        token = request.headers.get("Authorization")
        if token:
            token = token.removeprefix("Bearer ")
        else:
            raise AuthenticationFailed("No Bearer token in request")

        keycloak = KeycloakOpenID(
            server_url=settings.KEYCLOAK_SERVER,
            realm_name=settings.KEYCLOAK_REALM,
            client_id=settings.KEYCLOAK_CLIENT,
        )

        try:
            user_info = await keycloak.a_decode_token(token)
        except JWTExpired:
            raise AuthenticationFailed("Token expired")

        UserModel = get_user_model()

        try:
            user = await UserModel.objects.aget(username=user_info["preferred_username"])
        except UserModel.DoesNotExist:
            raise AuthenticationFailed("User does not exist")

        return (user, None)
