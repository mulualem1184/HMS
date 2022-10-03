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

class BedCategory(models.Model):

	category = models.CharField(max_length=1000, null=True, blank=True)

	def __str__(self):
		return self.category 


class Bed(models.Model):

	bed_number = models.IntegerField( null=True)
	ward = models.ForeignKey(Ward,  on_delete= models.SET_NULL, null=True)
	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True, blank=True)
	category = models.ForeignKey(BedCategory, on_delete= models.SET_NULL, null=True, blank=True)

	def __str__(self):
		return  str(self.ward) + " Bed " + str(self.bed_number) + " - " + str(self.category)

	@property
	def bed_patient(self):
		if self.patient:
			return  str(self.patient.full_name) + " in " + str(self.category)

	@property
	def bed_with_patient(self):
		bed = Bed.objects.filter(patient__isnull=False)
		return  str(bed.count())

	@property
	def return_ward_patients(self):
		beds = Bed.objects.filter(patient__isnull=False)
		patients = []
		for bed in beds:
			patients.append(bed.patient)
		return patients
	"""
	@property
	def bed_release_date(self):
		if self.patient:
			if PatientStayDurationPrediction.get(patient=self.patient):
				prediction
				return self.bed_release_date is None
	"""
class BedReleaseDate(models.Model):
	bed_release_date_status = (
		('active', 'active'),
		('not_active', 'not_active'),       
		)

	bed = models.ForeignKey(Bed, on_delete=models.CASCADE)	
	bed_release_date = models.DateField(null=True, blank=True)
	status = models.CharField(max_length=100,choices=bed_release_date_status, null=True, blank=True)

	def __str__(self):
		return  str(self.bed.ward) + " Bed " + str(self.bed.bed_number) + " - " + str(self.bed.category) + "   Release Date:  " + str(self.bed_release_date)

	"""
	@property
	def bed_release_date(self):
		if self.bed.patient:
			return
			if bed_release_date:
				prediction
				return self.bed_release_date is None
	"""
class PatientStayDurationPrediction(models.Model):
	prediction_status = (
		('active', 'active'),
		('not_active', 'not_active'),       
		)

	duration_units = (
		('days', 'days'),
		('weeks', 'weeks'),       
		('months', 'months'),       

		)

	patient = models.ForeignKey(Patient, on_delete=models.CASCADE)	
	duration = models.IntegerField(blank=True, null=True)
	duration_unit = models.CharField(max_length=100,choices=duration_units, null=True, blank=True)
	status = models.CharField(max_length=100,choices=prediction_status, null=True, blank=True)


class RoomPrice(models.Model):
	room = models.ForeignKey(Bed, on_delete=models.CASCADE)	
	room_price = models.IntegerField(blank=True, null=True)
	active = models.BooleanField(default=True)

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
			return  str(self.team.team_name) + str(self.ward_service_provider.full_name)

class WardNurseTeam(models.Model):
	team = models.ForeignKey(InpatientTeam,  on_delete= models.SET_NULL, null=True)	
	nurse = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True)
	def __str__(self):
		if self.nurse:
			return  str(self.team.team_name) + str(self.nurse.full_name)
		else:
			return  str(self.team.team_name)

class WardTeamBed(models.Model):
	team = models.ForeignKey(WardTeam,  on_delete= models.SET_NULL, null=True, blank=True)	
	nurse_team = models.ForeignKey(WardNurseTeam,  on_delete= models.SET_NULL, null=True, blank=True)
	bed = models.ForeignKey(Bed,  on_delete= models.SET_NULL, null=True)
	"""
	def __str__(self):
		if self.team:	
			return  str(self.team.team.team_name)
		elif self.nurse_team:
			return str(self.nurse_team.team.team_name)
	"""
class ServiceProviderBed(models.Model):
	service_provider = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True)
	bed = models.ForeignKey(Bed,  on_delete= models.SET_NULL, null=True)

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

class AdmissionPriorityLevel(models.Model):
	priority_status = (
		('active', 'active'),
		('not_active', 'not_active'),       
		)
	priority_level = (
		('high', 'high'),
		('medium_high', 'medium_high'),  
		('medium', 'medium'),  
		('medium_low', 'medium_low'),  
		('medium_low', 'medium_low'),  
		)

	patient = models.ForeignKey(to=Patient, on_delete=models.SET_NULL, null=True, blank=True)	
	priority = models.CharField(max_length=100,choices=priority_level, null=True, blank=True)
	status = models.CharField(max_length=100,choices=priority_status, null=True, blank=True)
	
	def __str__(self):
		return  str(self.priority)

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
	
#	def __str__(self):
#		return  str(self)

