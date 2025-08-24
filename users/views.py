from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import SignupSerializer, UserSerializer


class PingAPI(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"status": "ok"}, status=200)


class SignupAPI(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = SignupSerializer(data=request.data)
        if ser.is_valid():
            user = ser.save()
            return Response(
                {"message": "signed_up", "username": user.username}, status=201
            )
        return Response(ser.errors, status=400)


class MeAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data, status=200)
