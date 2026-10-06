from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from employees.authentication import authenticate_employee
from employees.models import (
    Employee,
    EmployeeBankDetails,
    EmployeeBusinessCardDetails,
    EmployeeDeclaration,
    EmployeeDocumentChecklist,
    EmployeeEducation,
    EmployeeEmergencyContact,
    EmployeeKYC,
    LeaveApplication,
)


class EmployeeLoginSerializer(serializers.Serializer):
    employee_id = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        user = authenticate_employee(attrs['employee_id'], attrs['password'])
        if user is None:
            raise AuthenticationFailed('Invalid employee credentials.')

        attrs['user'] = user
        return attrs


class LeaveApplicationSerializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(
        source='employee.employee_id', read_only=True
    )
    employee_name = serializers.CharField(
        source='employee.full_name', read_only=True
    )

    class Meta:
        model = LeaveApplication
        fields = (
            'id',
            'employee',
            'employee_id',
            'employee_name',
            'leave_type',
            'start_date',
            'end_date',
            'number_of_days',
            'reason',
            'status',
            'applied_date',
            'reviewed_date',
            'reviewer',
            'admin_remarks',
        )
        read_only_fields = (
            'id',
            'employee',
            'employee_id',
            'employee_name',
            'number_of_days',
            'status',
            'applied_date',
            'reviewed_date',
            'reviewer',
            'admin_remarks',
        )

    def validate(self, attrs):
        start_date = attrs.get(
            'start_date', self.instance.start_date if self.instance else None
        )
        end_date = attrs.get(
            'end_date', self.instance.end_date if self.instance else None
        )
        if start_date is not None and end_date is not None and end_date < start_date:
            raise serializers.ValidationError({
                'end_date': 'End date cannot be before start date.'
            })
        return attrs


class LeaveReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveApplication
        fields = ('status', 'admin_remarks')

    def validate_status(self, value):
        if value not in (
            LeaveApplication.Status.APPROVED,
            LeaveApplication.Status.REJECTED,
        ):
            raise serializers.ValidationError(
                'A leave application can only be approved or rejected.'
            )
        if self.instance.status != LeaveApplication.Status.PENDING:
            raise serializers.ValidationError(
                'Only pending leave applications can be reviewed.'
            )
        return value


class EmployeeKYCSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeKYC
        exclude = ('employee',)


class EmployeeBankDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeBankDetails
        exclude = ('employee',)


class EmployeeEmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeEmergencyContact
        exclude = ('employee',)


class EmployeeEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeEducation
        exclude = ('employee',)


class EmployeeBusinessCardDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeBusinessCardDetails
        exclude = ('employee',)


class EmployeeDocumentChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDocumentChecklist
        exclude = ('employee',)


class EmployeeDeclarationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDeclaration
        exclude = ('employee',)


class EmployeeSerializer(serializers.ModelSerializer):
    kyc = EmployeeKYCSerializer(required=False, default=None)
    bank_details = EmployeeBankDetailsSerializer(required=False, default=None)
    emergency_contact = EmployeeEmergencyContactSerializer(required=False, default=None)
    education = EmployeeEducationSerializer(required=False, default=None)
    business_card_details = EmployeeBusinessCardDetailsSerializer(
        required=False, default=None
    )
    document_checklist = EmployeeDocumentChecklistSerializer(
        required=False, default=None
    )
    declaration = EmployeeDeclarationSerializer(required=False, default=None)

    related_serializers = {
        'kyc': (EmployeeKYC, EmployeeKYCSerializer),
        'bank_details': (EmployeeBankDetails, EmployeeBankDetailsSerializer),
        'emergency_contact': (
            EmployeeEmergencyContact,
            EmployeeEmergencyContactSerializer,
        ),
        'education': (EmployeeEducation, EmployeeEducationSerializer),
        'business_card_details': (
            EmployeeBusinessCardDetails,
            EmployeeBusinessCardDetailsSerializer,
        ),
        'document_checklist': (
            EmployeeDocumentChecklist,
            EmployeeDocumentChecklistSerializer,
        ),
        'declaration': (EmployeeDeclaration, EmployeeDeclarationSerializer),
    }

    class Meta:
        model = Employee
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, attrs):
        for field_name, (model, serializer_class) in self.related_serializers.items():
            data = attrs.get(field_name)
            if data is None:
                continue

            related_record_exists = (
                self.instance is not None
                and model.objects.filter(employee_id=self.instance.pk).exists()
            )
            if not related_record_exists:
                required_fields = {
                    name
                    for name, field in serializer_class().fields.items()
                    if field.required
                }
                missing_fields = required_fields - data.keys()
                if missing_fields:
                    raise serializers.ValidationError({
                        field_name: {
                            name: ['This field is required.']
                            for name in sorted(missing_fields)
                        }
                    })

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        related_data = {
            name: validated_data.pop(name, None)
            for name in self.related_serializers
        }
        employee = Employee.objects.create(**validated_data)
        self._save_related(employee, related_data)
        return employee

    @transaction.atomic
    def update(self, instance, validated_data):
        related_data = {
            name: validated_data.pop(name, None)
            for name in self.related_serializers
        }
        for name, value in validated_data.items():
            setattr(instance, name, value)
        instance.save()
        self._save_related(instance, related_data)
        return instance

    def _save_related(self, employee, related_data):
        for name, data in related_data.items():
            if data is None:
                continue

            model, _ = self.related_serializers[name]
            model.objects.update_or_create(
                employee=employee,
                defaults=data,
            )
