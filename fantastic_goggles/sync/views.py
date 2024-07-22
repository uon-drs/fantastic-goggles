import base64
import uuid
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse
from keycloak import KeycloakAuthenticationError, KeycloakOpenID, KeycloakPostError
from rest_framework.response import Response
from rest_framework.request import Request, HttpRequest
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotAuthenticated
from jwcrypto.jwt import JWTExpired


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
    redirect_uri = request.build_absolute_uri(reverse("callback"))
    url = keycloak.auth_url(redirect_uri, scope="openid", state=str(uuid.uuid4()))
    return redirect(url)


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
            redirect_uri = request.build_absolute_uri(reverse("callback"))
            user_token = keycloak.token(
                code=code,
                grant_type=["authorization_code"],
                redirect_uri=redirect_uri,
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


@api_view(["POST"])
def get_token(request: Request | HttpRequest) -> Response:
    """Get user tokens from Keycloak.

    Args:
        request (HttpRequest): The request to the server

    Returns:
        Response: The response containing the tokens and status code
    """
    keycloak = KeycloakOpenID(
        server_url=settings.KEYCLOAK_SERVER,
        realm_name=settings.KEYCLOAK_REALM,
        client_id=settings.KEYCLOAK_CLIENT,
    )
    auth = request.headers.get("Authorization")
    if not auth:
        return Response(
            data={"detail": "Request did not contain the Authorization header"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        credentials = auth.removeprefix("Basic ")
        decoded_credentials = base64.b64decode(credentials)
        username, password = decoded_credentials.decode().split(":")
        result = keycloak.token(username=username, password=password)
        return Response(data=result, status=status.HTTP_200_OK)

    except ValueError:
        return Response(
            data={
                "detail": "The Authorization header is incorrect. This endpoint requires Basic Authorization"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    except KeycloakAuthenticationError:
        return Response(
            data={"detail": "User credentials are invalid"},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    except Exception:
        return Response(
            data={"detail": "Unable to request auth token from OIDC provider"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
def refresh_token(request: Request | HttpRequest) -> Response:
    """Refresh the user tokens.

    Args:
        request (HttpRequest): The request to the server

    Returns:
        Response: The response containing the new tokens and status code
    """
    keycloak = KeycloakOpenID(
        server_url=settings.KEYCLOAK_SERVER,
        realm_name=settings.KEYCLOAK_REALM,
        client_id=settings.KEYCLOAK_CLIENT,
    )

    if refresh := request.data.get("refresh_token"):
        try:
            new_token = keycloak.refresh_token(refresh_token=refresh)
            return Response(data=new_token, status=status.HTTP_200_OK)
        except KeycloakPostError:
            return Response(
                data={"detail": "Invalid refresh token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                data={"detail": "Unable to refresh the user token"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return Response(
        data={"detail": "No refresh token in body"}, status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["POST"])
def logout(request: Request | HttpRequest) -> Response:
    """Log the user out.

    Args:
        request (HttpRequest): The request to the server

    Returns:
        Response: The response containing the status code only
    """
    keycloak = KeycloakOpenID(
        server_url=settings.KEYCLOAK_SERVER,
        realm_name=settings.KEYCLOAK_REALM,
        client_id=settings.KEYCLOAK_CLIENT,
    )

    if refresh := request.data.get("refresh_token"):
        try:
            keycloak.logout(refresh_token=refresh)
            return Response(data=None, status=status.HTTP_204_NO_CONTENT)
        except KeycloakPostError:
            return Response(
                data={"detail": "Invalid refresh token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                data={"detail": "Unable to logout"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return Response(
        data={"detail": "No refresh token in body"}, status=status.HTTP_400_BAD_REQUEST
    )
