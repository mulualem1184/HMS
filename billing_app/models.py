from django.db import models
from django.contrib.auth.models import User
#from core.models import * 
from outpatient_app.models import *
from lis.models import *
from inpatient_app.models import Bed, WardTeamBed,RoomPrice,WardStayDuration
from staff_mgmt.models import Employee
from core.models import PatientInsurance,PatientTreatment
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





class PatientStayDuration(models.Model):
	bill = models.ForeignKey(InpatientBill, on_delete=models.CASCADE,null=True,blank=True)
	patient = models.ForeignKey(Patient,  on_delete= models.SET_NULL, null=True, blank=True)
	room = models.ForeignKey(Bed, on_delete=models.CASCADE,null=True)	
	admission_date = models.DateTimeField(blank=True, null=True)
	leave_date = models.DateTimeField(blank=True, null=True)
	def __str__(self):
		return str(self.patient)



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
	stay_duration = models.ForeignKey(WardStayDuration, on_delete=models.CASCADE, null=True, blank=True)
	patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)
	registered_on=models.DateTimeField(auto_now_add=True)
	registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	def __str__(self):
		return str(self.test)





class RoomBillDetail(models.Model):

	room = models.ForeignKey(Bed, on_delete=models.CASCADE, blank=True, null=True)
	room_price = models.ForeignKey(RoomPrice, on_delete=models.CASCADE, blank=True, null=True)
	stay_duration = models.ForeignKey(WardStayDuration, on_delete=models.CASCADE, null=True, blank=True)
	discount = models.BooleanField(default=False)
	insurance = models.BooleanField(default=False)
	free = models.BooleanField(default=False)
	credit = models.BooleanField(default=False)

	patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)
	registered_on=models.DateTimeField(auto_now_add=True)
	registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	active = models.BooleanField(default=True)


class DrugBill(models.Model):
	departments = {('Outpatient','Outpatient'),
				('Inpatient','Inpatient'),
				('Emergency','Emergency'),
	}
	bill = models.ForeignKey(Bill, on_delete=models.CASCADE,null=True, blank=True)	
	drug = models.ForeignKey(Dosage, on_delete=models.CASCADE)
	stay_duration = models.ForeignKey(WardStayDuration, on_delete=models.CASCADE, null=True, blank=True)	
	product = models.ForeignKey(OtherProducts, on_delete= models.SET_NULL, null=True, blank=True)
	selling_price = models.ForeignKey(DrugPrice, on_delete=models.SET_NULL, null=True)
	quantity=models.IntegerField(null=True)
	discount = models.BooleanField(default=False)
	insurance = models.BooleanField(default=False)
	free = models.BooleanField(default=False)
	credit = models.BooleanField(default=False)
	department = models.CharField(max_length=500, choices=departments, null=True)

	patient =models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)
	registered_on=models.DateTimeField(auto_now_add=True)
	def __str__(self):
		bill_string = str(self.bill)
		return bill_string

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

class Treatment(models.Model):

	name = models.CharField(max_length=5000, blank=True)	
	description = models.CharField(max_length=5000, blank=True)
	active = models.BooleanField(default=False)
	registered_on = models.DateTimeField(null=True)
	def __str__(self):
		return str(self.name)


