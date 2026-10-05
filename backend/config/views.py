from django.contrib.auth import authenticate, logout
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken


class CsrfTokenView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'csrfToken': get_token(request)})


class AdminLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        if not isinstance(request.data, dict):
            return Response(
                {'detail': 'A JSON object with username and password is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        username = request.data.get('username')
        password = request.data.get('password')
        if not isinstance(username, str) or not username:
            return Response(
                {'username': 'This field is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not isinstance(password, str) or not password:
            return Response(
                {'password': 'This field is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=username, password=password)
        if user is None or not user.is_staff:
            return Response(
                {'detail': 'Invalid admin credentials.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


@method_decorator(csrf_protect, name='dispatch')
class AdminLogoutView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request):
        logout(request)
        return Response({'detail': 'Logout successful.'})


class AdminTestView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response({'detail': 'Admin access granted.'})
