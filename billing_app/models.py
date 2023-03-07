from django.db import models
from django.contrib.auth.models import User
#from core.models import * 
from outpatient_app.models import *
from lis.models import *
from inpatient_app.models import Bed, WardTeamBed,RoomPrice,WardStayDuration
from staff_mgmt.models import Employee
from core.models import PatientInsurance,PatientTreatment
from django.db.models import Sum

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


class ItemCategory(models.Model):

	name = models.CharField(max_length=5000, blank=True)	
	active = models.BooleanField(default=False)
	registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	registered_on = models.DateTimeField(null=True)
	def __str__(self):
		return str(self.name)

class ItemPrice(models.Model):
	sale_price = models.IntegerField(blank=True, null=True)
	buy_price = models.IntegerField(blank=True, null=True)
	discount_price = models.IntegerField(blank=True, null=True)
	active = models.BooleanField(default=False)
	registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	registered_on=models.DateTimeField(auto_now_add=True)



class Item(models.Model):
	item_type_choices = {('1','Inventory'),
						('2','Service'),
	}

	medical_type_choices = {('1','Treatment'),
						('2','Drug'),
						('3','Surgery'),
						('4','Material'),
						('5','Inpatient Accommodation'),
						('6','Laboratory Test'),
						('7','Imaging Test'),
						('8','Laboratory Material'),

	}

	name = models.CharField(max_length=5000)	
	generic_name = models.CharField(max_length=5000)	
	category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE, blank=True, null=True)
	item_type = models.CharField(max_length=500, choices=item_type_choices, null=True)
	medical_type = models.CharField(max_length=500, choices=medical_type_choices, null=True)
	drug = models.ForeignKey(to=Dosage, on_delete=models.SET_NULL, null=True,blank=True)
	lab_test = models.ForeignKey(to=LaboratoryTestType, on_delete=models.SET_NULL, null=True,blank=True)
	price_info = models.ForeignKey(ItemPrice, on_delete=models.CASCADE, blank=True, null=True)
	measurement_unit = models.CharField(max_length=5000,null=True,blank=True)	
	code = models.CharField(max_length=5000, blank=True,null=True)
	active = models.BooleanField(default=False)
	available_in_appointment = models.BooleanField(default=False)
	registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	registered_on = models.DateTimeField(null=True)
	def __str__(self):
		return str(self.name)


	@property
	def return_unassociated_drugs(self):
		drug_items = Item.objects.filter(medical_type='2')
		drug_array = []
		for item in drug_items:
			if item.drug == None:
				print('')
			else:
				drug_array.append(item.drug.id) 
		drugs = Dosage.objects.exclude(id__in=drug_array)
		return drugs

	@property
	def return_unassociated_lab_tests(self):
		lab_test_items = Item.objects.filter(medical_type='6')
		lab_test_array = []
		for item in lab_test_items:
			if item.lab_test == None:
				print('')
			else:
				lab_test_array.append(item.lab_test.id) 
		lab_tests = LaboratoryTestType.objects.exclude(id__in=lab_test_array)
		return lab_tests

class ItemSaleInfo(models.Model):

	item = models.ForeignKey(to=Item, on_delete=models.SET_NULL, null=True)
	quantity = models.IntegerField(null=True, blank=True)
	discount = models.BooleanField(default=False)
	active = models.BooleanField(default=False)
	temp_active = models.BooleanField(default=True)

class BillableItem(models.Model):
	item = models.ForeignKey(to=Item, on_delete=models.SET_NULL, null=True)
	patient = models.ForeignKey(to=Patient, on_delete=models.SET_NULL, null=True)
	billed = models.BooleanField(default=False)
	active = models.BooleanField(default=False)
	registered_on = models.DateTimeField(null=True)

class Invoice(models.Model):
	item_type_choices = {('1','Inventory'),
						('2','Service'),
	}

	medical_type_choices = {('1','Treatment'),
						('2','Drug'),
						('3','Surgery'),
						('4','Material'),
						('5','Inpatient Accommodation'),
						('6','Laboratory Test'),
						('7','Imaging Test'),
						('8','Laboratory Material'),

	}

	patient = models.ForeignKey(to=Patient, on_delete=models.SET_NULL, null=True)
	item_info = models.ManyToManyField(ItemSaleInfo,null=True,blank=True)
	discount = models.BooleanField(default=False)
	active = models.BooleanField(default=False)
	paid = models.BooleanField(default=False)
	due_date = models.DateTimeField(null=True)
	registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	registered_on = models.DateTimeField(null=True)
	receipt = models.BooleanField(default=False)
	estimate = models.BooleanField(default=False)

	def __str__(self):
		return str(self.patient) + " - " + str(self.item_info)

	@property
	def no_of_items(self):
		count = self.item_info.all().count()
		return count

	@property
	def total_amount(self):
		amount = 0
		for info in self.item_info.all():
			amount += info.quantity * info.item.price_info.sale_price
		return amount
	"""
	@property
	def open_invoices(self):
		invoices = []
		for invoice in self.objects.all():
			invoice += info.quantity * info.item.price_info.sale_price
		return amount
	"""
	"""
	@property
	def unpaid_amount(self):
		amount = 0
		paid_amount = 0
		for info in self.item_info.all():
			amount += info.quantity * info.item.price_info.sale_price
		payments = self.paid_invoice.filter(active=True)
		paid_amount_dict = payments.aggregate(Sum('amount_paid'))
		paid_amount = paid_amount_dict['amount_paid__sum']
		#print('paid_amount: ',paid_amount,'\n')		
		if paid_amount == None:
			paid_amount = 0
		return  amount - paid_amount
	"""
	@property
	def unpaid_amount(self):
		amount = 0
		paid_amount = 0
		for info in self.item_info.all():
			amount += info.quantity * info.item.price_info.sale_price
		reconcilations = self.reconciled_invoice.filter(payment__isnull=False)
		reconciled_amount_dict = reconcilations.aggregate(Sum('amount_paid'))
		reconciled_amount = reconciled_amount_dict['amount_paid__sum']
		#print('reconciled_amount: ',reconciled_amount,'\n')		
		if reconciled_amount == None:
			reconciled_amount = 0
		return  amount - reconciled_amount

