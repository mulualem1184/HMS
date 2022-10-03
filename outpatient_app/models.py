from django.db import models
from pharmacy_app.models import *
from django.contrib.auth import get_user_model
from core.models import * 
from lis.models import LaboratoryTestResult
from staff_mgmt.models import Employee
from radiology.models import ImagingReport

import datetime
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey
# Create your models here.



USER = get_user_model()



class OutpatientChiefComplaint(models.Model):
    complaint = models.CharField(max_length=100,)
    active = models.BooleanField(default=True)
    patient = models.ForeignKey(to=Patient, on_delete=models.CASCADE, null=True, blank=True)

#    def __str__(self):
#        return self.compliant

class TeamSetting(models.Model):
	team_setting = (
		('Team','Team'),
		('Individual','Individual'),
		('Both','Both'),
		)

	setting = models.CharField(max_length=100,null=True,blank=True, choices=team_setting)
	registered_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)	
	active = models.BooleanField(default=True)
	def __str__(self):
		return self.setting

"""
class PatientReferralLocation(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
"""

class PatientArrivalDetail(models.Model):
    # stores details of patient,
    # including patient info, case type, date
    AVPU_CHOICES = [
        (0, 'ALERT'),
        (1, 'REACTS TO VOICE'),
        (2, 'REACTS TO PAIN'),
        (3, 'UNRESPONSIVE'),
    ]
    MOBILITY_CHOICES = [
        (0, 'Walking'),
        (1, 'With help'),
        (2, 'Stretcher/Immobile'),
    ]
    registered_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    arrival_date = models.DateTimeField(default=timezone.now, verbose_name='Date and Time of Arrival')
#   was_referred = models.BooleanField(default=False)
#   referred_from = models.ForeignKey(to=PatientReferralLocation, null=True, on_delete=models.SET_NULL)
    pre_hospital_care = models.CharField(verbose_name="Was pre-hospital care/first aid given?", max_length=300, default='')
    date_of_illness = models.DateTimeField(default=timezone.now, blank=True)
    injury_mechanism = models.CharField(verbose_name="Mechanism of injury", max_length=400, null=True, blank=True)
    chief_complaint = models.ForeignKey(to=OutpatientChiefComplaint,on_delete=models.SET_NULL, null=True)
    vital_sign = models.ForeignKey(to=PatientVitalSign, on_delete=models.CASCADE, null=True, blank=True)
    triage_treatment = models.TextField(verbose_name="Treatment and Investigation on Triage", null=True, blank=True)
    avpu = models.IntegerField(verbose_name='AVPU', choices=AVPU_CHOICES, null=True, blank=True)
    mobility = models.IntegerField(choices=MOBILITY_CHOICES, null=True, blank=True, default=None)
    patient = models.ForeignKey(to=Patient, on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField(default=True)


class PatientAnthropometry(models.Model):
	
	patient = models.ForeignKey(Patient,on_delete= models.SET_NULL, null=True)
	height = models.FloatField(null=True,blank=True)
	weight = models.FloatField(null=True,blank=True)


class PatientSymptom(models.Model):
	symptom_status = (
		('active','active'),
		('not_active','not_active'),
		)
	patient = models.ForeignKey(Patient,on_delete= models.SET_NULL, null=True)
	symptom = models.CharField(max_length=100,null=True,blank=True)	
	active = models.CharField(max_length=100,null=True,blank=True, choices=symptom_status)

class PatientAllergy(models.Model):
	allergy_status = (
		('active','active'),
		('not_active','not_active'),
		)
	patient = models.ForeignKey(Patient,on_delete= models.SET_NULL, null=True)
	allergy = models.CharField(max_length=100,null=True,blank=True)	
	reaction = models.CharField(max_length=5000,null=True,blank=True)	

	active = models.CharField(max_length=100,null=True,blank=True, choices=allergy_status)
	registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)

	registered_on = models.DateTimeField(null=True)


class PatientHabit(models.Model):
	habit_status = (
		('active','active'),
		('not_active','not_active'),
		)
	habit_duration_unit = (
		('days','days'),
		('weeks','weeks'),
		('months','months'),
		('years','years'),
		)

	patient = models.ForeignKey(Patient,on_delete= models.SET_NULL, null=True)
	habit = models.CharField(max_length=100,null=True,blank=True)	
	habit_duration = models.IntegerField(null=True,blank=True)
	habit_duration_unit = models.CharField(max_length=100,null=True,blank=True, choices=habit_duration_unit)

	active = models.CharField(max_length=100,null=True,blank=True, choices=habit_status)
	registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)

	registered_on = models.DateTimeField(null=True)


class PatientHistory(models.Model):
	"""
	diagnosis history: information regarding history of disease of a patient
	"""
	patient = models.ForeignKey(Patient,on_delete= models.SET_NULL, null=True)
	diagnosis = models.ForeignKey(PathologicalFindings, on_delete= models.SET_NULL, null=True, blank=True)
	drug = models.ForeignKey(Dosage, on_delete= models.SET_NULL, null=True, blank=True)
	treatment = models.CharField(max_length=100,null=True,blank=True)


