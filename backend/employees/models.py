from django.db import models
from django.core.validators import RegexValidator


class Employee(models.Model):
    full_name = models.CharField(max_length=255, verbose_name='Full Name (as per PAN)')
    preferred_short_name = models.CharField(
        max_length=255, blank=True, verbose_name='Preferred / Short Name'
    )
    fathers_spouses_name = models.CharField(
        max_length=255, verbose_name="Father's / Spouse's Name"
    )
    date_of_birth = models.DateField(verbose_name='Date of Birth')
    gender = models.CharField(max_length=50, verbose_name='Gender')
    marital_status = models.CharField(
        max_length=50, blank=True, verbose_name='Marital Status'
    )
    blood_group = models.CharField(max_length=10, blank=True, verbose_name='Blood Group')
    nationality = models.CharField(max_length=100, verbose_name='Nationality')
    personal_mobile_number = models.CharField(
        max_length=20, verbose_name='Personal Mobile No.'
    )
    alternate_mobile_number = models.CharField(
        max_length=20, blank=True, verbose_name='Alternate Mobile No.'
    )
    personal_email = models.EmailField(verbose_name='Personal Email ID')
    current_address = models.CharField(
        max_length=255, verbose_name='Current Address (House, Street, Area)'
    )
    current_city = models.CharField(max_length=100, verbose_name='Current City')
    current_state = models.CharField(max_length=100, verbose_name='Current State')
    current_pin_code = models.CharField(
        max_length=6,
        validators=[RegexValidator(r'^\d{6}$', 'Enter a 6-digit PIN code.')],
        verbose_name='Current PIN Code',
    )
    permanent_address_same_as_current = models.BooleanField(
        verbose_name='Permanent address same as current?'
    )
    permanent_address = models.CharField(
        max_length=255, blank=True, verbose_name='Permanent Address'
    )
    permanent_city = models.CharField(
        max_length=100, blank=True, verbose_name='Permanent City'
    )
    permanent_state = models.CharField(
        max_length=100, blank=True, verbose_name='Permanent State'
    )
    permanent_pin_code = models.CharField(
        max_length=6,
        blank=True,
        validators=[RegexValidator(r'^\d{6}$', 'Enter a 6-digit PIN code.')],
        verbose_name='Permanent PIN Code',
    )
    employee_id = models.CharField(
        max_length=50, unique=True, verbose_name='Employee ID'
    )
    date_of_joining = models.DateField(verbose_name='Date of Joining')
    designation = models.CharField(max_length=150, verbose_name='Designation')
    department = models.CharField(max_length=150, verbose_name='Department')
    employment_type = models.CharField(max_length=50, verbose_name='Employment Type')
    work_location = models.CharField(max_length=255, verbose_name='Work Location')
    reporting_manager = models.CharField(max_length=255, verbose_name='Reporting Manager')
    official_email = models.EmailField(verbose_name='Official Email ID')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.employee_id} - {self.full_name}'


class EmployeeKYC(models.Model):
    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, related_name='kyc'
    )
    pan = models.CharField(
        max_length=10,
        validators=[RegexValidator(r'^[A-Z]{5}[0-9]{4}[A-Z]$')],
        verbose_name='PAN',
    )
    name_as_per_pan = models.CharField(max_length=255, verbose_name='Name as per PAN')
    aadhaar_number = models.CharField(
        max_length=12,
        validators=[RegexValidator(r'^\d{12}$')],
        verbose_name='Aadhaar Number',
    )
    name_as_per_aadhaar = models.CharField(
        max_length=255, verbose_name='Name as per Aadhaar'
    )
    passport_number = models.CharField(
        max_length=50, blank=True, verbose_name='Passport Number'
    )
    passport_expiry_date = models.DateField(
        blank=True, null=True, verbose_name='Passport Expiry Date'
    )
    voter_id_epic_number = models.CharField(
        max_length=50, blank=True, verbose_name='Voter ID (EPIC) No.'
    )
    driving_licence_number = models.CharField(
        max_length=50, blank=True, verbose_name='Driving Licence No.'
    )
    driving_licence_expiry = models.DateField(
        blank=True, null=True, verbose_name='Driving Licence Expiry'
    )
    uan = models.CharField(
        max_length=50, blank=True, verbose_name='UAN (if existing PF member)'
    )
    previous_pf_member_id = models.CharField(
        max_length=100, blank=True, verbose_name='Previous PF Member ID'
    )
    esic_ip_number = models.CharField(
        max_length=50, blank=True, verbose_name='ESIC IP Number (if any)'
    )
    previous_employer = models.CharField(
        max_length=255, blank=True, verbose_name='Previous Employer'
    )
    income_tax_regime_opted = models.CharField(
        max_length=50, blank=True, verbose_name='Income Tax Regime Opted'
    )

    def __str__(self):
        return f'KYC - {self.employee.employee_id}'


