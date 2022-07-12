from django import forms

from .utils import Fieldset
from .models import (ContactPerson, EmergencyCase, Epidemic,
                     MedicalEmergencyType, PatientReferralLocation)
from django.utils import timezone


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
                'class': 'form-control',
                'placeholder': 'Enter Contact Persons name',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Contact persons phone number'
            }),
            'living_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Contact persons living address'
            }),
        }


class EmergencyCaseForm(forms.ModelForm):

    class Meta:
        model = EmergencyCase
        fields = [
            'patient_name', 'patient_age', 
            'patient_sex', 'arrival_date', 
            'triage_date', 'address',
            'transport', 'triage_color',
            'triage_treatment', 'other_illness',
            'avpu', 'mobility',
        ]
        widgets = {
            'type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'patient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Patient full name',
            }),
            'patient_age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Patient age',
                'min': 0,
            }),
            'patient_sex': forms.Select(attrs={
                'class': 'form-control',
            }),
            'transport': forms.Select(attrs={
                'class': 'form-control'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'arrival_date': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'triage_date': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'triage_color': forms.Select(attrs={
                'class': 'form-control'
            }),
            'triage_treatment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'If any treatment was given before patient was admitted to emergency room ',
            }),
            'other_illness': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write if patient has any known allergies or illness',
            }),
            'avpu': forms.Select(attrs={
                'class': 'form-control'
            }),
            'mobility': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


class FilterCaseForm(forms.Form):
    TRIAGE_COLOR_CHOICES = [
        (0, '-------'),
        ('RED', 'RED'),
        ('ORANGE', 'ORANGE'),
        ('YELLOW', 'YELLOW'),
        ('BLACK', 'BLACK'),
    ]
    referred_from = forms.ModelChoiceField(PatientReferralLocation.objects.all(), required=False, widget=forms.Select(
        attrs={
            'class': 'form-control'
        }
    ))
    from_date = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'class': 'form-control',
        'placeholder': timezone.now().date(),
    }))
    to_date = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'class': 'form-control',
        'placeholder': timezone.now().date(),
    }))
    triage_color = forms.ChoiceField(required=False, choices=TRIAGE_COLOR_CHOICES, widget=forms.Select(attrs={
        'class': 'form-control',
    }))


patient_info_fieldset = Fieldset('Patient Information',['patient_name', 'patient_age', 
        'patient_sex','arrival_date', 'triage_date',
        'transport'], EmergencyCaseForm(),
    )

contact_person_fieldset = Fieldset('Contact Person info', [
    'name', 'phone_number', 'living_address'
], ContactPersonForm())

triage_color_fieldset = Fieldset('', ['', ], EmergencyCaseForm())
other_fieldset = Fieldset('Other', ['triage_treatment', 'other_illness'], EmergencyCaseForm())
triage_stat_fieldset = Fieldset('', ['avpu', 'mobility'], EmergencyCaseForm())