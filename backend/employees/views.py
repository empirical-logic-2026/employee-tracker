from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from employees.models import Employee
from employees.serializers import EmployeeLoginSerializer, EmployeeSerializer


class EmployeeLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get_authenticate_header(self, request):
        return 'Bearer'

    def post(self, request):
        serializer = EmployeeLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh = RefreshToken.for_user(serializer.validated_data['user'])
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


class EmployeeListCreateView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    queryset = Employee.objects.select_related(
        'kyc',
        'bank_details',
        'emergency_contact',
        'education',
        'business_card_details',
        'document_checklist',
        'declaration',
    )
    serializer_class = EmployeeSerializer


class EmployeeDetailView(generics.RetrieveUpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    queryset = Employee.objects.select_related(
        'kyc',
        'bank_details',
        'emergency_contact',
        'education',
        'business_card_details',
        'document_checklist',
        'declaration',
    )
    serializer_class = EmployeeSerializer
    lookup_field = 'pk'
