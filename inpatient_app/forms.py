from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from inpatient_app.models import *
from pharmacy_app.models import *
from outpatient_app.models import *
from billing_app.models import *

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
class HospitalStructureForm(forms.Form):

	building_name = forms.CharField(widget=forms.TextInput(
		attrs={
			'class': 'form-control',
		}
	))

	ward_amount = forms.IntegerField(widget=forms.NumberInput(
		attrs={
			'class': 'form-control',
		}
	))
	bed_amount = forms.IntegerField(widget=forms.NumberInput(
		attrs={
			'class': 'form-control',
		}
	))

class BedForm(forms.ModelForm):
	class Meta:
		model = BedPatientAllocation
		fields = ['bed']
		widgets = {			
			'bed': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'bed',

				}),
		
			}
"""
class NursePatientForm(forms.ModelForm):
	class Meta:
		model = NursePatient
		fields = ['nurse','patient']
		widgets = {			
			'nurse': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'nurse',
				}),
			'patient': forms.SelectMultiple(attrs={
			'class' : 'form-control select2',
			'id' : 'patient',
				}),
		
			}
"""
class PatientForm(forms.ModelForm):
	class Meta:
		model = PatientCredit
		fields = ['patient']
		widgets = {			
			'patient': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'patient',

				}),
		
			}
"""
class AssignInpatientForm(forms.ModelForm):
	class Meta:
		model = Patient
		fields = ['treatment_status']
		widgets = {			
			'treatment_status': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'treatment-status',

				}),
		
			}
"""
class InpatientPrescriptionForm(forms.ModelForm):
	class Meta:
		model = DrugPrescription
		fields = ['diagnosis','drug','order_category','comments']
		widgets = {			
			'diagnosis': forms.TextInput(attrs={
			'class' : 'form-control forms',
		
				}),
			'drug': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'drug',

				}),
			'order_category': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			'comments': forms.TextInput(attrs={
			'class' : 'form-control forms',
				}),
		
			}

class InpatientServiceForm(forms.ModelForm):
	class Meta:
		model = InpatientServiceBillDetail
		fields = ['service']
		widgets = {			

			'service': forms.Select(attrs={
			'class' : 'form-control select2',

				}),
		
			}

class RoomPriceForm(forms.ModelForm):
	class Meta:
		model = RoomPrice
		fields = ['room_price']
		widgets = {			
			'room_price': forms.NumberInput(attrs={
			'class' : 'form-control forms',
				}),
		
			}

class ChangePatientBedForm(forms.ModelForm):
	class Meta:
		model = BedPatientAllocation
		fields = ['bed']
		widgets = {			
			'bed': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
		
			}


class InpatientObservationForm(forms.ModelForm):
	class Meta:
		model = InpatientObservation
		fields = ['observation']
		widgets = {			
			'observation': forms.Textarea(attrs={
			'class' : 'form-control select2',
				}),
		
			}


class InpatientDoctorInstructionForm(forms.ModelForm):
	DateTimeInput = partial(forms.DateTimeInput, {'class':'datepicker'})
	class Meta:
		model = InpatientDoctorInstruction
		fields = ['instruction','expected_outcome','instruction_time']
		widgets = {			
			'instruction': forms.Textarea(attrs={
			'class' : 'form-control forms',
				}),
			'expected_outcome': forms.Textarea(attrs={
			'class' : 'form-control forms',
				}),
			'instruction_time': forms.DateTimeInput(attrs={
			'class' : 'form-control forms',
			'id' : ''
				}),
		
			}

class NurseInstructionResponseForm(forms.ModelForm):
	class Meta:
		model = NurseInstructionCheck
		fields = ['intervention']
		widgets = {			
			'intervention': forms.Textarea(attrs={
			'class' : 'form-control select2',
				}),
			}

class NurseIndependentInterventionForm(forms.ModelForm):
	class Meta:
		model = NurseIndependentIntervention
		fields = ['intervention','intervention_cause','rational']
		widgets = {			
			'intervention': forms.Textarea(attrs={
			'class' : 'form-control select2',
				}),
			'intervention_cause': forms.Textarea(attrs={
			'class' : 'form-control select2',
				}),
			'rational': forms.Textarea(attrs={
			'class' : 'form-control select2',
				}),
			}