class MaternalPatient(models.Model):
	pregnancy_status=(
		('Pregnant','Pregnant'),
		('Not_Pregnant','Not_Pregnant'),
		)
	patient = models.ForeignKey(Patient,on_delete= models.SET_NULL, null=True)
	pregnancy_status = models.CharField(max_length=200, choices=pregnancy_status, null=True)
	LMP= models.DateField(null=True) #Last Menstrual Period

class OutpatientTeam(models.Model):
	team_name = models.CharField(max_length=1000, blank=True)	
	def __str__(self):
		return  str(self.team_name)


class Service(models.Model):

	service_name = models.CharField(max_length=1000, blank=True)
	service_price = models.IntegerField(null=True, blank=True)
	service_discounted_price = models.IntegerField(null=True, blank=True)

	def __str__(self):
		return str(self.service_name)# + " for " +str(self.service_price)
	"""
	@property
	def get(self):

		return PostA.objects.filter(company__pk=self.pk)
	"""
class ServicePrice(models.Model):

	service = models.ForeignKey(Service,  on_delete= models.SET_NULL, null=True)
	price = models.IntegerField(null=True, blank=True)
	discounted_price = models.IntegerField(null=True, blank=True)
	active = models.BooleanField(default=True)
	effective_date = models.DateTimeField(null=True)

class ServiceTeam(models.Model):
	service = models.ForeignKey(Service,  on_delete= models.SET_NULL, null=True, related_name='team_set')
	team = models.ForeignKey(OutpatientTeam,  on_delete= models.SET_NULL, null=True)	
	service_provider = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True)
#	service = TreeForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True, related_name='children')

	def __str__(self):
#		if not self.level:
#			self.level = 0
		return  str(self.team.team_name) + str(self.service_provider)
#	class MPTTMeta:
#		order_insertion_by = ['name']

class ServiceCopy(models.Model):
	service = models.ForeignKey(Service,  on_delete= models.SET_NULL, null=True)	
	def __str__(self):
		return str(self.service.service_name)
	@property
	def get_team(self):
		return ServiceTeam.objects.filter(service__id=self.service.id)

class ServiceProvider(models.Model):
	service = models.ForeignKey(Service,  on_delete= models.SET_NULL, null=True)
	service_provider = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True)

#	service_provider = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True)

	def __str__(self):
		return str(self.service_provider.user_profile)

class ServiceBuilding(models.Model):
	"""
	building_name : name of the building that gives outpatient care services
	"""
	building_name = models.CharField(max_length=5000, blank=True)
	def __str__(self):
		return self.building_name

class ServiceRoom(models.Model):
	building = models.ForeignKey(ServiceBuilding,  on_delete= models.SET_NULL, null=True)
	room = models.CharField(max_length=5000, blank=True)
	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True, blank=True)

	def __str__(self):
		return self.building.building_name + "  " + self.room


class ServiceRoomProvider(models.Model):
	room = models.ForeignKey(ServiceRoom,  on_delete= models.SET_NULL, null=True, blank=True)
	service_team = models.ForeignKey(OutpatientTeam,  on_delete= models.SET_NULL, null=True, blank=True)

	"""
	def __str__(self):
		return self.service_provider.user_profile + " in " + self.room.room
	"""

class PatientVisit(models.Model):
	"""
	visiting_time: time when patient 
	service_provider: staff member (doctor, councelor, etc..)
	"""
	Visit_status = (
		('Ended', 'Ended'),
		('Pending', 'Pending'),		
		('Active', 'Active'),		
		)
	payment_status = {
		('paid','paid'),
		('not_paid','not_paid'),
	}

	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True)
	visiting_time = models.DateTimeField(null=True)
	service_room = models.ForeignKey(ServiceRoom,  on_delete= models.SET_NULL, null=True)
	visit_status = models.CharField(max_length=100,choices=Visit_status, null=True)
	payment_status = models.CharField(null=True,blank=True, max_length=100, choices=payment_status)
	registered_on = models.DateTimeField(null=True)

#	visited_department = models.ForeignKey(Department)
	def __str__(self):
		return str(self.patient)

class VisitQueue(models.Model):
	visit = models.ForeignKey(PatientVisit, on_delete= models.SET_NULL, null=True)
	queue_number = models.IntegerField(null=True,blank=True)

#	def __str__(self):
#		return self.visit.patient.first_name + " " + self.visit.patient.last_name + " in " + self.visit.service_room.room + ', Queue: ' +  str(self.queue_number)

class FollowUp(models.Model):
	"""
	visiting_time: time when patient 
	service_provider: staff member (doctor, councelor, etc..)
	"""

	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True)
	visit = models.ForeignKey(PatientVisit,  on_delete= models.SET_NULL, null=True, blank=True)
	appointment_time = models.DateTimeField(null=True)
	ordered_by = models.ForeignKey(Employee, on_delete= models.SET_NULL, null=True)
	registered_on = models.DateTimeField(null=True)

