from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import *
from core.models import *
from inpatient_app.models import PatientSurgeryHistory
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

class PatientRegistrationForm(forms.ModelForm):
	DateInput = partial(forms.DateInput, {'class':'datepicker'})

	
	class Meta:
		model = Patient
		fields = ['first_name', 'last_name', 'sex', 'dob',
					'occupation', 'phone_number', 'address']
		
		widgets = {
			'first_name': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			'last_name': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			'sex': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),
			'dob': forms.DateInput(attrs={
			'class' : 'form-control select2',
			'placeholder': 'Date Of Birth',
				}),
			'occupation': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			'phone_number': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			'address': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			
			}

class TeamSettingForm(forms.ModelForm):
	
	class Meta:
		model = TeamSetting
		fields = ['setting']
		
		widgets = {
			'setting': forms.Select(attrs={
			'class' : 'select2 form-control',
				}),
			}

class ServiceTeamForm(forms.ModelForm):

	class Meta:
		model = ServiceTeam
		fields = ['team', ]
		
		widgets = {
			'team': forms.Select(attrs={
			'class' : 'select2 form-control',

				}),
			}

class OutpatientInterventionForm(forms.ModelForm):

	class Meta:
		model = OutpatientIntervention
		fields = ['intervention_cause','intervention','rational']
		
		widgets = {
			'intervention_cause': forms.Textarea(attrs={
			'class' : 'forms form-control',
			'rows':2,
				}),
			'intervention': forms.Textarea(attrs={
			'class' : 'forms form-control',
			'rows':2,
				}),
			'rational': forms.Textarea(attrs={
			'class' : 'forms form-control',
			'rows':2,
				}),
			}

class OutpatientMedicalNote(forms.ModelForm):

	class Meta:
		model = OutpatientMedicalNote
		fields = ['note']
		
		widgets = {
			'note': forms.Textarea(attrs={
			'class' : 'forms form-control',
				}),
			}

class PatientArrivalForm(forms.ModelForm):

    class Meta:
        model = PatientArrivalDetail
        fields = [
            'pre_hospital_care', 'date_of_illness', 
            'injury_mechanism', 'triage_treatment', 
            'avpu', 'mobility',
        ]
        widgets = {
            'pre_hospital_care': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'If any treatment was given before patient came to hospital ',#to emergency room 
            }),

            'triage_treatment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'If any treatment was given before patient was admitted to OPD',#to emergency room 
            }),
            'injury_mechanism': forms.Textarea(attrs={
                'class': 'form-control',
                 'cols': 30,
                 'rows': 10,
				'placeholder': 'How patient was injured or became sick',

                #'placeholder': 'If any treatment was given before patient was admitted to OPD',to emergency room 
            }),

            'avpu': forms.Select(attrs={
                'class': 'form-control'
            }),
            'mobility': forms.Select(attrs={
                'class': 'form-control'
            }),
			'date_of_illness': forms.DateTimeInput(attrs={
			'class' : 'forms form-control',
				}),


			}


class ChiefComplaintForm(forms.ModelForm):

    class Meta:
        model = OutpatientChiefComplaint
        fields = ['complaint', 'patient']
        widgets = {
            'complaint': forms.Textarea(attrs={
                'class': 'form-control',
				'placeholder': 'Main reason patient visited hospital',

            }),
            'patient': forms.Select(attrs={
                'class': 'form-control'
            }),

			}
class VitalSignForm(forms.ModelForm):
    class Meta:
        model = PatientVitalSign
        fields = [
            'pulse_rate', 'temperature', 'temperature_unit',
            'systolic_blood_pressure', 'diastolic_blood_pressure', 
        ]
        widgets = {            
            'pulse_rate': forms.NumberInput(attrs={
                'class' : 'form-control forms',
                'class' : 'form-control forms',
				'placeholder': 'Heart Beat Per Minute',

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

            'temperature_unit': forms.Select(attrs={
                'class' : 'form-control select2',
            }),
        }

class HospitalStructureForm(forms.Form):
	building_name = forms.CharField(widget=forms.TextInput(
		attrs={
			'class': 'form-control',
		}
	))
	room_amount = forms.CharField(widget=forms.NumberInput(
		attrs={
			'class': 'form-control',
		}
	))

class EditRoomForm(forms.ModelForm):
	class Meta:
		model = ServiceRoom
		fields = ['room']
		widgets = {			
						
			'room': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			

			}


class AppointmentForm(forms.ModelForm):
	DateTimeInput = partial(forms.DateTimeInput, {'class':'datepicker'})

	class Meta:
		model = PatientAppointment
		fields = ['patient','appointment_time']
		widgets = {			
						
			'patient': forms.Select(attrs={
			'class' : 'forms form-control',
				}),
			'appointment_time': forms.DateTimeInput(attrs={
			'class' : 'forms form-control',
				}),
			

			}


class AssignPatientForm(forms.ModelForm):
	class Meta:
		model = PatientVisit
		fields = ['patient','service_room']
		widgets = {			
						
			'patient': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'patient',

				}),
			'service_room': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'service_room',

				}),			
			}

