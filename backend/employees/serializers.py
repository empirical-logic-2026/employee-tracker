from django.db import transaction
from rest_framework import serializers

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