#	visited_department = models.ForeignKey(Department)
	def __str__(self):
		return str(self.patient)


class OutpatientIntervention(models.Model):
	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True, blank=True)	
	service_provider = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	intervention_cause = models.CharField( max_length = 1000, blank=True, null=True)
	intervention = models.CharField( max_length = 1000, blank=True, null=True)
	rational = models.CharField( max_length = 1000, blank=True, null=True)
	visit = models.ForeignKey(PatientVisit,  on_delete= models.SET_NULL, null=True, blank=True)
	registered_on = models.DateTimeField(null=True)

class OutpatientMedicalNote(models.Model):

	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True, blank=True)	
	note = models.CharField( max_length = 2000, blank=True, null=True)
	service_provider = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	visit = models.ForeignKey(PatientVisit,  on_delete= models.SET_NULL, null=True, blank=True)
	registered_on = models.DateTimeField(null=True)

class QuestionForPatient(models.Model):
	question = models.CharField( max_length = 2000, blank=True, null=True)
	registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	registered_on = models.DateTimeField(null=True)

	def __str__(self):
		return self.question


class OpdPatientResponse(models.Model):
	response = models.CharField( max_length = 2000, blank=True, null=True)
	question = models.ForeignKey(QuestionForPatient,  on_delete= models.SET_NULL, null=True, blank=True)
	visit = models.ForeignKey(PatientVisit,  on_delete= models.SET_NULL, null=True, blank=True)
	registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	registered_on = models.DateTimeField(null=True)

class PatientAppointment(models.Model):
	"""
	service_provider: staff member (doctor, councelor, etc..) who gives some type of clinical service
	apointment_time: time when 
	"""
	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True)
	service_provider = models.ForeignKey(ServiceProvider,  on_delete= models.SET_NULL, null=True)
	appointment_time = models.DateTimeField(null=True)

class PatientMedication(models.Model):
    Visit_status = (
        ('Ended', 'Ended'),
        ('Pending', 'Pending'),     
        ('Active', 'Active'),       
        )

    patient = models.ForeignKey(to=Patient, on_delete=models.SET_NULL, null=True, blank=True)
    diagnosis = models.CharField(max_length=100, blank=True, null=True)
#    drug= models.ForeignKey(to=Dosage, on_delete=models.SET_NULL, null=True, blank=True)
    drug_prescription = models.ForeignKey(to=DrugPrescription, on_delete=models.SET_NULL, null=True, blank=True)
    drug_status = models.CharField(max_length=100,choices=Visit_status, null=True)
    date = models.DateField(null=True, blank=True)


class OutpatientMedication(models.Model):
	medication_status = (
		('Ended', 'Ended'),
		('Cancelled', 'Cancelled'),     
		('Active', 'Active'),       
		)
	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True, blank=True)
	visit =  models.ForeignKey(PatientVisit, on_delete=models.CASCADE)	
	drug_prescription = models.ForeignKey(to=DrugPrescription, on_delete=models.SET_NULL, null=True, blank=True)
	drug_status = models.CharField(max_length=100,choices=medication_status, null=True)
	doctor = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	registered_on = models.DateField(null=True, blank=True)

class OutpatientLabResult(models.Model):

	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True, blank=True)
	visit =  models.ForeignKey(PatientVisit, on_delete=models.CASCADE)	
	lab_result = models.ForeignKey(to=LaboratoryTestResult, on_delete=models.SET_NULL, null=True, blank=True)
	doctor = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	registered_on = models.DateField(null=True, blank=True)

class OutpatientRadiologyResult(models.Model):

	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True, blank=True)
	visit =  models.ForeignKey(PatientVisit, on_delete=models.CASCADE)	
	result = models.ForeignKey(to=ImagingReport, on_delete=models.SET_NULL, null=True, blank=True)
	doctor = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	registered_on = models.DateField(null=True, blank=True)

class OutpatientDischargeSummary(models.Model):
	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True, blank=True)
	#discharge_condition = models.CharField(max_length=100,choices=discharge_conditions, null=True)
	significant_findings = models.CharField(max_length=400, null=True)
	summary = models.CharField(max_length=2000, null=True)
	registered_on = models.DateField(null=True, blank=True)
	visit = models.ForeignKey(PatientVisit, on_delete=models.CASCADE, null=True)
	discharged_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)




class SurgeryHistory(models.Model):
    patient = models.ForeignKey(to=Patient, on_delete=models.SET_NULL, null=True, blank=True)
    diagnosis = models.CharField(max_length=100, blank=True, null=True)
    surgery_type = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField(null=True, blank=True)

class PatientMedicalCondition(models.Model):
    patient = models.ForeignKey(to=Patient, on_delete=models.SET_NULL, null=True, blank=True)
    medical_condition = models.CharField(max_length=1000, null=True, blank=True)
    registered_date = models.DateField(null=True, blank=True)
    registered_by = models.ForeignKey(to=USER, on_delete=models.SET_NULL, null=True, blank=True)
