from django.db import models
from pharmacy_app.models import *
from core.models import *
from staff_mgmt.models import Employee

# Create your models here.
class HospitalUnit(models.Model):
	unit_name = models.CharField(null=True, max_length = 100)

class Ward(models.Model):
	ward_number = models.IntegerField( null=True)
	hospital_unit = models.ForeignKey(HospitalUnit,  on_delete= models.SET_NULL, null=True)
	def __str__(self):
		return "Ward " + str(self.ward_number)

class Bed(models.Model):

	bed_number = models.IntegerField( null=True)
	ward = models.ForeignKey(Ward,  on_delete= models.SET_NULL, null=True)
	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True, blank=True)
	category = models.CharField(max_length=1000, null=True, blank=True)

	def __str__(self):
		return str(self.ward) + " Bed " + str(self.bed_number)



class RoomPrice(models.Model):
	room = models.ForeignKey(Bed, on_delete=models.CASCADE)	
	room_price = models.IntegerField(blank=True, null=True)
	def __str__(self):
		return str(self.room_price) + " birr"



class BedPatientAllocation(models.Model):
	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True, blank=True)
	previous_bed = models.ForeignKey(Bed,on_delete= models.SET_NULL, null=True, related_name = 'previous_bed')
	bed = models.ForeignKey(Bed,  on_delete= models.SET_NULL, null=True, related_name='bed')





class InpatientTeam(models.Model):
	team_name = models.CharField(max_length=1000, blank=True)	
	def __str__(self):
		return  str(self.team_name)

class WardTeam(models.Model):
	team = models.ForeignKey(InpatientTeam,  on_delete= models.SET_NULL, null=True)	
	ward_service_provider = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True)
	def __str__(self):
		return  str(self.team.team_name)

class WardNurseTeam(models.Model):
	team = models.ForeignKey(InpatientTeam,  on_delete= models.SET_NULL, null=True)	
	nurse = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True)
	def __str__(self):
		return  str(self.team.team_name)

class WardTeamBed(models.Model):
	team = models.ForeignKey(WardTeam,  on_delete= models.SET_NULL, null=True, blank=True)	
	nurse_team = models.ForeignKey(WardNurseTeam,  on_delete= models.SET_NULL, null=True, blank=True)
	bed = models.ForeignKey(Bed,  on_delete= models.SET_NULL, null=True)

	def __str__(self):
		return  str(self.team.team.team_name)

class TemporaryWardTeamBed(models.Model):
	doctor = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, related_name='doctor')
	nurse = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True)
	
	bed = models.ForeignKey(Bed,  on_delete= models.SET_NULL, null=True)

	def __str__(self):
		return  str(self.team.team.team_name)



"""
class NursePatient(models.Model):
	nurse = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True)
	patient = models.ManyToManyField(Patient)
"""


class InpatientMedicalCondition(models.Model):
	patient = models.ForeignKey(to=Patient, on_delete=models.SET_NULL, null=True, blank=True)
	medical_condition = models.CharField(max_length=1000, null=True, blank=True)
	registered_on = models.DateField(null=True, blank=True)
	registered_by = models.ForeignKey(to=Employee, on_delete=models.SET_NULL, null=True, blank=True)

class PatientSurgeryHistory(models.Model):
	patient = models.ForeignKey(to=Patient, on_delete=models.SET_NULL, null=True, blank=True)
	surgery = models.CharField(max_length=1000, null=True, blank=True)
	registered_on = models.DateField(null=True, blank=True)
	registered_by = models.ForeignKey(to=Employee, on_delete=models.SET_NULL, null=True, blank=True)


class InpatientReason(models.Model):
	inpatient_reason_status = (
		('active', 'active'),
		('not_active', 'not_active'),       
		)

	service_provider = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True)
	patient = models.ForeignKey(to=Patient, on_delete=models.SET_NULL, null=True, blank=True)	
	reason =  models.CharField(max_length=1000, null=True, blank=True) 
	status = models.CharField(max_length=100,choices=inpatient_reason_status, null=True, blank=True)
	registered_on = models.DateField(null=True, blank=True)

	def __str__(self):
		return  str(self.reason)

class InpatientCarePlan(models.Model):
	inpatient_care_plan_status = (
		('active', 'active'),
		('not_active', 'not_active'),       
		)

	service_provider = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True)
	patient = models.ForeignKey(to=Patient, on_delete=models.SET_NULL, null=True, blank=True)	
	care_plan =  models.CharField(max_length=1000, null=True, blank=True) 
	status = models.CharField(max_length=100,choices=inpatient_care_plan_status, null=True, blank=True)
	
	def __str__(self):
		return  str(self.care_plan)


class InpatientAdmissionAssessment(models.Model):
	inpatient_assessment_status = (
		('active', 'active'),
		('not_active', 'not_active'),       
		)

	admitted_from_choices = (
		('OPD', 'OPD'),
		('Emergency Department', 'Emergency Department'),       
		('Other', 'Other'),       
		)

	service_provider = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True)
	patient = models.ForeignKey(to=Patient, on_delete=models.SET_NULL, null=True, blank=True)	
	general_appearance =  models.CharField(max_length=1000, null=True, blank=True) 
	other_assessment =  models.CharField(max_length=1000, null=True, blank=True) 
	admitted_from = models.CharField(max_length=100,choices=admitted_from_choices, null=True, blank=True)
	status = models.CharField(max_length=100,choices=inpatient_assessment_status, null=True, blank=True)
	
	def __str__(self):
		return  str(self.care_plan)

