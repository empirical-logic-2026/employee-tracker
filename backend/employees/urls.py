from django.urls import path

from employees.views import (
    EmployeeDetailView,
    AdminLeaveListView,
    AdminLeaveReviewView,
    EmployeeLeaveApplyView,
    EmployeeLeaveBalanceView,
    EmployeeLeaveHistoryView,
    EmployeeListCreateView,
    EmployeeLoginView,
    EmployeeProfileView,
    EmployeeAssetDetailView,
EmployeeAssetListCreateView,
EmployeeMyAssetsView,
EmployeeAssetDetailView,
EmployeeAssetListCreateView,
)


app_name = 'employees'

urlpatterns = [
    path('auth/login/', EmployeeLoginView.as_view(), name='employee-login'),
    path('me/', EmployeeProfileView.as_view(), name='employee-profile'),
    path('leave/balance/', EmployeeLeaveBalanceView.as_view(), name='leave-balance'),
    path('leave/history/', EmployeeLeaveHistoryView.as_view(), name='leave-history'),
    path('leave/apply/', EmployeeLeaveApplyView.as_view(), name='leave-apply'),
    path('admin/leaves/', AdminLeaveListView.as_view(), name='admin-leave-list'),
    path(
        'admin/leaves/<int:pk>/review/',
        AdminLeaveReviewView.as_view(),
        name='admin-leave-review',
    ),
    path('', EmployeeListCreateView.as_view(), name='employee-list'),
    path('<int:pk>/', EmployeeDetailView.as_view(), name='employee-detail'),
    path('assets/', EmployeeAssetListCreateView.as_view(), name='asset-list'),
path('assets/<int:pk>/', EmployeeAssetDetailView.as_view(), name='asset-detail'),
path('me/assets/', EmployeeMyAssetsView.as_view(), name='my-assets'),

]
