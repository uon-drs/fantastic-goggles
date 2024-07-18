import base64
import uuid
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse
from keycloak import KeycloakOpenID, KeycloakAuthenticationError, KeycloakPostError
from rest_framework.response import Response
from rest_framework.request import Request, HttpRequest
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotAuthenticated
from adrf.decorators import api_view as async_api_view
from jwcrypto.jwt import JWTExpired


@async_api_view(["GET"])
async def a_sign_in_or_sign_up(request: Request | HttpRequest) -> HttpResponseRedirect:
    """Asynchronously sign in or user or sign them up.

    Args:
        request (Request | HttpRequest): The request to the server

    Returns:
        HttpResponseRedirect: Redirect the request to the sign in/sign up page
    """
    keycloak = KeycloakOpenID(
        server_url=settings.KEYCLOAK_SERVER,
        realm_name=settings.KEYCLOAK_REALM,
        client_id=settings.KEYCLOAK_CLIENT,
    )
    callback_url = settings.KEYCLOAK_REDIRECT_URI
    url = await keycloak.a_auth_url(
        callback_url, scope="openid", state=str(uuid.uuid4())
    )
    return redirect(url)


@api_view(["GET"])
def sign_in_or_sign_up(request: Request | HttpRequest) -> HttpResponseRedirect:
    """Sign in or user or sign them up.

    Args:
        request (Request | HttpRequest): The request to the server

    Returns:
        HttpResponseRedirect: Redirect the request to the sign in/sign up page
    """
    keycloak = KeycloakOpenID(
        server_url=settings.KEYCLOAK_SERVER,
        realm_name=settings.KEYCLOAK_REALM,
        client_id=settings.KEYCLOAK_CLIENT,
    )
    callback_url = settings.KEYCLOAK_REDIRECT_URI
    url = keycloak.auth_url(callback_url, scope="openid", state=str(uuid.uuid4()))
    return redirect(url)


@async_api_view(["GET"])
async def a_signin_callback(request: Request | HttpRequest) -> HttpResponseRedirect:
    """Asynchronous callback for signing in.

    Args:
        request (Request | HttpRequest): The request to the server

    Raises:
        NotAuthenticated: Could not authenticate the user

    Returns:
        HttpResponseRedirect: Redirect the request to the post-auth page
    """
    keycloak = KeycloakOpenID(
        server_url=settings.KEYCLOAK_SERVER,
        realm_name=settings.KEYCLOAK_REALM,
        client_id=settings.KEYCLOAK_CLIENT,
    )
    if code := request.query_params.get("code"):
        try:
            callback_url = settings.KEYCLOAK_REDIRECT_URI
            user_token = await keycloak.a_token(
                code=code,
                grant_type=["authorization_code"],
                redirect_uri=callback_url,
            )
            user_info = await keycloak.a_decode_token(user_token["access_token"])
            UserModel = get_user_model()
            await UserModel.objects.aget_or_create(
                username=user_info["preferred_username"], email=user_info["email"]
            )

        except JWTExpired:
            raise NotAuthenticated("Token expired")
        except KeycloakPostError:
            return Response(
                data={"detail": "Invalid token call"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    return redirect(settings.KEYCLOAK_POST_AUTH_REDIRECT_URI)


@api_view(["GET"])
def signin_callback(request: Request | HttpRequest) -> HttpResponseRedirect:
    """Callback for signing in.

    Args:
        request (Request | HttpRequest): The request to the server

    Raises:
        NotAuthenticated: Could not authenticate the user

    Returns:
        HttpResponseRedirect: Redirect the request to the post-auth page
    """
    keycloak = KeycloakOpenID(
        server_url=settings.KEYCLOAK_SERVER,
        realm_name=settings.KEYCLOAK_REALM,
        client_id=settings.KEYCLOAK_CLIENT,
    )
    if code := request.query_params.get("code"):
        try:
            callback_url = settings.KEYCLOAK_REDIRECT_URI
            user_token = keycloak.token(
                code=code,
                grant_type=["authorization_code"],
                redirect_uri=callback_url,
            )
            user_info = keycloak.decode_token(user_token["access_token"])
            UserModel = get_user_model()
            UserModel.objects.get_or_create(
                username=user_info["preferred_username"], email=user_info["email"]
            )

        except JWTExpired:
            raise NotAuthenticated("Token expired")
        except KeycloakPostError:
            return Response(
                data={"detail": "Invalid token call"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    return redirect(settings.KEYCLOAK_POST_AUTH_REDIRECT_URI)
