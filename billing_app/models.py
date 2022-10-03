from django.db import models
from django.contrib.auth.models import User
#from core.models import * 
from outpatient_app.models import *
from lis.models import *
from inpatient_app.models import Bed, WardTeamBed,RoomPrice
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
	active = models.BooleanField(default=False)
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
	departments = {('Outpatient','Outpatient'),
				('Inpatient','Inpatient'),
				('Emergency','Emergency'),
	}

	bill = models.ForeignKey(VisitBill, on_delete=models.CASCADE)	
	visiting_card = models.ForeignKey(VisitingCardPrice, on_delete=models.CASCADE)	
	selling_price = models.IntegerField(blank=True, null=True)
	discount = models.BooleanField(default=False)
	insurance = models.BooleanField(default=False)
	free = models.BooleanField(default=False)
	credit = models.BooleanField(default=False)
	department = models.CharField(max_length=500, choices=departments, null=True)

	patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)
	registered_on=models.DateTimeField(auto_now_add=True)
	registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)

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
	departments = {('Outpatient','Outpatient'),
				('Inpatient','Inpatient'),
				('Emergency','Emergency'),
	}
	insurance = {
	('Yes','Yes'),
	('No','No'),
	}

	#bill = models.ForeignKey(ServiceBill, on_delete=models.CASCADE)	
	service = models.ForeignKey(Service, on_delete=models.CASCADE)	
	service_price = models.IntegerField(blank=True, null=True)

	visit = models.ForeignKey(PatientVisit, on_delete=models.CASCADE, blank=True,null=True)	
	discount = models.BooleanField(default=False)
	insurance = models.BooleanField(default=False)
	free = models.BooleanField(default=False)
	credit = models.BooleanField(default=False)

	patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)
	registered_on=models.DateTimeField(auto_now_add=True)
	registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	def __str__(self):
		return str(self.patient) + str(self.service)





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
	stay_duration = models.ForeignKey(PatientStayDuration, on_delete=models.CASCADE)	
	discharged_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)


class InpatientAdministrationTime(models.Model):

	drug_prescription = models.ForeignKey(to=DrugPrescription, on_delete=models.SET_NULL, null=True, blank=True)
	time_gap = models.IntegerField(blank=True, null=True)
	first_time = models.TimeField(null=True, blank=True)

	registered_on = models.DateTimeField(null=True, blank=True)

class InpatientLabResult(models.Model):
	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True, blank=True)
	stay_duration = models.ForeignKey(PatientStayDuration, on_delete=models.CASCADE, null=True, blank=True)	
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
	departments = {('Outpatient','Outpatient'),
				('Inpatient','Inpatient'),
				('Emergency','Emergency'),
	}

	#bill = models.ForeignKey(LabBill, on_delete=models.CASCADE)	
	test = models.ForeignKey(LaboratoryTestType, on_delete=models.CASCADE)
	test_price = models.ForeignKey(LaboratoryTestPrice, on_delete=models.CASCADE, null=True)
	discount = models.BooleanField(default=False)
	insurance = models.BooleanField(default=False)
	free = models.BooleanField(default=False)
	credit = models.BooleanField(default=False)
	department = models.CharField(max_length=500, choices=departments, null=True)
	patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)
	registered_on=models.DateTimeField(auto_now_add=True)
	registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	def __str__(self):
		return str(self.test)





class RoomBillDetail(models.Model):

	room = models.ForeignKey(Bed, on_delete=models.CASCADE, blank=True, null=True)
	room_price = models.ForeignKey(RoomPrice, on_delete=models.CASCADE, blank=True, null=True)

	discount = models.BooleanField(default=False)
	insurance = models.BooleanField(default=False)
	free = models.BooleanField(default=False)
	credit = models.BooleanField(default=False)

	patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)
	registered_on=models.DateTimeField(auto_now_add=True)
	registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	active = models.BooleanField(default=True)


class CashierDebt(models.Model):

	cashier = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	cash_debt = models.IntegerField(blank=True, null=True, default=0)
	debt_date =models.DateField(auto_now_add=True)
	reconciled = models.BooleanField(default=False)

class CashierReconcilation(models.Model):
	finance_employee = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	debt = models.ForeignKey(CashierDebt, on_delete=models.CASCADE, blank=True, null=True)
	remaining_amount = models.IntegerField(blank=True, null=True)
	registered_on=models.DateTimeField(auto_now_add=True)
