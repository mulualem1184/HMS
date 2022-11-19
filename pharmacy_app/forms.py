from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import *
from django.contrib.auth.models import User
import datetime
from django.contrib.admin import site as admin_site
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.contrib.admin.widgets import AdminDateWidget
from functools import partial
from inpatient_app.models import IPDTreatmentPlan
#import autocomplete_light

from django.forms.models import(
	inlineformset_factory,
	modelform_factory,
	modelformset_factory
	)





#Drug profile form
###
class DrugProfileForm(forms.ModelForm):

	
	class Meta:
		model = DrugProfile
		fields = ['commercial_name', 'generic_name', 'NDC', 'tier']

		exclude = ['image']
		
		widgets = {
			'commercial_name': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			'generic_name': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			'NDC': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			'tier': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			
			}
	"""
	def __init__(self, *args, **kwargs):
		super(DrugProfileForm, self).__init__(*args, **kwargs)      
		self.fields['pathological_findings'].widget = (
			RelatedFieldWidgetWrapper(
				self.fields['pathological_findings'].widget,
				self.instance._meta.get_field('pathological_findings').remote_field,
				admin_site,
			)
		)	
	"""
class PrescriptionInfoForm(forms.ModelForm):
	class Meta:
		model = DrugPrescriptionInfo
		fields = ['drug' ,'units_per_take', 'frequency', 'frequency_unit',
					'duration', 'duration_unit']
		widgets = {			
			'units_per_take': forms.NumberInput(attrs={
			'class' : 'form-control forms',
				}),
			'frequency': forms.NumberInput(attrs={
			'class' : 'form-control forms',
				}),
			'frequency_unit': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			'duration': forms.NumberInput(attrs={
			'class' : 'form-control forms',
				}),
			'duration_unit': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			'drug': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
		
			}

class EditPrescriptionInfoForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		planid = kwargs.pop('planid')
		plan = IPDTreatmentPlan.objects.get(id=planid)
		print('plannnn ',plan.id)
		print('pspspspsjnjjjjjj',plan.prescription.info)
		info = plan.prescription.info
		super(EditPrescriptionInfoForm, self).__init__(*args, **kwargs)
		for f in self.fields:
			if hasattr(info,f):
				value = getattr(info,f)
				self.fields[f].initial = value

	class Meta:
		model = DrugPrescriptionInfo
		fields = ['drug' ,'units_per_take', 'frequency', 'frequency_unit',
					'duration', 'duration_unit']
		widgets = {			
			'units_per_take': forms.NumberInput(attrs={
			'class' : 'form-control forms',
				}),
			'frequency': forms.NumberInput(attrs={
			'class' : 'form-control forms',
				}),
			'frequency_unit': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			'duration': forms.NumberInput(attrs={
			'class' : 'form-control forms',
				}),
			'duration_unit': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			'drug': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
		
			}


class DiseaseDrugForm(forms.ModelForm):
	class Meta:
		model = DiseaseDrugModel
		fields = ['drug','pathological_findings']
		widgets = {

			'drug': forms.Select(attrs={
			'class' : 'form-control select2',
				}),			
		
			'pathological_findings': forms.SelectMultiple(attrs={
			'class' : 'form-control select2',
				}),			
			}

class ContraIndicationDrugForm(forms.ModelForm):
	class Meta:
		model = ContraIndicationDrugModel
		fields = ['drug','contraindication']
		widgets = {
			'drug': forms.Select(attrs={
			'class' : 'form-control select2',
				}),		
			'contraindication': forms.SelectMultiple(attrs={
			'class' : 'form-control select2',
				}),			
			}

class SideEffectDrugForm(forms.ModelForm):
	class Meta:
		model = SideEffectDrugModel
		fields = ['drug','side_effect']
		widgets = {
			'drug': forms.Select(attrs={
			'class' : 'form-control select2',
				}),		
			'side_effect': forms.SelectMultiple(attrs={
			'class' : 'form-control select2',
				}),			
			}



class DiseaseForm(forms.ModelForm):
	class Meta:
		model = PathologicalFindings
		fields = ['disease']
		widgets = {
			'disease': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			}

