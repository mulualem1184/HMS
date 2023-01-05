from django.db import models
from pharmacy_app.models import *
from core.models import *
from staff_mgmt.models import Employee
from django import template
from outpatient_app.models import *
from lis.models import *
from datetime import  timedelta
from datetime import  datetime
from dateutil.tz import UTC

# Create your models here.
class HospitalUnit(models.Model):
	unit_name = models.CharField(null=True, max_length = 100)
	registered_on = models.DateField(null=True, blank=True)
	registered_by = models.ForeignKey(to=Employee, on_delete=models.SET_NULL, null=True, blank=True)
	active = models.BooleanField(default=True)
	
	def __str__(self):
		return  str(self.unit_name)

	@property
	def used_bedd_amount(self):
		wards = self.sp_building.all()
		bed_count = 0
		for ward in wards:
			beds = Bed.objects.filter(ward=ward,patient__isnull=False)
			bed_count = bed_count + beds.count()				
			
		return bed_count

class BedCategory(models.Model):

	category = models.CharField(max_length=1000, null=True, blank=True, verbose_name='name')
	registered_on = models.DateField(null=True, blank=True)
	registered_by = models.ForeignKey(to=Employee, on_delete=models.SET_NULL, null=True, blank=True)
	active = models.BooleanField(default=True)

	def __str__(self):
		return self.category 

	
	def filtered_ward(self,):
		wards = self.sp_category.all()
		bed_count = 0
		for ward in wards:
			beds = Bed.objects.filter(ward=ward,patient__isnull=False)
			bed_count = bed_count + beds.count()				
			
		return bed_count

	@property
	def used_bed_amount(self):
		wards = self.sp_category.all()
		bed_count = 0
		for ward in wards:
			beds = Bed.objects.filter(ward=ward,patient__isnull=False)
			bed_count = bed_count + beds.count()				
			
		return bed_count

	@property
	def free_bed_amount(self):
		wards = self.sp_category.all()
		bed_count = 0
		for ward in wards:
			beds = Bed.objects.filter(ward=ward,patient__isnull=True)
			bed_count = bed_count + beds.count()				
			
		return bed_count

	@property
	def total_bed_amount(self):
		wards = self.sp_category.all()
		bed_count = 0
		for ward in wards:
			beds = Bed.objects.filter(ward=ward)
			bed_count = bed_count + beds.count()				
			
		return bed_count

class Ward(models.Model):
	SEX_CHOICES = [
		('MALE','MALE'),
		('FEMALE', 'FEMALE'),
		('MIXED', 'MIXED'),

	]

	name = models.CharField(max_length=50, null=True)
	hospital_unit = models.ForeignKey(HospitalUnit,  on_delete= models.SET_NULL, null=True,related_name='sp_building')
	by_gender = models.CharField(max_length=10, choices=SEX_CHOICES, null=True,blank=True)
	category = models.ForeignKey(BedCategory, on_delete= models.SET_NULL, null=True, blank=True, verbose_name='Ward', related_name='sp_category')

	registered_on = models.DateField(null=True, blank=True)
	registered_by = models.ForeignKey(to=Employee, on_delete=models.SET_NULL, null=True, blank=True)
	active = models.BooleanField(default=True)

	def __str__(self):
		return  self.name

	@property
	def used_bedd_amount(self):
		beds = self.sp_ward.filter(patient__isnull=False)
		return beds.count()

	@property
	def filtered_mixed_ward(self):
		wards = Ward.objects.filter(by_gender='MIXED')
		categories = []
		for ward in wards:
			if ward.category in categories:
				print('nothing')
			else:
				categories.append(ward.category)
		"""
		wards = self.sp_category.all()
		bed_count = 0
		for ward in wards:
			beds = Bed.objects.filter(ward=ward,patient__isnull=False)
			bed_count = bed_count + beds.count()				
		"""
		return categories

