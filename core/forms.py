from django import forms
from .models import Patient, PatientVitalSign, PatientPaymentStatus, InsuranceDetail


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
            'systolic_blood_pressure', 'diastolic_blood_pressure', 
            'oxygen_saturation','blood_glucose_level',
            'glucose_level_unit'
        ]
        widgets = {            
            'pulse_rate': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'temperature': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'systolic_blood_pressure': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'diastolic_blood_pressure': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'oxygen_saturation': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'blood_glucose_level': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'glucose_level_unit': forms.Select(attrs={
                'class' : 'form-control select2',
            }),
            'temperature_unit': forms.Select(attrs={
                'class' : 'form-control select2',
            }),

        }


class PatientPaymentStatusForm(forms.ModelForm):
    
    class Meta:
        model = PatientPaymentStatus 
        fields = ['payment_status']
        
        widgets = {
            'payment_status': forms.Select(attrs={
            'class' : 'select2 form-control',

                }),
            }

class InsuranceDetailForm(forms.ModelForm):
    
    class Meta:
        model = InsuranceDetail
        fields = ['name',  'phone_number', 'address']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'phone_number': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'address': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),

            }