class Payment(models.Model):
	patient = models.ForeignKey(to=Patient, on_delete=models.SET_NULL, null=True)
	invoice = models.ManyToManyField(Invoice,null=True,blank=True,related_name='paid_invoice')
	amount_paid = models.IntegerField(null=True, blank=True)
	pre_payment = models.BooleanField(default=False)
	active = models.BooleanField(default=False)
	registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	registered_on = models.DateTimeField(null=True)

	@property
	def remaining_amount(self):
		amount = self.amount_paid
		reconcilations = self.reconciled_payment.all()
		reconciled_amount_dict = reconcilations.aggregate(Sum('amount_paid'))
		reconciled_amount = reconciled_amount_dict['amount_paid__sum']
		#print('reconciled_amount: ',reconciled_amount,'\n')		
		if reconciled_amount == None:
			reconciled_amount = 0
		return  amount - reconciled_amount

class InvoiceReconcilation(models.Model):
	invoice = models.ForeignKey(Invoice, on_delete= models.SET_NULL, null=True,related_name='reconciled_invoice')
	payment = models.ForeignKey(Payment, on_delete= models.SET_NULL, null=True,related_name='reconciled_payment')
	amount_paid = models.IntegerField(null=True)
	fully_paid = models.BooleanField(default=False)
	active = models.BooleanField(default=False)
	registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	registered_on = models.DateTimeField(null=True)

class ShelfItem(models.Model):
	shelf = models.ForeignKey(to=StockShelf, on_delete=models.SET_NULL, null=True)
	item = models.ForeignKey(to=Item, on_delete=models.SET_NULL, null=True)
	quantity = models.IntegerField(null=True)
	active = models.BooleanField(default=False)
	registered_on = models.DateTimeField(null=True)
	relocated_at = models.DateTimeField(null=True,blank=True)

	def item_stock_amount(self,item,stock):
		if stock == None:
			items = ShelfItem.objects.filter(active=True,item=item)
		else:
			items = ShelfItem.objects.filter(active=True,item=item,shelf__stock=stock)
		amount_dict = items.aggregate(Sum('quantity'))
		amount = amount_dict['quantity__sum']
		
		if amount:
			return amount
		else:
			return 0

	def item_one_stock_amount(self,item,quantity,stock):
		items = ShelfItem.objects.filter(active=True,item=item,shelf__stock=stock)
		amount_dict = items.aggregate(Sum('quantity'))
		amount = amount_dict['quantity__sum']
		if amount:
			pass
		else:
			return False
		if amount > quantity:
			return amount
		elif amount == quantity:
			return amount

		else:
			return False

class InventoryThreshold(models.Model):
	item = models.ForeignKey(Item,  on_delete= models.SET_NULL, null=True)
	threshold = models.IntegerField(null=True)
	registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	registered_on = models.DateTimeField(null=True)



class ItemTransferInfo(models.Model):
	item = models.ForeignKey(to=Item, on_delete=models.SET_NULL, null=True)
	quantity = models.IntegerField(null=True, blank=True)
	stock = models.ForeignKey(to=Stock, on_delete=models.SET_NULL, null=True)
	active = models.BooleanField(default=False)

class TransferRequest(models.Model):
	status = {('1','Pending'),
			('2','Approved Once'),
			('3','Approved Twice'),
			('4','Rejected'),
	}

	source = models.ForeignKey(to=Stock, on_delete=models.SET_NULL, null=True, related_name='source_stock')
	destination = models.ForeignKey(to=Stock, on_delete=models.SET_NULL, null=True, related_name='destination_stock')
	item_info = models.ManyToManyField(ItemTransferInfo,null=True,blank=True)
	active = models.BooleanField(default=False)
	status = models.CharField(max_length=500, choices=status, null=True)
	registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	registered_on = models.DateTimeField(null=True)

	def item_stock_amount(self,item,shelf):
		items = ShelfItem.objects.filter(active=True,item=item,)
		amount_dict = items.aggregate(Sum('quantity'))
		amount = amount_dict['quantity__sum']
		
		if amount:
			return amount
		else:
			return 0
	
	def is_item_available(self,item,quantity,shelf):
		shelf_items = ShelfItem.objects.filter(active=True,item=item,shelf=shelf)
		amount_dict = shelf_items.aggregate(Sum('quantity'))
		amount = amount_dict['quantity__sum']
		print('Shelf Amount:',amount)
		if amount + 1 > quantity:
			return True 
		else:
			return False

	@property	
	def return_items(self):
		infos = self.item_info.all()
		items = []
		for info in infos:
			if info.item in items:
				pass
			else:
				items.append(info.item.id)
		return items


