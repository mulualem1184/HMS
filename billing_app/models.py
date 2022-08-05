from django.db import models
from django.contrib.auth.models import User
#from core.models import * 
from outpatient_app.models import *
from lis.models import *
from inpatient_app.models import Bed, WardTeamBed
from staff_mgmt.models import Employee
from core.models import PatientInsurance
#from pharmacy_app.models import DrugPrescription

class PatientInsuranceDetail(models.Model):
	insurance = models.ForeignKey(to=PatientInsurance, on_delete=models.SET_NULL, null=True, blank=True)
	patient = models.ForeignKey(to=Patient, on_delete=models.SET_NULL, null=True, blank=True)
	sum_insured = models.IntegerField(null=True, blank=True)

class InsuranceExcludedService(models.Model):
	insurance = models.ForeignKey(to=PatientInsurance, on_delete=models.SET_NULL, null=True, blank=True)
	excluded_service =  models.ForeignKey(to=Service, on_delete=models.SET_NULL, null=True, blank=True)

class VisitingCardPrice(models.Model):
	service = models.ForeignKey(Service,  on_delete= models.SET_NULL, null=True)
	visiting_price = models.IntegerField(null=True, blank=True)
	discounted_price = models.IntegerField(null=True, blank=True)
	def __str__(self):
		return str(self.visiting_price) + " birr for " + str(self.service.service_name)

class VisitBill(models.Model):
	"""
	bill_no : 
	drug :
	selling_price:
	quantity : the amount of drugs sold to a single patient
	patient : 
	"""
	bill_no = models.AutoField( primary_key=True)
	registered_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	def __str__(self):
 
		return str(self.bill_no)


class VisitBillDetail(models.Model):
	discount = {
	('Yes','Yes'),
	('No','No'),
	}
	insurance = {
	('Yes','Yes'),
	('No','No'),
	}

	bill = models.ForeignKey(VisitBill, on_delete=models.CASCADE)	
	visiting_card = models.ForeignKey(VisitingCardPrice, on_delete=models.CASCADE)	
	selling_price = models.IntegerField(blank=True, null=True)
	discount = models.CharField(null=True,blank=True, max_length=100, choices=discount)
	insurance = models.CharField(null=True,blank=True, max_length=100, choices=insurance)
	patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)
	registered_on=models.DateTimeField(auto_now_add=True)
	def __str__(self):
		bill_string = str(self.bill)
		return bill_string


class ServiceBill(models.Model):
	"""
	bill_no : 
	drug :
	selling_price:
	quantity : the amount of drugs sold to a single patient
	patient : 
	"""
	bill_no = models.AutoField( primary_key=True)
	registered_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	def __str__(self):
		bill_string = str(self.bill_no)
		return bill_string




class ServiceBillDetail(models.Model):
	discount = {
	('Yes','Yes'),
	('No','No'),
	}
	insurance = {
	('Yes','Yes'),
	('No','No'),
	}

	bill = models.ForeignKey(ServiceBill, on_delete=models.CASCADE)	
	service = models.ForeignKey(Service, on_delete=models.CASCADE)	
	visit = models.ForeignKey(PatientVisit, on_delete=models.CASCADE, blank=True,null=True)	

	service_price = models.IntegerField(blank=True, null=True)
	discount = models.CharField(null=True,blank=True, max_length=100, choices=discount)
	insurance = models.CharField(null=True,blank=True, max_length=100, choices=insurance)
	patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)
	registered_on=models.DateTimeField(auto_now_add=True)
	def __str__(self):
		bill_string = str(self.bill)
		return bill_string



class InpatientBill(models.Model):
	bill_no = models.AutoField( primary_key=True)
	registered_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	def __str__(self):
		bill_string = str(self.bill_no)
		return bill_string

class InpatientBillRelation(models.Model):
	active = {
	('active','active'),
	('not_active','not_active'),
	}

	bill = models.ForeignKey(InpatientBill, on_delete=models.CASCADE)	
	patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)
	is_active = models.CharField(null=True,blank=True, max_length=100, choices=active)



