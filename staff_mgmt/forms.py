from typing import Any
from django.forms import ModelForm
from django import forms
from .models import (Attendance, Department, Designation, Employee, EmployeeDocument, 
                    StaffLeave, WorkShift, StaffTeam, MedicalPermission, ComponentPermission,
                    BillingPermission,SettingPermission,LaboratoryPermission, PharmacyPermission,
                    WardPermission,OtherPermission)
from django.contrib.auth import get_user_model

User = get_user_model()


class DepartmentForm(ModelForm):
    class Meta:
        model = Department
        exclude = []
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
            }),
        }


class DesignationForm(ModelForm):
    class Meta:
        model = Designation
        exclude = []
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'staff_code': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'department': forms.Select(attrs={
                'class': 'form-control',
            }),
        }


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'profile_image', 'phone_number',
            'email', 'password','gender', 'age', 
            'is_active',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control input-height',
                'placeholder': 'enter first name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'enter last name',
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'enter phone number',
            }),
            'email': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'enter email',
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'enter password',
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control',
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': '',
            })
        }

    def save(self, commit=True, update=False) -> Any:
        user_instance = super().save(commit=commit)
        if not update:
            user_instance.set_password(self.data['password'])
            user_instance.save()
        return user_instance


class EmployeeForm(ModelForm):
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'employed_date',
            'designation'
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'employed_date': forms.DateInput(attrs={
                'class': 'form-control',
            }),
            'designation': forms.Select(attrs={
                'class': 'form-control',
            }),
        }


class EmployeeDocumentForm(ModelForm):
    class Meta:
        model = EmployeeDocument
        fields = [
            'document_name', 'document',
        ]
        widgets = {
            'document_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'document': forms.FileInput(attrs={
                'class': 'form-control',
            })
        }


class ResetPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
        }
    ))


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
        }
    ))
    new_password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
        }
    ))


class LeaveForm(ModelForm):
    class Meta:
        model = StaffLeave
        fields = [
            'from_date', 'to_date',
            'type_of_leave', 'description', 
        ]
        widgets = {
            'from_date': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'to_date': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'type_of_leave': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control'
            }),
        }


class WorkShiftForm(ModelForm):
    class Meta:
        model = WorkShift
        fields = [
            'shift_type', 'day', 'start_time', 'end_time'
        ]
        widgets = {
            'shift_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'day': forms.Select(attrs={
                'class': 'form-control'
            }),
            'start_time': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'end_time': forms.TextInput(attrs={
                'class': 'form-control'
            }),
        }


class EmployeeShiftForm(ModelForm):
    class Meta:
        model = WorkShift
        exclude = [
            
        ]


class UpdateAttendanceForm(ModelForm):
    class Meta:
        model = Attendance
        fields = [
            'start_time', 'end_time',
        ]


