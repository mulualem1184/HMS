from .models import XRayRequest, ImagingReport
from django.forms import ModelForm
from django import forms


class XRayRequestForm(ModelForm):
    class Meta:
        model = XRayRequest
        fields = [
            'scan_area', 'film', 'number', 
            'marker', 'scan_area',
        ]
        widgets = {
            'film': forms.Select(attrs={
                'class': 'form-control',
            }),
            'number': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'marker': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'scan_area': forms.Select(attrs={
                'class': 'form-control',
            })
        }


class ReportForm(ModelForm):
    class Meta:
        model = ImagingReport
        fields = [
            'report',
        ]
        widgets = {
            'report': forms.Textarea(attrs={
                'class': 'form-control'
            })
        }