class InpatientRoomBillDetail(models.Model):
	discount = {
	('Yes','Yes'),
	('No','No'),
	}
	insurance = {
	('Yes','Yes'),
	('No','No'),
	}
	active = {
	('active','active'),
	('not_active','not_active'),
	}

	bill = models.ForeignKey(InpatientBill, on_delete=models.CASCADE)	
	room = models.ForeignKey(Bed, on_delete=models.CASCADE, blank=True, null=True)
	room_price = models.IntegerField(blank=True, null=True)
	discount = models.CharField(null=True,blank=True, max_length=100, choices=discount)
	insurance = models.CharField(null=True,blank=True, max_length=100, choices=insurance)
	patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)
	registered_on=models.DateTimeField(auto_now_add=True)
	active = models.CharField(null=True,blank=True, max_length=100, choices=active)

	def __str__(self):
		bill_string = str(self.bill)
		return bill_string



class InpatientDrugBillDetail(models.Model):
	discount = {
	('Yes','Yes'),
	('No','No'),
	}
	insurance = {
	('Yes','Yes'),
	('No','No'),
	}

	bill = models.ForeignKey(InpatientBill, on_delete=models.CASCADE)	
	drug_prescription = models.ForeignKey(DrugPrescription, on_delete=models.CASCADE, null=True, blank=True)
	drug = models.ForeignKey(Dosage, on_delete=models.CASCADE, blank=True)
	drug_price = models.IntegerField(blank=True, null=True)
	quantity=models.IntegerField(null=True)

	discount = models.CharField(null=True,blank=True, max_length=100, choices=discount)
	insurance = models.CharField(null=True,blank=True, max_length=100, choices=insurance)
	patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)
	registered_on=models.DateTimeField(auto_now_add=True)
	def __str__(self):
		bill_string = str(self.bill)
		return bill_string



class InpatientServiceBillDetail(models.Model):
	discount = {
	('Yes','Yes'),
	('No','No'),
	}
	insurance = {
	('Yes','Yes'),
	('No','No'),
	}

	bill = models.ForeignKey(InpatientBill, on_delete=models.CASCADE)	
	service = models.ForeignKey(Service, on_delete=models.CASCADE, blank=True)	
	service_price = models.IntegerField(blank=True, null=True)
	discount = models.CharField(null=True,blank=True, max_length=100, choices=discount)
	insurance = models.CharField(null=True,blank=True, max_length=100, choices=insurance)
	patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)
	registered_on=models.DateTimeField(auto_now_add=True)
	def __str__(self):
		bill_string = str(self.bill)
		return bill_string


class PatientStayDuration(models.Model):
	bill = models.ForeignKey(InpatientBill, on_delete=models.CASCADE)
	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True, blank=True)
	room = models.ForeignKey(Bed, on_delete=models.CASCADE,null=True)	
	admission_date = models.DateTimeField(blank=True, null=True)
	leave_date = models.DateTimeField(blank=True, null=True)

class InpatientObservation(models.Model):
	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True, blank=True)
	observation = models.CharField(max_length=5000, blank=True)
	stay_duration = models.ForeignKey(PatientStayDuration, on_delete=models.CASCADE)	
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
	stay_duration = models.ForeignKey(PatientStayDuration, on_delete=models.CASCADE)
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
	stay_duration = models.ForeignKey(PatientStayDuration, on_delete=models.CASCADE)	
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
	stay_duration = models.ForeignKey(PatientStayDuration, on_delete=models.CASCADE)
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
	stay_duration = models.ForeignKey(PatientStayDuration, on_delete=models.CASCADE)	
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
	stay_duration = models.ForeignKey(PatientStayDuration, on_delete=models.CASCADE)	
	laboratory_order = models.ForeignKey(to=Order, on_delete=models.SET_NULL, null=True, blank=True)
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
	stay_duration = models.ForeignKey(PatientStayDuration, on_delete=models.CASCADE)	
	discharged_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)