class FilterScheduleForm(forms.Form):
    department = forms.ModelChoiceField(Department.objects.all(), required=False,
            widget=forms.Select(attrs={
                'class': 'form form-control',
            }))
    month = forms.ChoiceField(required=False, choices=[
        (0, '-----'),
        (1, 'January'), (2, 'February'),
        (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'),
        (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'),
        (11, 'November'), (12, 'December'),
    ], widget=forms.Select(attrs={
        'class': 'form-control',
    }))


class UpdateDepartmentHeadForm(forms.Form):
    employee = forms.ModelChoiceField(
        Employee.objects.all(), required=True,
        widget=forms.Select(attrs={
            'class': 'form form-control',
        })
    )
class CreateStaffTeamForm(forms.ModelForm):

    class Meta:
        model = StaffTeam
        fields = [ 'team_name', 'department']

        widgets = {                     
            'team_name': forms.TextInput(attrs={
            'class' : 'form-control forms',

                }),
            'department': forms.Select(attrs={
            'class' : 'form-control forms select2',

                }),

            }


class MedicalViewPermissionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        designation_id = kwargs.pop('designation_id')
        designation = Designation.objects.get(id=designation_id)
        super(MedicalViewPermissionForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            try:
                has = hasattr(designation.permission.medical,f)
                value = getattr(designation.permission.medical,f)
                self.fields[f].initial = value

            except :
                pass
            """
            if hasattr(designation.permission.medical,f):
                value = getattr(designation.permission.medical,f)
                self.fields[f].initial = value
            """
    class Meta:
        model = MedicalPermission
        fields = [  'view_consultation','view_clinical_finding',
                    'view_treatment','view_allergy',
                    'view_paraclinical_finding','view_prescription',
                    'view_diagnosis','view_surgery','view_document',
                    'view_treatment_plan','view_treatment_plan_action',
                    'view_medical_attendance','view_medical_certificate'
        ]

class MedicalWritePermissionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        designation_id = kwargs.pop('designation_id')
        designation = Designation.objects.get(id=designation_id)
        super(MedicalWritePermissionForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            try:
                has = hasattr(designation.permission.medical,f)
                value = getattr(designation.permission.medical,f)
                self.fields[f].initial = value

            except :
                pass
            """
            if hasattr(designation.permission.medical,f):
                value = getattr(designation.permission.medical,f)
                self.fields[f].initial = value
            """
    class Meta:
        model = MedicalPermission
        fields = ['write_consultation','write_clinical_finding','write_treatment',
                    'write_allergy','write_paraclinical_finding','write_prescription',
                    'write_diagnosis','write_surgery','write_document',
                    'write_treatment_plan','write_treatment_plan_action',
                    'write_medical_certificate','write_medical_attendance'
        ]





class EditMedicalPermissionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        designation_id = kwargs.pop('designation_id')
        designation = Designation.objects.get(id=designation_id)
        super(EditMedicalPermissionForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            if hasattr(designation.permission.medical,f):
                value = getattr(designation.permission.medical,f)
                self.fields[f].initial = value


    class Meta:
        model = MedicalPermission
        fields = [ 'write_consultation', 'view_consultation','write_clinical_finding','view_clinical_finding',
                    'write_treatment','view_treatment','write_allergy','view_allergy','write_paraclinical_finding',
                    'view_paraclinical_finding','write_prescription','view_prescription','write_diagnosis',
                    'view_diagnosis','write_surgery','view_surgery','write_document','view_document','write_treatment_plan',
                    'view_treatment_plan','write_treatment_plan_action','view_treatment_plan_action'
        ]


class ComponentPermissionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        designation_id = kwargs.pop('designation_id')
        designation = Designation.objects.get(id=designation_id)
        super(ComponentPermissionForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            try:
                has = hasattr(designation.permission.component,f)
                value = getattr(designation.permission.component,f)
                self.fields[f].initial = value
            except :
                pass

    class Meta:
        model = ComponentPermission
        fields = [ 'view_patient_record', 'view_patient_chart','view_ward','view_laboratory',
                    'view_lab_dashboard','view_billing','view_billing_dashboard','view_cashier_reconcilation',
                    'view_pharmacy','view_staff'
        ]


class LaboratoryViewPermissionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        designation_id = kwargs.pop('designation_id')
        designation = Designation.objects.get(id=designation_id)
        super(LaboratoryViewPermissionForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            try:
                has = hasattr(designation.permission.laboratory,f)
                value = getattr(designation.permission.laboratory,f)
                self.fields[f].initial = value
            except :
                pass

    class Meta:
        model = LaboratoryPermission
        fields = [ 'view_lab_request', 'view_lab_specimen','view_lab_result']

class LaboratoryWritePermissionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        designation_id = kwargs.pop('designation_id')
        designation = Designation.objects.get(id=designation_id)
        super(LaboratoryWritePermissionForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            try:
                has = hasattr(designation.permission.laboratory,f)
                value = getattr(designation.permission.laboratory,f)
                self.fields[f].initial = value
            except:
                pass

    class Meta:
        model = LaboratoryPermission
        fields = [ 'write_lab_request', 'write_lab_specimen','write_lab_result']

class SettingPermissionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        designation_id = kwargs.pop('designation_id')
        designation = Designation.objects.get(id=designation_id)
        super(SettingPermissionForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            try:
                has = hasattr(designation.permission.setting,f)
                value = getattr(designation.permission.setting,f)
                self.fields[f].initial = value
            except :
                pass

    class Meta:
        model = SettingPermission
        fields = [ 'write_lab_test_type','write_item','write_ward_structure','write_pharmacy_structure']

class BillingWritePermissionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        designation_id = kwargs.pop('designation_id')
        designation = Designation.objects.get(id=designation_id)
        super(BillingWritePermissionForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            try:
                has = hasattr(designation.permission.billing,f)
                value = getattr(designation.permission.billing,f)
                self.fields[f].initial = value
            except :
                pass

    class Meta:
        model = BillingPermission
        fields = [ 'write_invoice','write_receipt','write_payment']

class BillingViewPermissionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        designation_id = kwargs.pop('designation_id')
        designation = Designation.objects.get(id=designation_id)
        super(BillingViewPermissionForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            try:
                has = hasattr(designation.permission.billing,f)
                value = getattr(designation.permission.billing,f)
                self.fields[f].initial = value
            except :
                pass

    class Meta:
        model = BillingPermission
        fields = [ 'view_invoice','view_receipt','view_payment']


class PharmacyPermissionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        designation_id = kwargs.pop('designation_id')
        designation = Designation.objects.get(id=designation_id)
        super(PharmacyPermissionForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            try:
                has = hasattr(designation.permission.pharmacy,f)
                value = getattr(designation.permission.pharmacy,f)
                self.fields[f].initial = value
            except :
                pass

    class Meta:
        model = PharmacyPermission
        fields = [ 'write_drug_transfer_request','write_first_transfer_request_approval',
                    'write_second_transfer_request_approval','write_relocate_item','write_allocate_item'
        ]

class WardPermissionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        designation_id = kwargs.pop('designation_id')
        designation = Designation.objects.get(id=designation_id)
        super(WardPermissionForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            try:
                has = hasattr(designation.permission.ward,f)
                value = getattr(designation.permission.ward,f)
                self.fields[f].initial = value
            except :
                pass

    class Meta:
        model = WardPermission
        fields = [ 'write_ward_admission','view_ward_admission',]

class OtherWritePermissionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        designation_id = kwargs.pop('designation_id')
        designation = Designation.objects.get(id=designation_id)
        super(OtherWritePermissionForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            try:
                has = hasattr(designation.permission.other,f)
                value = getattr(designation.permission.other,f)
                self.fields[f].initial = value
            except :
                pass

    class Meta:
        model = OtherPermission
        fields = [ 'write_checkin','write_resource',
                    'write_material'        ]

class OtherViewPermissionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        designation_id = kwargs.pop('designation_id')
        designation = Designation.objects.get(id=designation_id)
        super(OtherViewPermissionForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            try:
                has = hasattr(designation.permission.other,f)
                value = getattr(designation.permission.other,f)
                self.fields[f].initial = value
            except :
                pass

    class Meta:
        model = OtherPermission
        fields = [ 'view_checkin','view_resource',
                    'view_material'
        ]