class EmployeeBankDetails(models.Model):
    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, related_name='bank_details'
    )
    account_holder_name = models.CharField(
        max_length=255, verbose_name='Account Holder Name'
    )
    bank_name = models.CharField(max_length=255, verbose_name='Bank Name')
    branch = models.CharField(max_length=255, verbose_name='Branch')
    account_number = models.CharField(max_length=50, verbose_name='Account Number')
    account_type = models.CharField(max_length=50, verbose_name='Account Type')
    ifsc_code = models.CharField(
        max_length=11,
        validators=[RegexValidator(r'^[A-Z]{4}0[A-Z0-9]{6}$')],
        verbose_name='IFSC Code',
    )

    def __str__(self):
        return f'Bank details - {self.employee.employee_id}'


class EmployeeEmergencyContact(models.Model):
    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, related_name='emergency_contact'
    )
    contact_name = models.CharField(max_length=255, verbose_name='Contact Name')
    relationship = models.CharField(max_length=50, verbose_name='Relationship')
    contact_mobile_number = models.CharField(
        max_length=20, verbose_name='Contact Mobile No.'
    )

    def __str__(self):
        return f'{self.contact_name} - {self.employee.employee_id}'


class EmployeeEducation(models.Model):
    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, related_name='education'
    )
    highest_qualification = models.CharField(
        max_length=255, verbose_name='Highest Qualification'
    )
    university_institute = models.CharField(
        max_length=255, blank=True, verbose_name='University / Institute'
    )
    year_of_completion = models.PositiveSmallIntegerField(
        blank=True, null=True, verbose_name='Year of Completion'
    )

    def __str__(self):
        return f'{self.highest_qualification} - {self.employee.employee_id}'


class EmployeeBusinessCardDetails(models.Model):
    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, related_name='business_card_details'
    )
    name_to_print_on_card = models.CharField(
        max_length=255, blank=True, verbose_name='Name to print on card'
    )
    credentials_suffix = models.CharField(
        max_length=100, blank=True, verbose_name='Credentials / Suffix (optional)'
    )
    designation_to_print = models.CharField(
        max_length=150, blank=True, verbose_name='Designation to print'
    )
    department_practice_to_print = models.CharField(
        max_length=150, blank=True, verbose_name='Department / Practice to print'
    )
    mobile_to_print = models.CharField(
        max_length=30, blank=True, verbose_name='Mobile to print'
    )
    email_to_print = models.EmailField(blank=True, verbose_name='Email to print')
    office_landline_extension = models.CharField(
        max_length=50, blank=True, verbose_name='Office Landline / Extn.'
    )
    office_address_to_print = models.TextField(
        blank=True, verbose_name='Office Address to print'
    )
    linkedin_url = models.URLField(
        max_length=255, blank=True, verbose_name='LinkedIn URL (optional)'
    )
    quantity_of_cards = models.PositiveSmallIntegerField(
        blank=True, null=True, verbose_name='Quantity of cards'
    )

    def __str__(self):
        return f'Business card - {self.employee.employee_id}'


class EmployeeDocumentChecklist(models.Model):
    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, related_name='document_checklist'
    )
    pan_card_copy = models.CharField(max_length=30, verbose_name='PAN card copy')
    aadhaar_card_copy = models.CharField(max_length=30, verbose_name='Aadhaar card copy')
    passport_copy = models.CharField(
        max_length=30, blank=True, verbose_name='Passport copy'
    )
    passport_size_photograph = models.CharField(
        max_length=30, verbose_name='Passport-size photograph'
    )
    cancelled_cheque_bank_letter = models.CharField(
        max_length=30, verbose_name='Cancelled cheque / bank letter'
    )
    education_certificates = models.CharField(
        max_length=30, verbose_name='Education certificates'
    )
    relieving_experience_letter = models.CharField(
        max_length=30, blank=True, verbose_name='Relieving / experience letter'
    )
    last_three_months_payslips = models.CharField(
        max_length=30, blank=True, verbose_name="Last 3 months' payslips"
    )
    form_16_12b_previous_employer = models.CharField(
        max_length=30, blank=True, verbose_name='Form 16 / Form 12B (prev. employer)'
    )

    def __str__(self):
        return f'Document checklist - {self.employee.employee_id}'


class EmployeeDeclaration(models.Model):
    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, related_name='declaration'
    )
    declaration_confirmed = models.BooleanField(
        verbose_name='I confirm the above details are true and complete'
    )
    date_of_submission = models.DateField(verbose_name='Date of submission')
    verified_by_hr = models.CharField(
        max_length=255, blank=True, verbose_name='Verified by (HR)'
    )
    verification_date = models.DateField(
        blank=True, null=True, verbose_name='Verification date'
    )

    def __str__(self):
        return f'Declaration - {self.employee.employee_id}'
