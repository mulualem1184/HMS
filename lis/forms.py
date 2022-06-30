from django import forms
from django.db.models.base import Model
from django.forms import ModelForm, fields, widgets
from django.forms.forms import Form
from .models import Order, LaboratoryTest, ReferredTestResult, Specimen


class SpecimenForm(ModelForm):

    class Meta:
        model = Specimen
        fields = [
            'collected_by', 'collected_at', 'sample_type',
            'sample_volume','container_type'
        ]
        widgets = {
            'collected_by': forms.Select(attrs={
                'class': 'form-control'
            }),
            'collected_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
            }),
            'sample_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'sample_volume': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
            }),
            'container_type': forms.TextInput(attrs={
                'class': 'form-control'
            }),
        }
        

class OrderForm(ModelForm):
    # sample = forms.BooleanField(widget=forms.CheckboxInput(attrs={
    #     'class': 'form-control',
    # }))
    patient_id = forms.IntegerField(widget=forms.NumberInput(
        attrs={
            'min':1,
            'class': 'form-control',
        }
    ))

    class Meta:
        model = Order
        fields = ['patient_id', 'priority',]
        widgets = {
            'priority': forms.Select(attrs={
                'class': 'form-control',
            }),
        }


class LaboratoryTestForm(ModelForm):
    class Meta:
        model = LaboratoryTest
        fields = ['test_type', 'special_instructions']
        widgets = {
            'test_type': forms.Select(attrs={
                'class': 'form-control select2',
                'style': '',
            }),
            'special_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'style': 'width: 350px; height: 150px'
            })

        }


class ResultEntryForm(Form):

    def __init__(self, dynamic_fields={}, *args, **kwargs) -> None:
        self.fields = dynamic_fields
        super().__init__(*args, **kwargs)

    class Meta:
        fields = []


class ReferredTestResultForm(ModelForm):
    
    class Meta:
        model = ReferredTestResult
        fields = ['lab_name']
        widgets = {
            'lab_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Laboratory/Hospital Name'
            })
        }