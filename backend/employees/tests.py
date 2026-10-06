from datetime import date

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from employees.models import (
    Employee,
    EmployeeBankDetails,
    EmployeeBusinessCardDetails,
    EmployeeDeclaration,
    EmployeeDocumentChecklist,
    EmployeeEducation,
    EmployeeEmergencyContact,
    EmployeeKYC,
)


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


class EmployeeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        admin_user = get_user_model().objects.create_user(
            username='employee-api-admin',
            password='test-password',
            is_staff=True,
        )
        access_token = RefreshToken.for_user(admin_user).access_token
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        self.list_url = '/api/employees/'
        self.payload = {
            'full_name': 'Taylor Employee',
            'fathers_spouses_name': 'Jordan Employee',
            'date_of_birth': '1990-01-15',
            'gender': 'Other',
            'nationality': 'Indian',
            'personal_mobile_number': '9876543210',
            'personal_email': 'taylor@example.com',
            'current_address': '10 Example Street',
            'current_city': 'Bengaluru',
            'current_state': 'Karnataka',
            'current_pin_code': '560011',
            'permanent_address_same_as_current': True,
            'employee_id': 'EMP-API-001',
            'date_of_joining': '2024-04-01',
            'designation': 'Analyst',
            'department': 'Finance',
            'employment_type': 'Full-time',
            'work_location': 'Bengaluru',
            'reporting_manager': 'Morgan Manager',
            'official_email': 'taylor@company.example',
            'kyc': {
                'pan': 'ABCDE1234F',
                'name_as_per_pan': 'Taylor Employee',
                'aadhaar_number': '123456789012',
                'name_as_per_aadhaar': 'Taylor Employee',
            },
            'bank_details': {
                'account_holder_name': 'Taylor Employee',
                'bank_name': 'Example Bank',
                'branch': 'Bengaluru',
                'account_number': '1234567890',
                'account_type': 'Savings',
                'ifsc_code': 'ABCD0123456',
            },
        }

    def create_employee(self):
        response = self.client.post(self.list_url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        return response

    def test_create_employee_with_nested_related_data(self):
        response = self.create_employee()

        self.assertEqual(response.data['employee_id'], 'EMP-API-001')
        self.assertEqual(response.data['kyc']['pan'], 'ABCDE1234F')
        self.assertEqual(response.data['bank_details']['bank_name'], 'Example Bank')

    def test_retrieve_employee_with_nested_related_data(self):
        created = self.create_employee()

        response = self.client.get(f"{self.list_url}{created.data['id']}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], 'Taylor Employee')
        self.assertEqual(response.data['kyc']['aadhaar_number'], '123456789012')
        self.assertEqual(response.data['bank_details']['ifsc_code'], 'ABCD0123456')

    def test_update_employee(self):
        created = self.create_employee()
        payload = {**self.payload, 'full_name': 'Taylor Updated'}

        response = self.client.put(
            f"{self.list_url}{created.data['id']}/", payload, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['full_name'], 'Taylor Updated')

    def test_partially_update_employee(self):
        created = self.create_employee()

        response = self.client.patch(
            f"{self.list_url}{created.data['id']}/",
            {'department': 'Operations'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['department'], 'Operations')
        self.assertEqual(response.data['full_name'], 'Taylor Employee')

    def test_validation_failure_returns_bad_request(self):
        payload = {**self.payload, 'current_pin_code': '12A'}

        response = self.client.post(self.list_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('current_pin_code', response.data)

    def test_nonexistent_employee_returns_not_found(self):
        response = self.client.get(f'{self.list_url}999999/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_employees(self):
        self.create_employee()

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['employee_id'], 'EMP-API-001')


class EmployeeAuthenticationAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = '/api/employees/auth/login/'
        self.password = 'employee-test-password'
        self.user = get_user_model().objects.create_user(
            username='employee-auth-user',
            password=self.password,
        )
        self.employee = self.create_employee(
            employee_id='EMP-AUTH-001',
            user=self.user,
        )

    def create_employee(self, employee_id, user=None):
        return Employee.objects.create(
            full_name='Taylor Employee',
            fathers_spouses_name='Jordan Employee',
            user=user,
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
            employee_id=employee_id,
            date_of_joining=date(2024, 4, 1),
            designation='Analyst',
            department='Finance',
            employment_type='Full-time',
            work_location='Bengaluru',
            reporting_manager='Morgan Manager',
            official_email='taylor@company.example',
        )

    def login(self, employee_id='EMP-AUTH-001', password=None):
        return self.client.post(
            self.login_url,
            {
                'employee_id': employee_id,
                'password': self.password if password is None else password,
            },
            format='json',
        )

    def test_employee_can_login_and_receive_jwt_tokens(self):
        response = self.login()

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertTrue(response.data['access'])
        self.assertTrue(response.data['refresh'])

    def test_login_rejects_unknown_employee_id(self):
        response = self.login(employee_id='EMP-UNKNOWN')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_rejects_invalid_password(self):
        response = self.login(password='wrong-password')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_rejects_inactive_user(self):
        self.user.is_active = False
        self.user.save(update_fields=['is_active'])

        response = self.login()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_rejects_employee_without_linked_user(self):
        self.employee.user = None
        self.employee.save(update_fields=['user'])

        response = self.login()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class EmployeeProfileAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.profile_url = '/api/employees/me/'
        self.user = get_user_model().objects.create_user(
            username='employee-profile-user',
            password='employee-test-password',
        )
        self.employee = self.create_employee('EMP-PROFILE-001', self.user)
        self.other_user = get_user_model().objects.create_user(
            username='other-employee-profile-user',
            password='employee-test-password',
        )
        self.other_employee = self.create_employee(
            'EMP-PROFILE-002', self.other_user
        )
        access_token = RefreshToken.for_user(self.user).access_token
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

    def create_employee(self, employee_id, user):
        return Employee.objects.create(
            full_name='Taylor Employee',
            fathers_spouses_name='Jordan Employee',
            user=user,
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
            employee_id=employee_id,
            date_of_joining=date(2024, 4, 1),
            designation='Analyst',
            department='Finance',
            employment_type='Full-time',
            work_location='Bengaluru',
            reporting_manager='Morgan Manager',
            official_email=f'{employee_id.lower()}@company.example',
        )

    def test_employee_can_view_own_complete_profile(self):
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
        EmployeeEmergencyContact.objects.create(
            employee=self.employee,
            contact_name='Jordan Employee',
            relationship='Spouse',
            contact_mobile_number='9876543211',
        )
        EmployeeEducation.objects.create(
            employee=self.employee,
            highest_qualification='Bachelors',
        )
        EmployeeBusinessCardDetails.objects.create(employee=self.employee)
        EmployeeDocumentChecklist.objects.create(
            employee=self.employee,
            pan_card_copy='Received',
            aadhaar_card_copy='Received',
            passport_size_photograph='Received',
            cancelled_cheque_bank_letter='Received',
            education_certificates='Received',
        )
        EmployeeDeclaration.objects.create(
            employee=self.employee,
            declaration_confirmed=True,
            date_of_submission=date(2024, 4, 1),
        )

        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.employee.pk)
        self.assertEqual(response.data['employee_id'], 'EMP-PROFILE-001')
        self.assertEqual(response.data['kyc']['pan'], 'ABCDE1234F')
        self.assertEqual(response.data['bank_details']['bank_name'], 'Example Bank')
        self.assertEqual(
            response.data['emergency_contact']['contact_name'], 'Jordan Employee'
        )
        self.assertEqual(response.data['education']['highest_qualification'], 'Bachelors')
        self.assertIn('business_card_details', response.data)
        self.assertEqual(response.data['document_checklist']['pan_card_copy'], 'Received')
        self.assertTrue(response.data['declaration']['declaration_confirmed'])

    def test_unauthenticated_request_is_rejected(self):
        self.client.credentials()

        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_employee_cannot_access_another_profile_using_url_id(self):
        response = self.client.get(f'{self.profile_url}{self.other_employee.pk}/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_without_employee_profile_is_handled_safely(self):
        user_without_profile = get_user_model().objects.create_user(
            username='user-without-employee-profile',
            password='employee-test-password',
        )
        access_token = RefreshToken.for_user(user_without_profile).access_token
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