class DrugFieldForm(forms.ModelForm):
	class Meta:
		model = Route
		fields = ['drug']
		widgets = {
			'drug': forms.Select(attrs={
			'class' : 'form-control select2',
				}),			
			}

"""
class ContraIndicationForm(forms.ModelForm):
	class Meta:
		model = ContraIndication
		fields = ['disease']
		widgets = {
			'disease': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			}
"""
class SideEffectForm(forms.ModelForm):
	class Meta:
		model = PathologicalFindings
		fields = ['disease']
		widgets = {
			'disease': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			}

			


class RouteForm(forms.ModelForm):

	class Meta:
		model = Route
		fields = ['route']

		widgets = {
			'route': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			}

class FullRouteForm(forms.ModelForm):
	
	class Meta:
		model = Route
		fields = ['drug','route']

		widgets = {
			'drug': forms.Select(attrs={
			'class' : 'form-control select2',
				}), 
			'route': forms.Select(attrs={
			'class' : 'form-control select2',
				}),

			}

class DosageForm(forms.ModelForm):

	class Meta:
		model = Dosage
		fields = ['age_range', 'weight_range', 'dosage_amount', 'unit','dosage_form']
		
		widgets = {
			'age_range': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			'weight_range': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			'dosage_amount': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			'unit': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			'dosage_form': forms.Select(attrs={
			'class' : 'form-control select2',
				}),							
			}


###


#supply form
###
class SupplyForm(forms.ModelForm):

	class Meta:
		model =  DrugSupply
		fields = ['purchasing_cost','supplier','slot_no']

		widgets = {
			
			'purchasing_cost': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			'supplier': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			'slot_no': forms.Select(attrs={
			'class' : 'forms form-control',
				}),
			}

class StockSupplyForm(forms.ModelForm):

	class Meta:
		model =  DrugSupply
#		autocomplete_fields = ("stock_slot_no")
		fields = ['purchasing_cost','supplier','stock_slot_no']

		widgets = {
			
			'purchasing_cost': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			'supplier': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			'stock_slot_no': forms.Select(attrs={
			'class' : 'form-control select2',
				}),

#			"stock_slot_no":autocomplete_light.TextWidget("StockSupplyAutocomplete"),
			}

class StockSlotForm(forms.ModelForm):

	class Meta:
		model =  DrugSupply
#		autocomplete_fields = ("stock_slot_no")
		fields = ['stock_slot_no']

		widgets = {
			
			'stock_slot_no': forms.Select(attrs={
			'class' : 'form-control select2',
				}),

#			"stock_slot_no":autocomplete_light.TextWidget("StockSupplyAutocomplete"),
			}
 
class BatchForm(forms.ModelForm):
	
	class Meta:
		model = Batch
		fields = ['batch_no','quantity', 'drug']

		widgets = {
			
			'batch_no': forms.NumberInput(attrs={
			'class' : 'forms form-control ',
				}),
			'quantity': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			'drug': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			}

class NoProcurementBatchForm(forms.ModelForm):
	
	class Meta:
		model = Batch
		fields = ['quantity', 'drug']

		widgets = {
			
			'quantity': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			'drug': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			}

class ExpirationDateForm(forms.ModelForm):
	#DateTimeInput = partial(forms.DateTimeInput, {'class':'datepicker'})

	class Meta:
		model = DrugExpiration
		fields = ['manufacturing_date','expiration_date']
		#expiration_date = forms.DateField(widget=AdminDateWidget())
		
		widgets = {
			'manufacturing_date': forms.DateTimeInput(attrs={
			'class' : 'forms form-control',
				}),
			
			'expiration_date': forms.DateTimeInput(attrs={
			'class' : 'forms form-control',
				}),							
			}

		
class ProcurementForm(forms.ModelForm):
	class Meta:
		model = Procurement
		fields = ['procurement_no']

		widgets = {
			
			'procurement_no': forms.TextInput(attrs={
			'class' : 'forms form-control ',
				}),
			
			}

