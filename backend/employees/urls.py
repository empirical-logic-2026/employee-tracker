from django.urls import path

from employees.views import (
    EmployeeDetailView,
    EmployeeListCreateView,
    EmployeeLoginView,
)

app_name = 'employees'

urlpatterns = [
    path('auth/login/', EmployeeLoginView.as_view(), name='employee-login'),
    path('', EmployeeListCreateView.as_view(), name='employee-list'),
    path('<int:pk>/', EmployeeDetailView.as_view(), name='employee-detail'),
]