class Bed(models.Model):

	name = models.CharField( null=True, max_length=50)
	ward = models.ForeignKey(Ward,  on_delete= models.SET_NULL, null=True,blank=True,related_name='sp_ward')
	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True, blank=True)
	category = models.ForeignKey(BedCategory, on_delete= models.SET_NULL, null=True, blank=True)
	registered_on = models.DateField(null=True, blank=True)
	registered_by = models.ForeignKey(to=Employee, on_delete=models.SET_NULL, null=True, blank=True)
	active = models.BooleanField(default=True)

	def __str__(self):
		return  str(self.name) 

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

	@property
	def return_outpatients(self):
		beds = Bed.objects.filter(patient__isnull=False)
		patient_id = []
		for bed in beds:
			patient_id.append(bed.patient.id)

		return Patient.objects.filter().exclude(id__in=patient_id)

	@property
	def used_bed_amount(self):
		beds = Bed.objects.filter(patient__isnull=False)
		return beds.count()

	@property
	def free_bed_amount(self):
		beds = Bed.objects.filter(patient__isnull=True)
		return beds.count()

	def is_inpatient(self,patient_id):
		patient = Patient.objects.get(id=patient_id)
		allocated_patients_id = Bed.objects.filter().first().return_ward_patients
		if patient.id in allocated_patients_id:		
			return True
		else:
			return ""

	def is_admitted(self,day,bed_id):
		bed = Bed.objects.get(id=bed_id)
		#print('day:', day)
		prediction = bed.prediction_bed.filter(start_date__lte=day, end_date__gte=day).exists()
		
		if prediction:
			return True
		else:
			return ""
		"""
		try:
			prediction = PatientStayDurationPrediction.objects.get(bed=bed,star)
		except Exception as e:
			raise e
		return beds.count()
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
		return  str(self.bed.ward) + " Bed " + str(self.bed.name) + " - " + str(self.bed.category) + "   Release Date:  " + str(self.bed_release_date)

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
	bed = models.ForeignKey(Bed, on_delete=models.CASCADE,blank=True,null=True,related_name='prediction_bed')	
	patient = models.ForeignKey(Patient, on_delete=models.CASCADE)	
	start_date = models.DateTimeField(null=True, blank=True)
	end_date = models.DateTimeField(null=True, blank=True)
	active = models.BooleanField(default=True)

	status = models.CharField(max_length=100,choices=prediction_status, null=True, blank=True)
	def __str__(self):
		return str(self.patient) 


class RoomPrice(models.Model):
	room = models.ForeignKey(Bed, on_delete=models.CASCADE)	
	room_price = models.IntegerField(blank=True, null=True)
	discounted_price = models.IntegerField(blank=True, null=True)
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
		('completed', 'completed'),       
		('dismissed', 'dismissed'),       
		)

	service_provider = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True)
	patient = models.ForeignKey(to=Patient, on_delete=models.SET_NULL, null=True, blank=True)	
	care_plan =  models.CharField(max_length=1000, null=True, blank=True) 
	status = models.CharField(max_length=100,choices=inpatient_care_plan_status, null=True, blank=True)
	registered_on = models.DateField(null=True, blank=True)
	
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
		('Direct', 'Direct'),       
		('Other', 'Other'),       
		)

	service_provider = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True)
	patient = models.ForeignKey(to=Patient, on_delete=models.SET_NULL, null=True, blank=True)	
	general_appearance =  models.CharField(max_length=1000, null=True, blank=True) 
	other_assessment =  models.CharField(max_length=1000, null=True, blank=True) 
	admitted_from = models.CharField(max_length=100,choices=admitted_from_choices, null=True, blank=True)
	status = models.BooleanField(default=True)
	
#	def __str__(self):
#		return  str(self)



class WardStayDuration(models.Model):
	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True, blank=True)
	bed = models.ForeignKey(Bed, on_delete=models.CASCADE,null=True)	
	admission_date = models.DateTimeField(blank=True, null=True)
	leave_date = models.DateTimeField(blank=True, null=True)
	bed_transfer = models.BooleanField(default=False)

	def __str__(self):
		return str(self.patient)


class BedTransfer(models.Model):
	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True, blank=True)
	from_bed = models.ForeignKey(Bed, on_delete=models.CASCADE,null=True,related_name='from_bed')
	to_bed = models.ForeignKey(Bed, on_delete=models.CASCADE,null=True,related_name='to_bed')
	stay_duration = models.ForeignKey(WardStayDuration, on_delete=models.CASCADE,null=True)
	registered_by = models.ForeignKey(Employee, on_delete= models.SET_NULL, null=True)
	registered_on = models.DateTimeField(null=True)

	def __str__(self):
		return str(self.patient)

class WardDischargeSummary(models.Model):
	discharge_conditions = (
		('Completed Treatment', 'Completed Treatment'),
		('Treatment Not Completed', 'Treatment Not Completed'),     
		('Died', 'Died'),       
		)
	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True, blank=True)
	discharge_condition = models.CharField(max_length=100,choices=discharge_conditions, null=True)
	significant_findings = models.CharField(max_length=2000, null=True)
	summary = models.CharField(max_length=2000, null=True) 
	registered_on = models.DateField(null=True, blank=True)
	discharged_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	active = models.BooleanField(default=False)
	def __str__(self):
		return str(self.patient)

	def has_summary(self,patient_id):
		patient = Patient.objects.get(id=patient_id)
		try:
			summary = WardDischargeSummary.objects.filter(patient=patient,active=True)
			if summary:
				return True
		except:
			return False



class InpatientObservation(models.Model):
	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True, blank=True)
	observation = models.CharField(max_length=5000, blank=True)
	stay_duration = models.ForeignKey(WardStayDuration, on_delete=models.CASCADE)	
	registered_on = models.DateTimeField(null=True)



class NurseProgressChart(models.Model):
	view_status=(
		('seen','seen'),
		('not_seen','not_seen'),
		)

	nurse = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	ward_team_bed = models.ForeignKey(WardTeamBed, on_delete= models.SET_NULL, null=True, blank=True)

	appearance = models.CharField(max_length=5000, blank=True)
	view_status = models.CharField(choices=view_status, max_length = 50, blank=True)
	
	observation = models.CharField(max_length=5000, blank=True)
	stay_duration = models.ForeignKey(WardStayDuration, on_delete=models.CASCADE)
	registered_on = models.DateTimeField(null=True)

class InpatientDoctorOrder(models.Model):
	result_status=(
		('recieved','recieved'),
		('not_recieved','not_recieved'),
		)

	view_status=(
		('seen','seen'),
		('not_seen','not_seen'),
		)
	
	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True, blank=True)
	doctor = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	ward_team_bed = models.ForeignKey(WardTeamBed, on_delete= models.SET_NULL, null=True, blank=True)
	lab_order = models.ForeignKey(LaboratoryTest, on_delete=models.CASCADE)
	instruction = models.CharField(max_length=5000, blank=True, null=True)
	nurse_check_time = models.DateTimeField(null=True)
	nurse_chart = models.ForeignKey(NurseProgressChart,  on_delete= models.SET_NULL, null=True, blank=True)
	stay_duration = models.ForeignKey(WardStayDuration, on_delete=models.CASCADE)	
	result_status = models.CharField(choices=result_status, max_length = 50, blank=True)
	view_status = models.CharField(choices=view_status, max_length = 50, blank=True)
	registered_on = models.DateTimeField(null=True)


class InpatientDoctorInstruction(models.Model):


	view_status=(
		('seen','seen'),
		('not_seen','not_seen'),
		)
	instruction_status=(
		('Done','Done'),
		('not_done','not_done'),
		)
	nurse_instruction_check = (
		('checked','checked'),
		('not_checked','not_checked'),
		)

	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True, blank=True)
	doctor = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	ward_team_bed = models.ForeignKey(WardTeamBed, on_delete= models.SET_NULL, null=True, blank=True)
	instruction = models.CharField(max_length=5000, blank=True, null=True)
	expected_outcome = models.CharField(max_length=5000, blank=True, null=True)
	instruction_time = models.DateTimeField(null=True,blank=True)
	stay_duration = models.ForeignKey(WardStayDuration, on_delete=models.CASCADE)
	view_status = models.CharField(choices=view_status, max_length = 50, blank=True)
	nurse_check_status = models.CharField(choices=nurse_instruction_check, max_length = 50, blank=True)

	instruction_status = models.CharField(choices=instruction_status, max_length = 50, blank=True)
	registered_on = models.DateTimeField(null=True)


class NurseInstructionCheck(models.Model):
	
	evaluation_status=(
		('evaluated','evaluated'),
		('not_evaluated','not_evaluated'),
		)
	
	doctor_instruction = models.ForeignKey(InpatientDoctorInstruction, on_delete=models.CASCADE, null=True,blank=True)
	nurse = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)

	intervention = models.CharField( max_length = 5000, blank=True)
	evaluation_status = models.CharField(choices=evaluation_status, max_length = 50, blank=True)
	registered_on = models.DateTimeField(null=True)

class NurseIndependentIntervention(models.Model):
	
	evaluation_status=(
		('evaluated','evaluated'),
		('not_evaluated','not_evaluated'),
		)

	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True, blank=True)	
	intervention_cause = models.CharField( max_length = 1000, blank=True, null=True)
	nurse = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)

	intervention = models.CharField( max_length = 1000, blank=True, null=True)
	rational = models.CharField( max_length = 1000, blank=True, null=True)

	evaluation_status = models.CharField(choices=evaluation_status, max_length = 50, blank=True)
	registered_on = models.DateTimeField(null=True)

class NurseEvaluation(models.Model):
	nurse = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)

	intervention = models.ForeignKey(NurseInstructionCheck, on_delete=models.CASCADE, null=True,blank=True)
	independent_intervention = models.ForeignKey(NurseIndependentIntervention, on_delete=models.CASCADE, null=True,blank=True)
	
	evaluation = models.CharField( max_length = 1000, blank=True)
	registered_on = models.DateTimeField(null=True)


class InpatientMedication(models.Model):
	medication_status = (
		('Ended', 'Ended'),
		('Cancelled', 'Cancelled'),     
		('Active', 'Active'),       
		)
	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True, blank=True)
	stay_duration = models.ForeignKey(WardStayDuration, on_delete=models.CASCADE)	
	drug_prescription = models.ForeignKey(to=DrugPrescription, on_delete=models.SET_NULL, null=True, blank=True)
	drug_status = models.CharField(max_length=100,choices=medication_status, null=True)
	doctor = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	registered_on = models.DateField(null=True, blank=True)

class InpatientLabOrder(models.Model):
	medication_status = (
		('Ended', 'Ended'),
		('Cancelled', 'Cancelled'),     
		('Active', 'Active'),       
		)
	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True, blank=True)
	stay_duration = models.ForeignKey(WardStayDuration, on_delete=models.CASCADE)	
	lab_result = models.ForeignKey(to=LaboratoryTestResult, on_delete=models.SET_NULL, null=True, blank=True)
	doctor = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	registered_on = models.DateField(null=True, blank=True)


class InpatientDischargeSummary(models.Model):
	discharge_conditions = (
		('Completed Treatment', 'Completed Treatment'),
		('Treatment Not Completed', 'Treatment Not Completed'),     
		('Died', 'Died'),       
		)
	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True, blank=True)
	discharge_condition = models.CharField(max_length=100,choices=discharge_conditions, null=True)
	significant_findings = models.CharField(max_length=2000, null=True)
	summary = models.CharField(max_length=2000, null=True) 
	registered_on = models.DateField(null=True, blank=True)
	stay_duration = models.ForeignKey(WardStayDuration, on_delete=models.CASCADE)	
	discharged_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)


class InpatientAdministrationTime(models.Model):

	drug_prescription = models.ForeignKey(to=DrugPrescription, on_delete=models.SET_NULL, null=True, blank=True)
	time_gap = models.IntegerField(blank=True, null=True)
	first_time = models.TimeField(null=True, blank=True)

	registered_on = models.DateTimeField(null=True, blank=True)

class InpatientLabResult(models.Model):
	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True, blank=True)
	stay_duration = models.ForeignKey(WardStayDuration, on_delete=models.CASCADE, null=True, blank=True)	
	ordered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	result = models.ForeignKey(LaboratoryTestResult, on_delete= models.SET_NULL, null=True, blank=True)
	registered_on = models.DateTimeField(null=True)



class InpatientMedicalAdministration(models.Model):
	"""
	prescription:
	administered_by: user(usually nurse) that administers the drug
	administration_time: the time that patient takes the drug
	"""
	drug_prescription = models.ForeignKey(DrugPrescription, on_delete=models.CASCADE, null=True, blank=True)
	administered_by = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)
	administration_on = models.DateTimeField(auto_now_add=True, null=True)


class VitalSignPlan(models.Model):

	temperature = models.BooleanField(default=False)
	blood_pressure = models.BooleanField(default=False)
	oxygen_saturation = models.BooleanField(default=False)
	glucose = models.BooleanField(default=False)
	pulse_rate = models.BooleanField(default=False)

	active = models.BooleanField(default=False)
	registered_on = models.DateTimeField(null=True)

class TolerableTimeDifference(models.Model):
	time_units=(
		('Minutes','Minutes'),
		('Hours','Hours'),
		('Days','Days'),
		('Weeks','Weeks'),
		)

	tolerable_earliness_unit = models.CharField(choices=time_units, max_length = 50, blank=True, null=True)
	tolerable_earliness = models.IntegerField(blank=True, null=True)
	tolerable_lateness_unit = models.CharField(choices=time_units, max_length = 50, blank=True, null=True)
	tolerable_lateness = models.IntegerField(blank=True, null=True)

class IPDTreatmentPlan(models.Model):
	view_status=(
		('Completed','Completed'),
		('Dismissed','Dismissed'),
		)

	patient = models.ForeignKey(to=Patient, on_delete=models.SET_NULL, null=True, blank=True)
	name = models.CharField(max_length=5000, blank=True)
	status = models.CharField(choices=view_status, max_length = 50, blank=True, null=True)
	start_time = models.DateTimeField(null=True,blank=True)
	end_time = models.DateTimeField(null=True,blank=True)	
	description = models.CharField(max_length=5000, blank=True)
	stay_duration = models.ForeignKey(WardStayDuration, on_delete=models.CASCADE,null=True,blank=True)
	prescription = models.ForeignKey(DrugPrescription, on_delete=models.CASCADE, null=True, blank=True)
	treatment = models.ForeignKey('core.PatientTreatment', on_delete=models.CASCADE, null=True, blank=True)
	appointment = models.ForeignKey(PatientAppointment, on_delete=models.CASCADE, null=True, blank=True)
	vital_sign = models.ManyToManyField(PatientVitalSign)
	recurrence = models.ForeignKey(Recurrence, on_delete=models.CASCADE, null=True, blank=True)
	vital_sign_options = models.ForeignKey(VitalSignPlan, on_delete=models.CASCADE, null=True, blank=True)
	tolerable_difference = models.ForeignKey(TolerableTimeDifference, on_delete=models.CASCADE, null=True, blank=True)

	active = models.BooleanField(default=False)
	registered_on = models.DateTimeField(null=True)
	def __str__(self):
		return str(self.patient)


class PerformPlan(models.Model):
	plan = models.ForeignKey(IPDTreatmentPlan, on_delete=models.CASCADE, null=True, blank=True,related_name='performed_plan')
	note = models.CharField(max_length=2000, blank=True)
	registered_by = models.ForeignKey(to=Employee, on_delete=models.SET_NULL, null=True, blank=True)
	registered_on = models.DateTimeField(null=True)
	def __str__(self):
		return str(self.plan.patient)

	def is_performed(self,day,plan_id):
		plan = IPDTreatmentPlan.objects.get(id=plan_id)
		print('\n','dayplan: ',plan.registered_on.date,'sentdate: ',day.date)
		after_date = day + timedelta(hours=12)
		before_date = day - timedelta(hours=12)

		if plan.recurrence.hourly:
			after_date = day + timedelta(minutes=30)
			before_date = day - timedelta(minutes=30)
		elif plan.recurrence.daily:
			after_date = day + timedelta(hours=12)
			before_date = day - timedelta(hours=12)
		if plan.tolerable_difference:
			if plan.tolerable_difference.tolerable_lateness_unit=='Hours':
				after_date = day + timedelta(hours=plan.tolerable_difference.tolerable_lateness)
			elif plan.tolerable_difference.tolerable_lateness_unit=='Days':
				after_date = day + timedelta(days=plan.tolerable_difference.tolerable_lateness)
			elif plan.tolerable_difference.tolerable_lateness_unit=='Minutes':
				after_date = day + timedelta(minutes=plan.tolerable_difference.tolerable_lateness)
			if plan.tolerable_difference.tolerable_earliness_unit=='Hours':
				before_date = day + timedelta(hours=plan.tolerable_difference.tolerable_earliness)
			elif plan.tolerable_difference.tolerable_earliness_unit=='Days':
				before_date = day + timedelta(days=plan.tolerable_difference.tolerable_earliness)
			elif plan.tolerable_difference.tolerable_earliness_unit=='Minutes':
				before_date = day + timedelta(minutes=plan.tolerable_difference.tolerable_earliness)


		performed = plan.performed_plan.filter(registered_on__range=[before_date,after_date]).exists()
		print('inperformed: ',performed,'\n')

		#scheduled_resources = resource.scheduled_resource.filter(start_time__lte=day, end_time__gte=day).exists()
		if day > datetime.now(UTC):
			performed = 'not_yet'  

		if performed ==True:
			return True
		elif performed == False:
			return False
