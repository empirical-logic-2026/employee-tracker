from datetime import date

from django.db import IntegrityError, transaction
from django.test import TestCase

from employees.models import Employee, EmployeeBankDetails, EmployeeKYC


class EmployeeModelTests(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(
            full_name='Taylor Employee',
            fathers_spouses_name='Jordan Employee',
            date_of_birth=date(1990, 1, 15),
            gender='Other',
            nationality='Indian',
            personal_mobile_number='9876543210',
            personal_email='taylor@example.com',
            current_address='10 Example Street',
            current_city='Bengaluru',
            current_state='Karnataka',
            current_pin_code='560011',
            permanent_address_same_as_current=True,
            employee_id='EMP-TEST-001',
            date_of_joining=date(2024, 4, 1),
            designation='Analyst',
            department='Finance',
            employment_type='Full-time',
            work_location='Bengaluru',
            reporting_manager='Morgan Manager',
            official_email='taylor@company.example',
        )

    def test_employee_record_is_created(self):
        employee = Employee.objects.get(employee_id='EMP-TEST-001')

        self.assertEqual(employee.pk, self.employee.pk)
        self.assertEqual(employee.full_name, 'Taylor Employee')
        self.assertIsNotNone(employee.created_at)
        self.assertIsNotNone(employee.updated_at)

    def test_employee_id_must_be_unique(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Employee.objects.create(
                    full_name='Another Employee',
                    fathers_spouses_name='Jordan Employee',
                    date_of_birth=date(1992, 3, 5),
                    gender='Other',
                    nationality='Indian',
                    personal_mobile_number='9876543211',
                    personal_email='another@example.com',
                    current_address='20 Example Street',
                    current_city='Bengaluru',
                    current_state='Karnataka',
                    current_pin_code='560012',
                    permanent_address_same_as_current=True,
                    employee_id='EMP-TEST-001',
                    date_of_joining=date(2024, 5, 1),
                    designation='Analyst',
                    department='Finance',
                    employment_type='Full-time',
                    work_location='Bengaluru',
                    reporting_manager='Morgan Manager',
                    official_email='another@company.example',
                )

    def test_employee_kyc_has_one_to_one_relationship(self):
        kyc = EmployeeKYC.objects.create(
            employee=self.employee,
            pan='ABCDE1234F',
            name_as_per_pan='Taylor Employee',
            aadhaar_number='123456789012',
            name_as_per_aadhaar='Taylor Employee',
        )

        self.assertEqual(kyc.employee, self.employee)
        self.assertEqual(self.employee.kyc, kyc)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                EmployeeKYC.objects.create(
                    employee=self.employee,
                    pan='FGHIJ5678K',
                    name_as_per_pan='Taylor Employee',
                    aadhaar_number='234567890123',
                    name_as_per_aadhaar='Taylor Employee',
                )

    def test_employee_bank_details_has_one_to_one_relationship(self):
        bank_details = EmployeeBankDetails.objects.create(
            employee=self.employee,
            account_holder_name='Taylor Employee',
            bank_name='Example Bank',
            branch='Bengaluru',
            account_number='1234567890',
            account_type='Savings',
            ifsc_code='ABCD0123456',
        )

        self.assertEqual(bank_details.employee, self.employee)
        self.assertEqual(self.employee.bank_details, bank_details)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                EmployeeBankDetails.objects.create(
                    employee=self.employee,
                    account_holder_name='Taylor Employee',
                    bank_name='Another Bank',
                    branch='Bengaluru',
                    account_number='0987654321',
                    account_type='Savings',
                    ifsc_code='EFGH0123456',
                )

    def test_employee_can_be_retrieved_with_related_data(self):
        EmployeeKYC.objects.create(
            employee=self.employee,
            pan='ABCDE1234F',
            name_as_per_pan='Taylor Employee',
            aadhaar_number='123456789012',
            name_as_per_aadhaar='Taylor Employee',
        )
        EmployeeBankDetails.objects.create(
            employee=self.employee,
            account_holder_name='Taylor Employee',
            bank_name='Example Bank',
            branch='Bengaluru',
            account_number='1234567890',
            account_type='Savings',
            ifsc_code='ABCD0123456',
        )

        employee = Employee.objects.select_related('kyc', 'bank_details').get(
            employee_id='EMP-TEST-001'
        )

        self.assertEqual(employee.kyc.pan, 'ABCDE1234F')
        self.assertEqual(employee.bank_details.bank_name, 'Example Bank')
