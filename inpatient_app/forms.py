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
#drug prescription
class PrescriptionInfoForm2(forms.ModelForm):
	class Meta:
		model = DrugPrescription
		fields = [ 'info']
		widgets = {			
			'info': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			}


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

class CreateBuildingForm(forms.ModelForm):
	class Meta:
		model = HospitalUnit
		fields = ['unit_name']
		widgets = {			
			'unit_name': forms.TextInput(attrs={
			'class' : 'form-control forms',

				}),
		
			}

class CreateRoomForm(forms.ModelForm):
	class Meta:
		model = Ward
		fields = ['hospital_unit','name' ,'by_gender','category']
		widgets = {			
			'hospital_unit': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			'name': forms.TextInput(attrs={
			'class' : 'form-control forms',

				}),
			'by_gender': forms.Select(attrs={
			'class' : 'form-control select2',

				}),
			'category': forms.Select(attrs={
			'class' : 'form-control select2',

				}),
		
			}

class CreateWardForm(forms.ModelForm):
	class Meta:
		model = BedCategory
		fields = ['category']
		widgets = {			
			'category': forms.TextInput(attrs={
			'class' : 'form-control forms',

				}),
		
			}

class CreateBedForm(forms.ModelForm):
	class Meta:
		model = Bed
		fields = ['name']
		widgets = {			
			'name': forms.TextInput(attrs={
			'class' : 'form-control forms',
			'name' : 'bed_id',

				}),
		
			}

class RoomFieldForm(forms.ModelForm):
	class Meta:
		model = Bed
		fields = ['ward']
		widgets = {			
			'ward': forms.Select(attrs={
			'class' : 'form-control select2',

				}),
		
			}

class BedCategoryForm(forms.ModelForm):
	class Meta:
		model = BedCategory
		fields = ['category']
		widgets = {			
			'category': forms.TextInput(attrs={
			'class' : 'form-control forms',

				}),
		
			}
class BedForm(forms.ModelForm):
	"""
	bed = forms.Select(Bed.objects.order_by('category'))
	
	bed = forms.ModelChoiceField(
		queryset=Bed.objects.all().order_by('category__category')
    )
	"""
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
class AllocateBedForm(forms.ModelForm):
	class Meta:
		model = BedReleaseDate
		fields = ['bed']
				
		widgets = {			
			'bed': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'bed',

				}),
		
			}
