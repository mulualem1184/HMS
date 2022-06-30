from django import forms
from .models import Patient, PatientVitalSign


class PatientForm(forms.ModelForm):

    class Meta:
        model = Patient
        widgets = {}
        exclude = []
        


class VitalSignForm(forms.ModelForm):
    class Meta:
        model = PatientVitalSign
        fields = [
            'pulse_rate', 'temperature', 'temperature_unit',
            'blood_pressure', 
        ]
        widgets = {            
            'pulse_rate': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'temperature': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'blood_pressure': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'temperature_unit': forms.Select(attrs={
                'class' : 'form-control select2',
            }),
        }