from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication

from employees.models import Employee
from employees.serializers import EmployeeSerializer


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
