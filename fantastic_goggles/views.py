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
