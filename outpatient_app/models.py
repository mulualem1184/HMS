from django.db import models
from pharmacy_app.models import *
from django.contrib.auth import get_user_model
from core.models import * 
from staff_mgmt.models import Employee
import datetime
# Create your models here.



USER = get_user_model()



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
"""
class PatientVitalSign(models.Model):
	symptom_status = (
		('active','active'),
		('not_active','not_active'),
		)
	temperature_unit = (
		('Fahrenheit','Fahrenheit'),
		('Celcius','Celcius'),
		)

	patient = models.ForeignKey(Patient,on_delete= models.SET_NULL, null=True)
	pulse_rate = models.FloatField(null=True,blank=True)	
	temperature = models.FloatField(null=True,blank=True)
	temperature_unit = models.CharField(max_length=100,null=True,blank=True, choices=temperature_unit)
	blood_pressure = models.FloatField(null=True,blank=True)
	active = models.CharField(max_length=100,null=True,blank=True, choices=symptom_status)
	registered_on = models.DateTimeField(null=True)
"""


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

class ServiceTeam(models.Model):
	team = models.ForeignKey(OutpatientTeam,  on_delete= models.SET_NULL, null=True)	
	service_provider = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True)
	def __str__(self):
		return  str(self.team.team_name)


class Service(models.Model):

	service_name = models.CharField(max_length=1000, blank=True)
	service_team = models.ForeignKey(ServiceTeam,  on_delete= models.SET_NULL, null=True, blank=True)
	service_price = models.IntegerField(null=True, blank=True)
	service_discounted_price = models.IntegerField(null=True, blank=True)
	def __str__(self):
		return str(self.service_name) + "  by "  + str(self.service_team.team.team_name) + " for " +str(self.service_price)

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

#	visited_department = models.ForeignKey(Department)
	def __str__(self):
		return str(self.patient)
class VisitQueue(models.Model):
	visit = models.ForeignKey(PatientVisit, on_delete= models.SET_NULL, null=True)
	queue_number = models.IntegerField(null=True,blank=True)

#	def __str__(self):
#		return self.visit.patient.first_name + " " + self.visit.patient.last_name + " in " + self.visit.service_room.room + ', Queue: ' +  str(self.queue_number)

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


