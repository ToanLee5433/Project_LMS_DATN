from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .views import MeAPI, PingAPI, SignupAPI, ChangePasswordAPI

urlpatterns = [
    path("ping/", PingAPI.as_view(), name="ping"),
    path("signup/", SignupAPI.as_view(), name="signup"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeAPI.as_view(), name="me"),
    path("change-password/", ChangePasswordAPI.as_view(), name="change_password"),
]