"""		
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
		fields = ['diagnosis','comments','info']
		widgets = {			
			'diagnosis': forms.TextInput(attrs={
			'class' : 'form-control forms',
		
				}),
			'info': forms.Select(attrs={
			'class' : 'form-control select2',

				}),
			'comments': forms.Textarea(attrs={
			'class' : 'form-control forms',
				}),
		
			}


class RoomPriceForm(forms.ModelForm):
	class Meta:
		model = RoomPrice
		fields = ['room_price','discounted_price']
		widgets = {			
			'room_price': forms.NumberInput(attrs={
			'class' : 'form-control forms',
				}),
			'discounted_price': forms.NumberInput(attrs={
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


class InpatientReasonForm(forms.ModelForm):
	class Meta:
		model = InpatientReason
		fields = ['reason']

		widgets = {						
			'reason': forms.Textarea(attrs={
			'class' : 'form-control forms',
			'rows' : 4,
						
			

				}),
}

class InpatientCarePlanForm(forms.ModelForm):
	class Meta:
		model = InpatientCarePlan
		fields = ['care_plan']

		widgets = {						
			'care_plan': forms.Textarea(attrs={
			'class' : 'form-control forms',
			'rows' : 4,

				}),
}

class InpatientAssessmentForm(forms.ModelForm):
	class Meta:
		model = InpatientAdmissionAssessment
		fields = ['general_appearance', 'other_assessment']

		widgets = {						
			'general_appearance': forms.Textarea(attrs={
			'class' : 'form-control forms',
			'rows' : 4,

				}),
			'other_assessment': forms.Textarea(attrs={
			'class' : 'form-control forms',
			'rows' : 4,

				}),

}

class BedReleaseDateForm(forms.ModelForm):
	class Meta:
		model = BedReleaseDate
		fields = ['bed_release_date']

		widgets = {						
			'bed_release_date': forms.TextInput(attrs={
			'class' : 'form-control forms',

				}),


}

class StayDurationPredictionForm(forms.ModelForm):
	DateTimeInput = partial(forms.DateTimeInput, {'class':'datepicker'})	
	class Meta:
		model = PatientStayDurationPrediction
		fields = ['start_date', 'end_date']

		widgets = {						
			'start_date': forms.NumberInput(attrs={
			'class' : 'form-control forms',

				}),
			'end_date': forms.NumberInput(attrs={
			'class' : 'form-control forms',

				}),


}


class WardAdmissionPriorityForm(forms.ModelForm):

	class Meta:
		model = AdmissionPriorityLevel
		fields = ['priority']

		widgets = {						
			'priority': forms.Select(attrs={
			'class' : 'form-control forms',

				}),

}

class AssignNurseToBedForm(forms.ModelForm):

	class Meta:
		model = WardTeamBed
		fields = ['bed']

		widgets = {						
			'bed': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'room-id',

				}),
			}

class AllocateNurseToBedForm(forms.ModelForm):

	class Meta:
		model = ServiceProviderBed
		fields = ['bed']

		widgets = {						
			'bed': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'bed-id',

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
		fields = ['nurse']

		widgets = {						
			'team': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'nurse-id',

				}),
			}

class AssignNurseToTeamForm(forms.ModelForm):

	class Meta:
		model = WardNurseTeam
		fields = [ 'nurse']


		widgets = {						
			'nurse': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'service-provider-id',

				}),
			}

class AssignDoctorToTeamForm(forms.ModelForm):

	class Meta:
		model = WardTeam
		fields = [ 'ward_service_provider']


		widgets = {						
			'ward_service_provider': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'service-provider-id',

				}),

			}


class CreateDoctorTeamForm(forms.ModelForm):

	class Meta:
		model = InpatientTeam
		fields = [ 'team_name']

		widgets = {						
			'team_name': forms.TextInput(attrs={
			'class' : 'form-control forms',

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

class DischargeSummaryForm(forms.ModelForm):
	class Meta:
		model = WardDischargeSummary 
		fields = ['discharge_condition',
					'significant_findings',
					'summary'
					]
		widgets = {			
			'discharge_condition': forms.Select(attrs={
			'class' : 'form-control forms',
				}),
			'significant_findings': forms.TextInput(attrs={
			'class' : 'form-control forms',
				}),
			'summary': forms.Textarea(attrs={
			'class' : 'form-control forms',
				}),
		
			}

class IPDTreatmentPlanForm(forms.ModelForm):
	class Meta:
		model = IPDTreatmentPlan 
		fields = ['patient',
					'name',
					'status',
					'description',

					]
		widgets = {			
			'patient': forms.Select(attrs={
			'class' : 'form-control forms',
			'id' : 'plan-patient-id',

				}),
			'name': forms.TextInput(attrs={
			'class' : 'form-control forms',
				}),
			'status': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			'description': forms.Textarea(attrs={
			'class' : 'form-control forms',
			'id' : ''
				}),		
			}

class TolerableDifferenceForm(forms.ModelForm):
	class Meta:
		model = TolerableTimeDifference
		fields = ['tolerable_earliness','tolerable_earliness_unit',
					'tolerable_lateness','tolerable_lateness_unit'
		]
		widgets = {			
			'tolerable_earliness': forms.NumberInput(attrs={
			'class' : 'form-control forms',
				}),
			'tolerable_lateness': forms.NumberInput(attrs={
			'class' : 'form-control forms',
				}),
			'tolerable_lateness_unit': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			'tolerable_earliness_unit': forms.Select(attrs={
			'class' : 'form-control select2',
				}),

			}

class PerformPlanForm(forms.ModelForm):
	class Meta:
		model = PerformPlan 
		fields = [
					'note',
					]
		widgets = {			
			'note': forms.Textarea(attrs={
			'class' : 'form-control forms',
			'id' : ''
				}),		
			}

class ManualTreatmentForm(forms.ModelForm):
	class Meta:
		model = Treatment 
		fields = [
					'name',
					'description',

					]
		widgets = {			
			'name': forms.TextInput(attrs={
			'class' : 'form-control forms',
				}),
			'description': forms.Textarea(attrs={
			'class' : 'form-control forms',
			'id' : ''
				}),		
			}

class DynamicTreatmentForm(forms.ModelForm):
	class Meta:
		model = IPDTreatmentPlan 
		fields = [
					'treatment',

					]
		widgets = {			
			'treatment': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			}
