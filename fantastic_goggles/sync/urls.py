from django.urls import path

from . import views

urlpatterns = [
    path("auth", views.sign_in_or_sign_up, name="sign_in_or_sign_up"),
    path("callback", views.signin_callback, name="callback"),
    path("token", views.get_token, name="get_token"),
]