class ProcurementDispensaryForm(forms.ModelForm):
	class Meta:
		model = DispensaryShelf
		fields = ['dispensary']

		widgets = {
			
			'dispensary': forms.Select(attrs={
			'class' : 'forms form-control select2 ',
				}),
			
			}

class ProcurementDetailForm(forms.ModelForm):
	class Meta:
		model = ProcurementDetail
		fields = ['drug', 'quantity']
		
		widgets = {			
			'drug': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			'quantity': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			}


class DiseaseForm(forms.ModelForm):
	class Meta:
		model = PathologicalFindings
		fields= ['disease']

		widgets = {			
			'disease': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			}

class ContraIndicationForm(forms.ModelForm):
	class Meta:
		model = ContraIndication
		fields = ['condition']

		widgets = {			
			'condition': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			}
class SideEffectForm(forms.ModelForm):
	class Meta:
		model = SideEffect
		fields = ['side_effect']

		widgets = {			
			'side_effect': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			}
class AgeRangeForm(forms.ModelForm):

	class Meta:
		model = AgeRange
		fields = ['minimum_age', 'maximum_age']

		widgets = {			
			'minimum_age': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			
			'maximum_age': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			}

class WeightRangeForm(forms.ModelForm):

	class Meta:
		model = WeightRange
		fields = ['minimum_weight', 'maximum_weight']

		widgets = {			
			'minimum_weight': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			
			'maximum_weight': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			}

"""
"""
#DrugCorelationForm
class DrugInteractionForm(forms.ModelForm):
	class Meta:
		model = DrugInteraction
		fields = ['effector_drug', 'affected_drug', 'relation']

		widgets = {			
			'effector_drug': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			
			'affected_drug': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			'relation': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),

			}
class FoodInteractionForm(forms.ModelForm):
	class Meta:
		model = DrugCorelation
		fields = ['drug', 'food', 'relation']

		widgets = {			
			'drug': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			
			'food': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			'relation': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			}
class AlcoholInteractionForm(forms.ModelForm):
	class Meta:
		model = DrugCorelation
		fields = ['drug', 'alcohol', 'relation']

		widgets = {			
			'drug': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			
			'alcohol': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			'relation': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			}
class DiseaseInteractionForm(forms.ModelForm):
	class Meta:
		model = DrugCorelation
		fields = ['drug', 'pathological_findings', 'relation']

		widgets = {			
			'drug': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			
			'pathological_findings': forms.Select(attrs={
			'class' : 'forms form-control',
				}),
			'relation': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			}
class IntakeModeForm(forms.ModelForm):
	class Meta:
		model = IntakeMode
		fields = ['drug','food','additional_info']

		widgets = {			
			'drug': forms.SelectMultiple(attrs={
			'class' : 'form-control select2',
				}),
			
			'additional_info': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			'food': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			}


#drug prescription
class PrescriptionForm(forms.ModelForm):
	"""
	diagnosis = forms.CharField(widget=forms.TextInput(
		attrs={
			'class': 'forms form-control',
		}
	))
	def save(self, commit=True):
		diagnosis_input = self.cleaned_data['diagnosis']
		diagnosis = PathologicalFindings.objects.get_or_create(disease=diagnosis_input)[0]  # returns (instance, <created?-boolean>)
		self.instance.diagnosis = diagnosis
		return super(PrescriptionForm, self).save(commit)
	"""
	class Meta:
		model = DrugPrescription
		fields = ['diagnosis','drug','order_category','comments', 'info']
		widgets = {			
			'diagnosis': forms.TextInput(attrs={
			'class' : 'form-control forms',
		
				}),
			'drug': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'drug',
				}),
			'info': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			'comments': forms.TextInput(attrs={
			'class' : 'form-control forms',
				}),
		
			}


class InventoryStructureForm(forms.Form):
	stock = forms.CharField(widget=forms.TextInput(
		attrs={
			'class': 'form-control',
		}
	))
	shelf_amount = forms.IntegerField(widget=forms.NumberInput(
		attrs={
			'class': 'form-control',
		}
	))
	slot_amount = forms.IntegerField(widget=forms.NumberInput(
		attrs={
			'class': 'form-control',
		}
	))

