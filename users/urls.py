from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .views import MeAPI, PingAPI, SignupAPI

urlpatterns = [
    path("ping/", PingAPI.as_view()),
    path("signup/", SignupAPI.as_view()),
    path("token/", TokenObtainPairView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("me/", MeAPI.as_view()),
]