class PatientAnthropometryForm(forms.ModelForm):
	class Meta:
		model = PatientAnthropometry
		fields = ['patient','height','weight']
		widgets = {			
						
			'patient': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'patient',

				}),
			'height': forms.NumberInput(attrs={
			'class' : 'forms form-control ',

				}),			
			'weight': forms.NumberInput(attrs={
			'class' : 'forms form-control ',

				}),			

			}
class PatientSymptomForm(forms.ModelForm):
	class Meta:
		model = PatientSymptom
		fields = ['patient','symptom']
		widgets = {			
						
			'patient': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'patient',

				}),
			'symptom': forms.Textarea(attrs={
			'class' : 'forms form-control ',

				}),			
			}

class ReassignRoomForm(forms.ModelForm):
	class Meta:
		model = PatientVisit
		fields = ['service_room']
		widgets = {			
						
			'service_room': forms.Select(attrs={
			'class' : 'form-control select2',
			'id':'service_room'
				}),
			}

"""
class ChangeOrderForm(forms.ModelForm):
	class Meta:
		model = VisitQueue
		fields = ['patient','service_room']
		widgets = {			
						
			'patient': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'patient',

				}),
			'service_room': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'service_room',

				}),			
			}
"""
class ChangeQueueOrderForm(forms.Form):
	queue_number = forms.IntegerField(widget=forms.NumberInput(
		attrs={
			'class': 'form-control',
		}
	))

class PatientPrescriptionForm(forms.ModelForm):

	class Meta:
		model = DrugPrescription
		fields = [ 'drug','diagnosis' ,'units_per_take','frequency','duration_amount','duration_unit','order_category', 'comments']

		widgets = {						
			'drug': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			'diagnosis': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),

			'units_per_take': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			'frequency': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),
			'duration_amount': forms.NumberInput(attrs={
			'class' : 'forms form-control',
				}),			
			'duration_unit': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			'order_category': forms.Select(attrs={
			'class' : 'form-control select2',
				}),
			'comments': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),
			}



class PatientSurgeryHistoryForm(forms.ModelForm):

	class Meta:
		model = PatientSurgeryHistory
		fields = [ 'surgery']

		widgets = {
			'surgery': forms.TextInput(attrs={
			'class' : 'forms form-control',
				}),

	
			}


class AssignServiceProviderForm(forms.ModelForm):

	class Meta:
		model = ServiceRoomProvider
		fields = ['room', 'service_team']

		widgets = {						
			'room': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'room-id',

				}),
			'service_team': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'service-team-id',

				}),
			}
# remind_me

class AssignServiceTeamForm(forms.ModelForm):

	class Meta:
		model = ServiceTeam
		fields = ['team', 'service_provider']

		widgets = {						
			'team': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'room-id',

				}),
			'service_provider': forms.Select(attrs={
			'class' : 'form-control select2',
			'id' : 'service-provider-id',

				}),
			}




class PatientAllergyForm(forms.ModelForm):

	class Meta:
		model = PatientAllergy
		fields = [ 'allergy', 'reaction']

		widgets = {						
			'allergy': forms.TextInput(attrs={
			'class' : 'form-control forms',

				}),
			'reaction': forms.Textarea(attrs={
			'class' : 'form-control forms',

				})

			}


class PatientHabitForm(forms.ModelForm):

	class Meta:
		model = PatientHabit
		fields = [ 'habit','habit_duration','habit_duration_unit' ,'active']

		widgets = {						
			'habit': forms.TextInput(attrs={
			'class' : 'form-control forms',

				}),
			'habit_duration': forms.NumberInput(attrs={
			'class' : 'form-control forms',
				}),			
			'habit_duration': forms.NumberInput(attrs={
			'class' : 'form-control forms',
				}),			
			'habit_duration_unit': forms.Select(attrs={
			'class' : 'form-control forms',
				}),			

			'active': forms.Select(attrs={
			'class' : 'form-control select2',

				}),			


			}

class PatientMedicalConditionForm(forms.ModelForm):

	class Meta:
		model = PatientMedicalCondition
		fields = ['medical_condition']

		widgets = {						
			'medical_condition': forms.TextInput(attrs={
			'class' : 'forms form-control ',

				}),

			}


class DischargeOutpatientForm(forms.ModelForm):
	class Meta:
		model = OutpatientDischargeSummary 
		fields = [
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