class NurseEvaluationForm(forms.ModelForm):
	class Meta:
		model = NurseEvaluation
		fields = ['evaluation']
		widgets = {			
			'evaluation': forms.Textarea(attrs={
			'class' : 'form-control forms',
				}),
		
			}



"""
class InpatientReasonForm(forms.ModelForm):
	reason = forms.CharField(widget=forms.Textarea(attrs={
        'rows' : 4,
        'class' : 'form-control forms',
        }))
	class Meta:
		model = InpatientReason
		fields = ['reason']
"""

class InpatientReasonForm(forms.ModelForm):
	class Meta:
		model = InpatientReason
		fields = ['reason']

		widgets = {						
			'reason': forms.Textarea(attrs={
			'class' : 'form-control forms',
			
			
			
			

				}),
}

class InpatientCarePlanForm(forms.ModelForm):
	class Meta:
		model = InpatientCarePlan
		fields = ['care_plan']

		widgets = {						
			'care_plan': forms.Textarea(attrs={
			'class' : 'form-control forms',

				}),
}

class InpatientAssessmentForm(forms.ModelForm):
	class Meta:
		model = InpatientAdmissionAssessment
		fields = ['general_appearance', 'other_assessment']

		widgets = {						
			'general_appearance': forms.Textarea(attrs={
			'class' : 'form-control forms',

				}),
			'other_assessment': forms.Textarea(attrs={
			'class' : 'form-control forms',

				}),

}

class AssignNurseForm(forms.ModelForm):

	class Meta:
		model = WardTeamBed
		fields = ['team', 'nurse_team']

		widgets = {						
			'team': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'room-id',

				}),
			'nurse_team': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'service-team-id',

				}),
			}

class AssignInpatientToTeamForm(forms.ModelForm):

	class Meta:
		model = WardTeam
		fields = ['team', 'ward_service_provider']

		widgets = {						
			'team': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'room-id',

				}),
			'ward_service_provider': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'service-provider-id',

				}),
			}

class AssignNurseToTeamForm(forms.ModelForm):

	class Meta:
		model = WardNurseTeam
		fields = ['team', 'nurse']

		widgets = {						
			'team': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'room-id',

				}),
			'nurse': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'service-provider-id',

				}),
			}

class NurseProgressChartForm(forms.ModelForm):
	class Meta:
		model = NurseProgressChart
		fields = ['appearance', 'observation']
		widgets = {			
			'appearance': forms.Textarea(attrs={
			'class' : 'form-control ',
				}),
			'observation': forms.Textarea(attrs={
			'class' : 'form-control ',
				}),
		
			}



class DrugPrescriptionPharmacistForm(forms.ModelForm):
	class Meta:
		model = DrugPrescription
		fields = ['units_per_take', 'frequency', 'frequency_unit',
					'duration_amount', 'duration_unit']
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
			'duration_amount': forms.NumberInput(attrs={
			'class' : 'form-control forms',
				}),
			'duration_unit': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
		
			}

class DrugAdministrationTimeForm(forms.ModelForm):
	class Meta:
		model = InpatientAdministrationTime
		fields = [ 'time_gap', 'first_time',]
		widgets = {			
			'time_gap': forms.NumberInput(attrs={
			'class' : 'form-control forms',
				}),
			'first_time': forms.TimeInput(attrs={
			'class' : 'form-control forms',
				}),
		
			}

class DoctorInstructionForm(forms.ModelForm):
	class Meta:
		model = InpatientDoctorOrder
		fields = ['instruction']
		widgets = {			
			'instruction': forms.TextInput(attrs={
			'class' : 'form-control forms',
				}),
		
			}



"""
class  SurgeryTypeForm(forms.ModelForm):
	class Meta:
		model = 

class BedForm(forms.Form):
	beds = Bed.objects.all()

	bed = forms.ChoiceField(widget=forms.Select(
		attrs={
			'class': 'form-control select2',
		}
	))
	bed.queryset = beds



class PatientAllocationForm(forms.ModelForm):
	class Meta:
		model = Bed
		fields = ['patient']

		widgets = {			
			'patient': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
		
			}


class BedAllocationForm(forms.ModelForm):
	class Meta:
		model = Ward
		fields = ['patient']

		widgets = {			
			'patient': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
		
			}
"""