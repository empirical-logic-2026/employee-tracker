from django.urls import path

from employees.views import (
    EmployeeDetailView,
    EmployeeListCreateView,
    EmployeeLoginView,
    EmployeeProfileView,
)

app_name = 'employees'

urlpatterns = [
    path('auth/login/', EmployeeLoginView.as_view(), name='employee-login'),
    path('me/', EmployeeProfileView.as_view(), name='employee-profile'),
    path('', EmployeeListCreateView.as_view(), name='employee-list'),
    path('<int:pk>/', EmployeeDetailView.as_view(), name='employee-detail'),
]
