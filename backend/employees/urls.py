from django.urls import path

from employees.views import EmployeeDetailView, EmployeeListCreateView

app_name = 'employees'

urlpatterns = [
    path('', EmployeeListCreateView.as_view(), name='employee-list'),
    path('<int:pk>/', EmployeeDetailView.as_view(), name='employee-detail'),
]
