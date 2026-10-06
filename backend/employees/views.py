from django.db import transaction
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from employees.models import Employee, LeaveApplication
from employees.serializers import (
    EmployeeLoginSerializer,
    EmployeeSerializer,
    LeaveApplicationSerializer,
    LeaveReviewSerializer,
)


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


class EmployeeProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        employee = get_object_or_404(
            Employee.objects.select_related(
                'kyc',
                'bank_details',
                'emergency_contact',
                'education',
                'business_card_details',
                'document_checklist',
                'declaration',
            ),
            user=request.user,
        )
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)


class EmployeeLeaveHistoryView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = LeaveApplicationSerializer

    def get_queryset(self):
        return LeaveApplication.objects.filter(
            employee__user=self.request.user
        ).select_related('employee', 'reviewer')


class EmployeeLeaveApplyView(generics.CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = LeaveApplicationSerializer

    def perform_create(self, serializer):
        employee = get_object_or_404(Employee, user=self.request.user)
        serializer.save(employee=employee)


class EmployeeLeaveBalanceView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        employee = get_object_or_404(Employee, user=request.user)
        applications = LeaveApplication.objects.filter(employee=employee)
        status_totals = {
            row['status']: row
            for row in applications.values('status').annotate(
                applications=Count('pk'),
                days=Sum('number_of_days'),
            )
        }
        statuses = LeaveApplication.Status.values
        by_status = {
            leave_status: {
                'applications': status_totals.get(leave_status, {}).get(
                    'applications', 0
                ),
                'days': status_totals.get(leave_status, {}).get('days') or 0,
            }
            for leave_status in statuses
        }
        by_leave_type = applications.values('leave_type').annotate(
            applications=Count('pk'),
            days=Sum('number_of_days'),
            approved_days=Sum(
                'number_of_days',
                filter=Q(status=LeaveApplication.Status.APPROVED),
            ),
            pending_days=Sum(
                'number_of_days',
                filter=Q(status=LeaveApplication.Status.PENDING),
            ),
        ).order_by('leave_type')

        return Response({
            'application_counts': {
                leave_status: totals['applications']
                for leave_status, totals in by_status.items()
            },
            'day_counts': {
                leave_status: totals['days']
                for leave_status, totals in by_status.items()
            },
            'by_leave_type': [
                {
                    **row,
                    'approved_days': row['approved_days'] or 0,
                    'pending_days': row['pending_days'] or 0,
                }
                for row in by_leave_type
            ],
            'remaining_entitlement': None,
        })


class AdminLeaveListView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    serializer_class = LeaveApplicationSerializer
    queryset = LeaveApplication.objects.select_related('employee', 'reviewer')


class AdminLeaveReviewView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    @transaction.atomic
    def patch(self, request, pk):
        application = get_object_or_404(
            LeaveApplication.objects.select_for_update(),
            pk=pk,
        )
        serializer = LeaveReviewSerializer(
            application,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(
            reviewer=request.user,
            reviewed_date=timezone.now(),
        )
        return Response(LeaveApplicationSerializer(application).data)


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
