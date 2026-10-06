from datetime import date

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from employees.models import (
    Employee,
    EmployeeAsset,
    EmployeeBankDetails,
    EmployeeBusinessCardDetails,
    EmployeeDeclaration,
    EmployeeDocumentChecklist,
    EmployeeEducation,
    EmployeeEmergencyContact,
    EmployeeKYC,
    LeaveApplication,
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


class LeaveManagementAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.employee_user = get_user_model().objects.create_user(
            username='leave-employee',
            password='employee-password',
        )
        self.employee = self.create_employee('EMP-LEAVE-001', self.employee_user)
        self.other_employee_user = get_user_model().objects.create_user(
            username='other-leave-employee',
            password='employee-password',
        )
        self.other_employee = self.create_employee(
            'EMP-LEAVE-002', self.other_employee_user
        )
        self.admin_user = get_user_model().objects.create_user(
            username='leave-admin',
            password='admin-password',
            is_staff=True,
        )
        self.apply_url = '/api/employees/leave/apply/'
        self.history_url = '/api/employees/leave/history/'
        self.balance_url = '/api/employees/leave/balance/'
        self.admin_list_url = '/api/employees/admin/leaves/'
        self.payload = {
            'leave_type': 'Annual',
            'start_date': '2026-10-12',
            'end_date': '2026-10-14',
            'reason': 'Personal leave',
        }
        self.authenticate_as(self.employee_user)

    def create_employee(self, employee_id, user):
        return Employee.objects.create(
            full_name='Taylor Employee',
            fathers_spouses_name='Jordan Employee',
            user=user,
            date_of_birth=date(1990, 1, 15),
            gender='Other',
            nationality='Indian',
            personal_mobile_number='9876543210',
            personal_email=f'{employee_id.lower()}@example.com',
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

    def authenticate_as(self, user):
        access_token = RefreshToken.for_user(user).access_token
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

    def create_leave(self, employee, **overrides):
        values = {
            'employee': employee,
            'leave_type': 'Annual',
            'start_date': date(2026, 10, 12),
            'end_date': date(2026, 10, 14),
            'reason': 'Personal leave',
        }
        values.update(overrides)
        return LeaveApplication.objects.create(**values)

    def test_employee_can_apply_and_days_are_calculated_on_backend(self):
        response = self.client.post(
            self.apply_url,
            {
                **self.payload,
                'number_of_days': 99,
                'status': LeaveApplication.Status.APPROVED,
                'employee': self.other_employee.pk,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['employee'], self.employee.pk)
        self.assertEqual(response.data['number_of_days'], 3)
        self.assertEqual(response.data['status'], LeaveApplication.Status.PENDING)
        self.assertIsNone(response.data['reviewed_date'])
        self.assertIsNone(response.data['reviewer'])
        self.assertEqual(
            LeaveApplication.objects.get(pk=response.data['id']).employee,
            self.employee,
        )

    def test_employee_cannot_apply_with_end_date_before_start_date(self):
        response = self.client.post(
            self.apply_url,
            {
                **self.payload,
                'start_date': '2026-10-14',
                'end_date': '2026-10-12',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('end_date', response.data)

    def test_employee_can_only_view_own_history(self):
        own_leave = self.create_leave(self.employee)
        self.create_leave(
            self.other_employee,
            leave_type='Sick',
            start_date=date(2026, 11, 2),
            end_date=date(2026, 11, 2),
        )

        response = self.client.get(self.history_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], own_leave.pk)
        self.assertEqual(response.data[0]['employee_id'], self.employee.employee_id)

    def test_employee_leave_balance_reports_status_and_type_progress(self):
        self.create_leave(
            self.employee,
            status=LeaveApplication.Status.APPROVED,
            reviewed_date=timezone.now(),
            reviewer=self.admin_user,
        )
        self.create_leave(
            self.employee,
            leave_type='Sick',
            start_date=date(2026, 11, 2),
            end_date=date(2026, 11, 2),
        )
        self.create_leave(self.other_employee)

        response = self.client.get(self.balance_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['application_counts']['approved'], 1)
        self.assertEqual(response.data['application_counts']['pending'], 1)
        self.assertEqual(response.data['day_counts']['approved'], 3)
        self.assertEqual(response.data['day_counts']['pending'], 1)
        self.assertIsNone(response.data['remaining_entitlement'])
        self.assertEqual(
            {item['leave_type'] for item in response.data['by_leave_type']},
            {'Annual', 'Sick'},
        )

    def test_employee_cannot_access_admin_leave_list_or_review(self):
        leave = self.create_leave(self.employee)

        list_response = self.client.get(self.admin_list_url)
        review_response = self.client.patch(
            f'{self.admin_list_url}{leave.pk}/review/',
            {'status': LeaveApplication.Status.APPROVED},
            format='json',
        )

        self.assertEqual(list_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(review_response.status_code, status.HTTP_403_FORBIDDEN)
        leave.refresh_from_db()
        self.assertEqual(leave.status, LeaveApplication.Status.PENDING)

    def test_admin_can_list_and_approve_or_reject_leave(self):
        approved_leave = self.create_leave(self.employee)
        rejected_leave = self.create_leave(
            self.other_employee,
            leave_type='Sick',
            start_date=date(2026, 11, 2),
            end_date=date(2026, 11, 2),
        )
        self.authenticate_as(self.admin_user)

        list_response = self.client.get(self.admin_list_url)
        approve_response = self.client.patch(
            f'{self.admin_list_url}{approved_leave.pk}/review/',
            {
                'status': LeaveApplication.Status.APPROVED,
                'admin_remarks': 'Approved.',
            },
            format='json',
        )
        reject_response = self.client.patch(
            f'{self.admin_list_url}{rejected_leave.pk}/review/',
            {
                'status': LeaveApplication.Status.REJECTED,
                'admin_remarks': 'Insufficient coverage.',
            },
            format='json',
        )

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 2)
        self.assertEqual(approve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(reject_response.status_code, status.HTTP_200_OK)
        approved_leave.refresh_from_db()
        rejected_leave.refresh_from_db()
        self.assertEqual(approved_leave.status, LeaveApplication.Status.APPROVED)
        self.assertEqual(approved_leave.reviewer, self.admin_user)
        self.assertIsNotNone(approved_leave.reviewed_date)
        self.assertEqual(approved_leave.admin_remarks, 'Approved.')
        self.assertEqual(rejected_leave.status, LeaveApplication.Status.REJECTED)
        self.assertEqual(rejected_leave.reviewer, self.admin_user)
        self.assertIsNotNone(rejected_leave.reviewed_date)
        self.assertEqual(
            rejected_leave.admin_remarks, 'Insufficient coverage.'
        )

    def test_unauthenticated_employee_leave_request_is_rejected(self):
        self.client.credentials()

        response = self.client.get(self.history_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_cannot_review_already_reviewed_application(self):
        leave = self.create_leave(
            self.employee,
            status=LeaveApplication.Status.APPROVED,
            reviewed_date=timezone.now(),
            reviewer=self.admin_user,
        )
        self.authenticate_as(self.admin_user)

        response = self.client.patch(
            f'{self.admin_list_url}{leave.pk}/review/',
            {'status': LeaveApplication.Status.REJECTED},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class EmployeeAssetAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin = get_user_model().objects.create_user(
            username='asset-admin',
            password='AdminPass123',
            is_staff=True,
            is_superuser=True,
        )

        self.employee = Employee.objects.create(
            full_name='Asset Test Employee',
            preferred_short_name='Asset Test',
            fathers_spouses_name='Test Parent',
            date_of_birth='1995-01-01',
            gender='Male',
            marital_status='Single',
            blood_group='O+',
            nationality='Indian',
            personal_mobile_number='9876543210',
            personal_email='asset.employee@example.com',
            current_address='Test Address',
            current_city='Mysore',
            current_state='Karnataka',
            current_pin_code='570001',
            permanent_address_same_as_current=True,
            employee_id='EMP-ASSET-001',
            date_of_joining='2026-10-01',
            designation='Software Developer',
            department='IT',
            employment_type='Full Time',
            work_location='Mysore',
            reporting_manager='Test Manager',
            official_email='asset.employee@company.com',
        )

        self.client.force_authenticate(user=self.admin)

        self.asset_url = '/api/employees/assets/'

    def test_admin_can_create_asset(self):
        response = self.client.post(
            self.asset_url,
            {
                'employee': self.employee.id,
                'asset_type': 'laptop',
                'asset_name': 'Dell Laptop',
                'model_series': 'Latitude 5450',
                'serial_number': 'DL-123456',
                'asset_tag': 'AST-001',
                'assigned_date': '2026-10-06',
                'status': 'assigned',
                'remarks': 'Company laptop',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['asset_name'], 'Dell Laptop')
        self.assertEqual(response.data['model_series'], 'Latitude 5450')

    def test_admin_can_list_assets(self):
        EmployeeAsset.objects.create(
            employee=self.employee,
            asset_type='laptop',
            asset_name='Dell Laptop',
            model_series='Latitude 5450',
            serial_number='DL-123456',
            asset_tag='AST-001',
            assigned_date='2026-10-06',
        )

        response = self.client.get(self.asset_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_can_filter_assets_by_employee(self):
        EmployeeAsset.objects.create(
            employee=self.employee,
            asset_type='laptop',
            asset_name='Dell Laptop',
            assigned_date='2026-10-06',
        )

        response = self.client.get(
            self.asset_url,
            {'employee_id': self.employee.id},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]['employee'],
            self.employee.id,
        )

    def test_admin_can_filter_assets_by_type(self):
        EmployeeAsset.objects.create(
            employee=self.employee,
            asset_type='laptop',
            asset_name='Dell Laptop',
            assigned_date='2026-10-06',
        )

        EmployeeAsset.objects.create(
            employee=self.employee,
            asset_type='monitor',
            asset_name='Dell Monitor',
            assigned_date='2026-10-06',
        )

        response = self.client.get(
            self.asset_url,
            {'asset_type': 'laptop'},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]['asset_type'],
            'laptop',
        )

    def test_admin_can_filter_assets_by_status(self):
        EmployeeAsset.objects.create(
            employee=self.employee,
            asset_type='laptop',
            asset_name='Dell Laptop',
            assigned_date='2026-10-06',
            status='assigned',
        )

        EmployeeAsset.objects.create(
            employee=self.employee,
            asset_type='monitor',
            asset_name='Dell Monitor',
            assigned_date='2026-10-06',
            status='returned',
            returned_date='2026-10-10',
        )

        response = self.client.get(
            self.asset_url,
            {'status': 'assigned'},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]['status'],
            'assigned',
        )

    def test_admin_can_update_asset(self):
        asset = EmployeeAsset.objects.create(
            employee=self.employee,
            asset_type='laptop',
            asset_name='Dell Laptop',
            model_series='Latitude 5450',
            assigned_date='2026-10-06',
        )

        response = self.client.patch(
            f'{self.asset_url}{asset.id}/',
            {
                'model_series': 'Latitude 5550',
                'serial_number': 'NEW-SERIAL-001',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        asset.refresh_from_db()

        self.assertEqual(asset.model_series, 'Latitude 5550')
        self.assertEqual(asset.serial_number, 'NEW-SERIAL-001')

    def test_returned_asset_requires_returned_date(self):
        response = self.client.post(
            self.asset_url,
            {
                'employee': self.employee.id,
                'asset_type': 'laptop',
                'asset_name': 'Dell Laptop',
                'assigned_date': '2026-10-06',
                'status': 'returned',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn('returned_date', response.data)

    def test_returned_date_cannot_be_before_assigned_date(self):
        response = self.client.post(
            self.asset_url,
            {
                'employee': self.employee.id,
                'asset_type': 'laptop',
                'asset_name': 'Dell Laptop',
                'assigned_date': '2026-10-10',
                'returned_date': '2026-10-05',
                'status': 'returned',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn('returned_date', response.data)