class DispensaryStructureForm(forms.Form):	
	dispensary = forms.CharField(widget=forms.TextInput(
		attrs={
			'class': 'form-control',
		}
	))
	shelf_amount = forms.IntegerField(widget=forms.NumberInput(
		attrs={
			'class': 'form-control',
		}
	))
	slot_amount = forms.IntegerField(widget=forms.NumberInput(
		attrs={
			'class': 'form-control',
		}
	))

class DispensaryStockForm(forms.ModelForm):
	class Meta:
		model = Dispensary
		fields = ['stock']
		widgets = {									
			'stock': forms.Select(attrs={
			'class' : 'forms form-control select2',
				}),
			

			}


class EditDispensaryShelfForm(forms.ModelForm):
	class Meta:
		model = DispensaryShelf
		fields = ['shelf_no']
		widgets = {			
						
			'shelf_no': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			

			}

class EditStockShelfForm(forms.ModelForm):
	class Meta:
		model = InStockShelf
		fields = ['shelf_no']
		widgets = {			
						
			'shelf_no': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),			
			}


class DrugImageForm(forms.ModelForm):
	class Meta:
		model = DrugImage
		fields = ['drug']

class ActiveImageForm(forms.Form):	
	make_active = forms.BooleanField()




class DrugPriceForm(forms.ModelForm):
	class Meta:
		model = DrugPrice
		fields = ['drug', 'selling_price', 'discounted_price',]
		widgets = {			
						
			'drug': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			'selling_price': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			'discounted_price': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),			

			}




class DiscountForm(forms.ModelForm):
	class Meta:
		model = BillDetail 
		fields = ['discount']
		widgets = {			
			'discount': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),

			}

class DrugDiscountForm(forms.Form):
	class Meta:
		model = BillDetail 
		fields = ['discount']
		widgets = {			
			'discount': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),
			}
class BillForm(forms.ModelForm):
	class Meta:
		model = BillDetail 
		fields = ['bill', 'drug', 'quantity']
		widgets = {			
			'bill': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),
			'drug': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			'quantity': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			}

class SmallBillForm(forms.ModelForm):
	class Meta:
		model = BillDetail
		fields = ['drug', 'quantity']
		widgets = {			
			'drug': forms.Select(attrs={
			'class' : 'form-control select2',
			'id':'id_drug',
				}),
			'quantity': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			}

BillFormSet = inlineformset_factory(
	Bill,
	BillDetail,
	BillForm,
	fields=('drug','quantity')
	)
	

class DispensionForm(forms.ModelForm):
	class Meta:
		model = DispensaryDrug
		fields = ['slot_no']
		widgets = {			
			'slot_no': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),
			}

class PaymentTypeForm(forms.ModelForm):
	class Meta:
		model = DrugDispensed
		fields = ['payment_type']
		widgets = {			
			'payment_type': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),
			}


class PatientForm(forms.ModelForm):
	class Meta:
		model = DrugPrescription
		fields = ['patient']
		widgets = {			
			'patient': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),
			}

class ThresholdForm(forms.ModelForm):
	class Meta:
		model = InventoryThreshold
		fields = ['drug','threshold']
		widgets = {			
			'drug': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),
			'threshold': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			}



	


class DrugRelocationForm(forms.ModelForm):
	class Meta:
		model = DrugRelocationTemp
		fields = ['drug','quantity']
		widgets = {			
			'drug': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),
			'quantity': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			}


class DispensaryDrugForm(forms.ModelForm):
	class Meta:
		model = DispensaryDrug
		fields = ['drug', 'quantity','slot_no',]
		widgets = {			
			'drug': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),
			'quantity': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			'slot_no': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),
			}

class AssignPharmacistForm(forms.ModelForm):
	class Meta:
		model = DispensaryPharmacist
		fields = ['pharmacist']
		widgets = {			
			'pharmacist': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),
			}

class DrugRequestForm(forms.ModelForm):
	class Meta:
		model = DispensaryProcurementRequest
		fields = ['drug', 'quantity']
		widgets = {			
			'drug': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),
			'quantity': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),

			}
