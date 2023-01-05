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

class PartialReconcilationForm(forms.Form):
	amount_paid = forms.IntegerField(widget=forms.NumberInput(
		attrs={
			'class': 'form-control',
		}
	))
			


class InvoiceForm(forms.ModelForm):

	class Meta:
		model = Invoice
		fields = [ 'patient']
		widgets = {
			'patient': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),
			'due_date': forms.DateInput(attrs={
			'class' : 'form-control forms',
				}),

			}


class ItemSaleInfoForm(forms.ModelForm):

	class Meta:
		model = ItemSaleInfo
		fields = [ 'item', 'quantity','discount']

		widgets = {
			'item': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),
			'quantity': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			'discount': forms.CheckboxInput(attrs={
				'class': '',
			})
			}

class PaymentForm(forms.ModelForm):

	class Meta:
		model = Payment
		fields = [ 'amount_paid']
		
		widgets = {
			'amount_paid': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			}


class PrePaymentForm(forms.ModelForm):

	class Meta:
		model = Payment
		fields = ['patient' ,'amount_paid']
		
		widgets = {
			'patient': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),
			'amount_paid': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			}


class CreateItemForm(forms.ModelForm):

	class Meta:
		model = Item
		fields = [ 'name','generic_name','category','item_type',
					'medical_type','measurement_unit','code',
					'available_in_appointment'
		]
		widgets = {
			'name': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			'generic_name': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),

			'category': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),
			'item_type': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),
			'medical_type': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),
			'measurement_unit': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			'code': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			'available_in_appointment': forms.CheckboxInput(attrs={
				'class': '',
			})


			}


class EditItemForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		item_id = kwargs.pop('item_id')
		item = Item.objects.get(id=item_id)
		#print('plannnn ',resource.id)
		super(EditItemForm, self).__init__(*args, **kwargs)
		for f in self.fields:
			if hasattr(item,f):
				value = getattr(item,f)
				self.fields[f].initial = value

	class Meta:
		model = Item
		fields = [ 'name','generic_name','category','item_type',
					'medical_type','measurement_unit','code',
					'available_in_appointment'
		]
		widgets = {
			'name': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			'generic_name': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),

			'category': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),
			'item_type': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),
			'medical_type': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),
			'measurement_unit': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			'code': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			'available_in_appointment': forms.CheckboxInput(attrs={
				'class': '',
			})


			}

class ItemPriceForm(forms.ModelForm):

	class Meta:
		model = ItemPrice
		fields = [ 'sale_price','buy_price','discount_price'
		]
		widgets = {
			'sale_price': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			'buy_price': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			'discount_price': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),

			}

class EditItemPriceForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		price_id = kwargs.pop('price_id')
		price = ItemPrice.objects.get(id=price_id)
		#print('plannnn ',resource.id)
		super(EditItemPriceForm, self).__init__(*args, **kwargs)
		for f in self.fields:
			if hasattr(price,f):
				value = getattr(price,f)
				self.fields[f].initial = value

	class Meta:
		model = ItemPrice
		fields = [ 'sale_price','buy_price','discount_price'
		]
		widgets = {
			'sale_price': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			'buy_price': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			'discount_price': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),

			}


class AssociateItemForm(forms.ModelForm):

	class Meta:
		model = Item
		fields = [ 'drug','lab_test']
		widgets = {

			'drug': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),
			'lab_test': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),

			}
