from django import forms
from django.forms import ModelForm
from django.forms.forms import Form

from .models import (LaboratoryTest, LaboratoryTestResultType, LaboratoryTestType, NormalRange, Order,
                     ReferredTestResult, SampleType, Specimen, LabEmployee)


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


class LabTestTypeForm(ModelForm):

    class Meta:
        model = LaboratoryTestType
        fields = [
            'section', 'name', 'price',
            'tat', 'is_available',
        ]
        widgets = {
            'section': forms.Select(attrs={
                'class': 'form-control',
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name of Test type'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Price in ETB'
            }),
            'tat': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'amount of time it takes to complete this test in hours'
            }),
            'is_available': forms.Select(attrs={
                'class': 'form-control',
            }),
        }


class SampleTypeForm(ModelForm):

    class Meta:
        model = SampleType
        exclude = []
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name of the type of sample'
            })
        }


class LabTestResultTypeForm(ModelForm):

    class Meta:
        model = LaboratoryTestResultType
        fields = [
            'name', 'input_type'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'input_type': forms.Select(attrs={
                'class': 'form-control',
                'onchange': 'displayChoices()',
            })
        }

    
class NormalRangeForm(ModelForm):

    class Meta:
        model = NormalRange
        fields = [
            'sex', 'min_age', 'max_age', 
            'min_value', 'max_value',
            'm_unit',
        ]
        widgets = {
            'sex': forms.Select(attrs={
                'class': 'form-control',
            }),
            'min_age': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Minimum age for the normal range'
            }),
            'max_age': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Maximum age for the normal range'
            }),
            'min_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Minimum value for the normal range'
            }),
            'max_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Maximum value for the normal range'
            }),
            'm_unit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Measurment unit of the set normal range'
            }),
        }

class AssignLabEmployeeForm(forms.ModelForm):
    class Meta:
        model = LabEmployee
        fields = ['laboratorist']
        widgets = {         
            'laboratorist': forms.Select(attrs={
            'class' : 'select2 form-control',
                }),
            }