class ItemRelocationInfo(models.Model):
	item = models.ForeignKey(to=Item, on_delete=models.SET_NULL, null=True)
	quantity = models.IntegerField(null=True, blank=True)
	shelf = models.ForeignKey(to=StockShelf, on_delete=models.SET_NULL, null=True)
	active = models.BooleanField(default=False)

class ItemRelocationTemp(models.Model):

	request = models.ForeignKey(to=TransferRequest, on_delete=models.SET_NULL, null=True)
	item_info = models.ManyToManyField(ItemRelocationInfo,null=True,blank=True)
	active = models.BooleanField(default=False)
	registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	registered_on = models.DateTimeField(null=True)

	def check_item(self,item,quantity):
		items = self.item_info.filter(active=True,item=item)
		if item in items:
			amount_dict = items.aggregate(Sum('quantity'))
			amount = amount_dict['quantity__sum']
			if quantity + 1 > amount:
				return True 
			else:
				return False
		else:
			return False

	def check_requested_item(self,request,item,quantity):
		item_infos = request.item_info.filter(item=item)
		items = request.return_items
		for item in items:
			print('Item: ', item)		
		if item in items:
			amount_dict = item_infos.aggregate(Sum('quantity'))
			amount = amount_dict['quantity__sum']
			print('Amount:',amount)
			print('Qmount:',quantity)

			if amount + 1 > quantity:
				return True 
			else:
				return False
		else:
			return False

	@property	
	def return_items(self):
		infos = self.item_info.filter(active=True)
		items = []
		for info in infos:
			if info.item in items:
				pass
			else:
				items.append(info.item.id)
		return items

class AllocatedItemInfo(models.Model):
	item = models.ForeignKey(to=Item, on_delete=models.SET_NULL, null=True)
	quantity = models.IntegerField(null=True, blank=True)
	shelf = models.ForeignKey(to=StockShelf, on_delete=models.SET_NULL, null=True)

class ItemAllocation(models.Model):
	relocated = models.ForeignKey(to=ItemRelocationTemp, on_delete=models.SET_NULL, null=True)
	item_info = models.ManyToManyField(ItemRelocationInfo,null=True,blank=True)
	active = models.BooleanField(default=False)
	registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	registered_on = models.DateTimeField(null=True)

	def remaining_item_amount(self,item):
		allocated_items = self.item_info.filter(active=True,item=item)
		relocated_items = self.relocated.item_info.filter(item=item)
		relocated_amount_dict =relocated_items.aggregate(Sum('quantity'))
		allocated_amount_dict =allocated_items.aggregate(Sum('quantity'))
		relocated_amount = relocated_amount_dict['quantity__sum']
		allocated_amount = allocated_amount_dict['quantity__sum']
		return relocated_amount - allocated_amount


"""
class InventoryLocation(models.Model):
	name = models.CharField(max_length=100, null=True)
	stock = models.ForeignKey(InStock, on_delete= models.SET_NULL,null=True)

	def __str__(self):
		return  self.dispensary_name

class Shelf(models.Model):
	shelf_no = models.CharField(null=True, max_length=1000)
	location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
	def __str__(self):
		shelf_no_string = str(self.shelf_no)
		return "Shelf " + shelf_no_string

class Slot(models.Model):
#	drug = models.ForeignKey(Dosage, on_delete= models.SET_NULL, null=True)	
#	product = models.ForeignKey(OtherProducts, on_delete= models.SET_NULL, null=True)
#	quantity = models.IntegerField(null=True)	
	slot_no = models.IntegerField(null=True)
	shelf_no = models.ForeignKey(DispensaryShelf, on_delete=models.SET_NULL, null=True)
	def __str__(self):
		slot_no_string = str(self.slot_no)
		shelf_no_string = str(self.shelf_no)
		return shelf_no_string + " Slot " + slot_no_string
	def get_total_amount(self):
		total_quantity = DispensarySlot.objects.aggregate(Sum('quantity'))

class InventoryItem(models.Model):
	slot_no = models.ForeignKey(DispensarySlot, on_delete=models.SET_NULL, null=True)
	item = models.ForeignKey(Item, on_delete= models.SET_NULL, null=True)	
	quantity = models.IntegerField(null=True)	

	def __str__(self):
		drug_string = str(self.drug)
		return drug_string 


class RelocationTemp(models.Model):
	item = models.ForeignKey(Item, on_delete= models.SET_NULL, null=True)	
	quantity = models.IntegerField(null=True)	
"""