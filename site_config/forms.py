from .models import SiteConfig
from django.forms import ModelForm
from django import forms


class SiteConfigForm(ModelForm):
    
    class Meta:
        model = SiteConfig
        fields = [
            'name', 'logo'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
            })
        }