from django.urls import path

from . import views

urlpatterns = [
    path("auth", views.a_sign_in_or_sign_up, name="sign_in_or_sign_up"),
    path("callback", views.a_signin_callback, name="callback"),
    path("token", views.a_get_token, name="get_token"),
    path("refresh", views.a_refresh_token, name="refresh"),
    path("logout", views.a_logout, name="logout"),
]
