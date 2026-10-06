from employees.models import Employee


def authenticate_employee(employee_id, password):
    try:
        employee = Employee.objects.select_related('user').get(
            employee_id=employee_id
        )
    except Employee.DoesNotExist:
        return None

    if employee.user_id is None:
        return None

    user = employee.user
    if not user.is_active or not user.check_password(password):
        return None

    return user