from django.urls import path

from . import views

urlpatterns = [
    path("signin", views.a_sign_in_or_sign_up, name="sign_in_or_sign_up"),
    path("callback", views.a_signin_callback, name="callback"),
]
