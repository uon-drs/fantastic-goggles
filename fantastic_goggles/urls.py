from django.urls import path

from . import views

urlpatterns = [
    path("signin", views.sign_in_or_sign_up, name="sign_in_or_sign_up"),
    path("callback", views.signin_callback, name="callback"),
]
