from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import *
from outpatient_app.models import *
from django.contrib.auth.models import User
import datetime
from django.contrib.admin import site as admin_site
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.contrib.admin.widgets import AdminDateWidget
from functools import partial

#import autocomplete_light

from django.forms.models import(
	inlineformset_factory,
	modelform_factory,
	modelformset_factory
	)



#Drug profile form
###
class PatientInsuranceDetailForm(forms.ModelForm):
	
	class Meta:
		model = PatientInsuranceDetail
		fields = ['sum_insured'	]
		
		widgets = {
			
			'sum_insured': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			}

class InsuranceExcludedServiceForm(forms.ModelForm):
	
	class Meta:
		model = InsuranceExcludedService
		fields = ['excluded_service']
		widgets = {
			'excluded_service': forms.Select(attrs={
			'class' : 'forms form-control select2',
				}),
			}

class CreateServiceForm(forms.ModelForm):
	
	class Meta:
		model = Service
		fields = ['service_name', 'service_discounted_price', 'service_price'
					]
		
		widgets = {
			
			'service_name': forms.TextInput(attrs={
			'class' : 'forms form-control',
			'id' : 'service-name-id'
				}),
			'service_discounted_price': forms.NumberInput(attrs={
			'class' : 'forms form-control',
			'id' : 'service-team-id'
				}),
			'service_price': forms.NumberInput(attrs={
			'class' : 'forms form-control',
			'id' : 'service-price-id'

				}),
			}

"""
class ServiceTeamForm(forms.ModelForm):
	
	class Meta:
		model = ServiceTeam
		fields = ['service_name', 'service_team', 'service_price'
					]
		
		widgets = {
			
			'service_name': forms.TextInput(attrs={
			'class' : 'forms form-control',
			'id' : 'service-id',
				}),
			'service_team': forms.Select(attrs={
			'class' : 'forms form-control',
				}),
			'service_price': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			}
"""
class VisitingBillForm(forms.ModelForm):
	
	class Meta:
		model = VisitingCardPrice
		fields = ['service', 'visiting_price', 'discounted_price'
					]
		
		widgets = {
			'service': forms.Select(attrs={
			'class' : 'select2 form-control',
			'id' : 'service-id',

				}),
			'visiting_price': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			'discounted_price': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			}


class AssignVisitingCardForm(forms.ModelForm):

	
	class Meta:
		model = VisitBillDetail
		fields = [ 'visiting_card', 'patient' ]
		
		widgets = {
			'visiting_card': forms.Select(attrs={
			'class' : 'select2 form-control',
			'id': 'visiting-card-id'

				}),
			'patient': forms.Select(attrs={
			'class' : 'select2 form-control',
			'id': 'patient-id'
				}),
			
			}


class VisitBillDiscountForm(forms.ModelForm):

	class Meta:
		model = VisitBillDetail
		fields = [ 'discount']
		
		widgets = {
			'discount': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),
			}

class VisitBillInsuranceForm(forms.ModelForm):

	class Meta:
		model = VisitBillDetail
		fields = [ 'insurance']
		
		widgets = {
			'insurance': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),
			}
"""
class PatientInsuranceForm(forms.ModelForm):

	class Meta:
		model = PatientInsurance
		fields = [ 'insurance_name', 'monetary_limit']
		
		widgets = {
			'insurance_name': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			'monetary_limit': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			}
"""
class InsuranceExcludedForm(forms.ModelForm):

	class Meta:
		model = InsuranceExcludedService
		fields = [ 'excluded_service']
		
		widgets = {
			'excluded_service': forms.SelectMultiple(attrs={
			'class' : 'select2 form-control',
			'id' : 'excluded-service',
				
				}),
			
			}


class ServiceForm(forms.ModelForm):

	class Meta:
		model = ServiceBillDetail
		fields = [ 'service']
		
		widgets = {
			'service': forms.Select(attrs={
			'class' : 'select2 form-control',
			'id' : 'service-id',
				
				}),
			
			}


class ServiceBillDetailForm(forms.ModelForm):

	class Meta:
		model = ServiceBillDetail
		fields = [ 'discount','insurance']
		
		widgets = {
			'discount': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),
			'insurance': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),

			}

class LabTestPriceForm(forms.ModelForm):

	class Meta:
		model = LabTestPrice
		fields = [ 'test','test_price', 'test_discounted_price']
		
		widgets = {
			'test': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),
			'test_price': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),

			'test_discounted_price': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			}
			