from typing import Any
from django.forms import ModelForm
from django import forms
from .models import Attendance, Department, Designation, Employee, EmployeeDocument, StaffLeave, WorkShift
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