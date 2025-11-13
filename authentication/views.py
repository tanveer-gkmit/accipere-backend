from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import status, permissions
from .serializers import EmailTokenObtainPairSerializer , LogoutSerializer, UserProfileSerializer

class EmailTokenObtainPairView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = EmailTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)


class CurrentUserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

