from .models import ContactPerson, EmergencyCase, Epidemic, MedicalEmergencyType
from django import forms


class EpidemicForm(forms.ModelForm):
    
    class Meta:
        model = Epidemic
        fields = [
            'name', 'description', 'prevention', 
            'treatment', 'start_date', 'end_date'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control'
            }),
            'prevention': forms.Textarea(attrs={
                'class': 'form-control'
            }),
            'treatment': forms.Textarea(attrs={
                'class': 'form-control'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control'
            }),
        }


class MedicalEmergencyTypeForm(forms.ModelForm):

    class Meta:
        model = MedicalEmergencyType
        fields = [
            'category', 'name',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


class ContactPersonForm(forms.ModelForm):

    class Meta:
        model = ContactPerson
        fields = [
            'name', 'phone_number', 
            'living_address',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'living_address': forms.TextInput(attrs={
                'class': 'form-control'
            }),
        }


class EmergencyCaseForm(forms.ModelForm):

    class Meta:
        model = EmergencyCase
        fields = [
            'type', 'patient_name',
            'patient_age', 'patient_sex',
            'description',
        ]
        widgets = {
            'type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'patient_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'patient_age': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'patient_sex': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control'
            }),
        }