class InpatientAdministrationTime(models.Model):

	drug_prescription = models.ForeignKey(to=DrugPrescription, on_delete=models.SET_NULL, null=True, blank=True)
	time_gap = models.IntegerField(blank=True, null=True)
	first_time = models.TimeField(null=True, blank=True)

	registered_on = models.DateTimeField(null=True, blank=True)

class InpatientLabResult(models.Model):
	
	order = models.ForeignKey(InpatientDoctorOrder,  on_delete= models.SET_NULL, null=True, blank=True)
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


#this model holds old and new prices of laboratory tests to be ordered.
class LabTestPrice(models.Model):
	"""
	drug : 
	selling_price : 
	effective_date : date since when the drug is sold with this price 
	"""
	TestPriceActive=(
		('active','active'),
		('not_active','not_active'),
		)

	
	test = models.ForeignKey(LaboratoryTest, on_delete=models.CASCADE)
#	product = models.ForeignKey(OtherProducts, on_delete= models.SET_NULL, null=True, blank=True)
	test_price = models.FloatField(null=True)
	test_discounted_price = models.FloatField(null=True, blank=True)
	effective_date = models.DateTimeField( null=True, blank=True)
	active = models.CharField(choices=TestPriceActive, max_length = 50, blank=True)


class LabBill(models.Model):
	bill_no = models.AutoField( primary_key=True)
	registered_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	def __str__(self):
		bill_string = str(self.bill_no)
		return bill_string


class LabBillDetail(models.Model):
	discount = {
	('Yes','Yes'),
	('No','No'),
	}
	insurance = {
	('Yes','Yes'),
	('No','No'),
	}

	bill = models.ForeignKey(LabBill, on_delete=models.CASCADE)	
	test = models.ForeignKey(LaboratoryTest, on_delete=models.CASCADE)
	test_price = models.IntegerField(blank=True, null=True)
	discount = models.CharField(null=True,blank=True, max_length=100, choices=discount)
	insurance = models.CharField(null=True,blank=True, max_length=100, choices=insurance)
	patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)
	registered_on=models.DateTimeField(auto_now_add=True)
	def __str__(self):
		bill_string = str(self.bill)
		return bill_string






# Create your models here.
"""

class Bill(models.Model):
	bill_no = models.AutoField( primary_key=True)
	registered_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	def __str__(self):
		bill_string = str(self.bill_no)
		return bill_string


class BillDetail(models.Model):
	discount = {
	('Yes','Yes'),
	('No','No'),
	}
	bill = models.ForeignKey(Bill, on_delete=models.CASCADE)	
	drug = models.ForeignKey(Dosage, on_delete=models.CASCADE)
	product = models.ForeignKey(OtherProducts, on_delete= models.SET_NULL, null=True, blank=True)
	selling_price = models.ForeignKey(DrugPrice, on_delete=models.SET_NULL, null=True)
	discount = models.CharField(null=True,blank=True, max_length=100, choices=discount)
	quantity=models.IntegerField(null=True)
	patient =models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)
	registered_on=models.DateTimeField(auto_now_add=True)
	def __str__(self):
		bill_string = str(self.bill)
		return bill_string




class LabBill(models.Model):
	
	bill_no = models.AutoField( primary_key=True)
	registered_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	def __str__(self):
		bill_string = str(self.bill_no)
		return bill_string

class LabBillDetail(models.Model):
	bill_no : 
	drug :
	selling_price:
	quantity : the amount of drugs sold to a single patient
	patient : the patient for whom the lab test was ordered
	discount = {
				('Yes','Yes'),
				('No','No'),
	}
	bill = models.ForeignKey(Bill, on_delete=models.CASCADE)	
	test = models.ForeignKey(LabratoryTest, on_delete=models.CASCADE)
	test_price = models.ForeignKey(TestPrice, on_delete=models.SET_NULL, null=True)
	discount = models.CharField(null=True,blank=True, max_length=100, choices=discount)
	patient =models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)
	registered_on=models.DateTimeField(auto_now_add=True)
	registered_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

	def __str__(self):
		bill_string = str(self.bill)
		return bill_string

class InsurancePatient(models.Model)
"""