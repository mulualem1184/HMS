from django.db import models
#from django.contrib.auth.models import User
from core.models import Patient
from staff_mgmt.models import Employee 

from django.contrib.auth import get_user_model

User = get_user_model()

#from .tasks import *
# Create your models here.


class OtherProducts(models.Model):
	product_name = models.CharField(max_length=200, null=True)
	date_registered = models.DateTimeField(auto_now_add=True, null=True)
	
#this class holds information related to drug sales to a single patient

# PathologicalFindings refers to the disease in which a drug  
class PathologicalFindings(models.Model):
	#disease : holds list of diseases
	disease = models.CharField(max_length=5000, null=True)
	def __str__(self):
		return self.disease

#contraindication refers to a condition where a drug should not be used
class ContraIndication(models.Model):
	condition = models.CharField(max_length=5000, null=True)
	def __str__(self):
		return self.condition
class SideEffect(models.Model):
	side_effect = models.CharField(max_length=5000, null=True)
	def __str__(self):
		return self.side_effect

#this class holds information about each distnict drug 	
class DrugProfile(models.Model):
	"""
	commercial_name : the name with which the drug will be refered to
	generic_name : the chemical name of the drug
	NDC : unique ten digit code used to identify the drug
	pathological_findings : the diseases that will be treated by this drug
	contraindication : conditions where a this drug should not be used
	tier : differentiates drugs to different levels of cost with tier 1 being the least expensive and tier 4 being the most expensive
	side_effect : information in regards to side effects that may result from this drug
	"""
	tier_list=(
		('Tier 1','Tier 1'),
		('Tier 2','Tier 2'),
		('Tier 3','Tier 3'),
		('Tier 4 ', 'Tier 4'),
		)
	
	commercial_name = models.CharField(max_length=200) #
	generic_name= models.CharField(max_length=200)
	NDC = models.CharField(max_length=12,primary_key=True, help_text= 'National Drug Code')
	pathological_findings = models.ManyToManyField(PathologicalFindings)
	contraindication = models.ManyToManyField(ContraIndication)
	tier = models.CharField(max_length=200, null=True, choices=tier_list)
	side_effect = models.ManyToManyField(SideEffect, blank=True)
#	image = models.ImageField(null=True)
	
#	image = models.ImageField(null=True)
	def __str__(self):
		return self.commercial_name



class DiseaseDrugModel(models.Model):
	drug = models.ForeignKey(DrugProfile,  on_delete= models.SET_NULL, null=True)
	pathological_findings = models.ManyToManyField(PathologicalFindings)

class ContraIndicationDrugModel(models.Model):
	drug = models.ForeignKey(DrugProfile,  on_delete= models.SET_NULL, null=True)
	contraindication = models.ManyToManyField(ContraIndication)

class SideEffectDrugModel(models.Model):
	drug = models.ForeignKey(DrugProfile,  on_delete= models.SET_NULL, null=True)
	side_effect = models.ManyToManyField(SideEffect)

#takes drug info as FK from 'DrugProgile' and adds information regarding the way the drug will be taken
class Route(models.Model):
#	route : the way a patient takes the drug
#	registered_by : the user that registers this information
	route_types=(
			('oral','oral'),
			('sublingual','sublingual'),
			('rectal','rectal'),
			('intravenous','intravenous'),
			('intramuscular','intramuscular'),
			('subcutaneous','subcutaneous'),
			('intranasal','intranasal'),
			('inhaled','inhaled'),
			('vaginal','vaginal'),
			)
	drug = models.ForeignKey(DrugProfile,  on_delete= models.SET_NULL, null=True)
	route = models.CharField(max_length=200, choices=route_types, null=True)
	registered_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)	

	def __str__(self):
		return self.drug.commercial_name

#holds age range information
class AgeRange(models.Model):
	minimum_age = models.PositiveIntegerField(null=True)
	maximum_age = models.PositiveIntegerField(null=True)	

	def __str__(self):
		minimum_age_string = str(self.minimum_age)
		maximum_age_string = str(self.maximum_age)
		return minimum_age_string + " - " + maximum_age_string

#holds weight range information
class WeightRange(models.Model):
	minimum_weight = models.FloatField(null=True)
	maximum_weight = models.FloatField(null=True)

	def __str__(self):
		minimum_age_string = str(self.minimum_weight)
		maximum_age_string = str(self.maximum_weight)
		return minimum_age_string + " - " + maximum_age_string

#takes drug + route info as FK and adds info regarding the dosge amount and form of the drug  
class Dosage(models.Model):
	"""
	drug : foreign key of 'Route' model which holds drug + route info
	age_range : minimum and maximum age of patient permitted to take drug with this dosage amount
	weight_range : minimum and maximum weight of patient permitted to take drug with this dosage amount
	dosage_amount : dosage amount in various units of measurement. eg 'Adrenaline 0.1% in 1ml', 'Amoxacillin 125mg/5ml'
	unit : units of drug  in a single drug item.
	dosage_form : form of the drug. eg 'Capsule', 'Tablet'
	"""
	dosage_forms = (
			('Tablet','Tablet'),
			('Capsule','Capsule'),
			('Oral_solution','Oral_solution'),
			('injection','injection'),
			('injection with diluent','injection with diluent'),
		)


	drug = models.ForeignKey(Route,  on_delete= models.SET_NULL, null=True)
	age_range = models.ForeignKey(AgeRange,  on_delete= models.SET_NULL, null=True)	
	weight_range = models.ForeignKey(WeightRange,  on_delete= models.SET_NULL, null=True)	
	dosage_amount = models.CharField(max_length=200, null=True)
	unit = models.CharField(max_length=200, null=True)
	dosage_form = models.CharField(max_length=200, choices=dosage_forms, null=True)

	def __str__(self):
		return self.drug.drug.commercial_name + self.dosage_amount + " " + self.dosage_form

class DrugPrescriptionInfo(models.Model):
	route_types=(
			('oral','oral'),
			('sublingual','sublingual'),
			('rectal','rectal'),
			('intravenous','intravenous'),
			('intramuscular','intramuscular'),
			('subcutaneous','subcutaneous'),
			('intranasal','intranasal'),
			('inhaled','inhaled'),
			('vaginal','vaginal'),
			)

	time_units=(
			
			('days','days'),
			('weeks','weeks'),
			('months','months'),
		
		)

	frequency_units=(
			
			('a day','a day'),
			('a week','a week'),
			('a month','a month'),
		
		)

	dosage_unit_types=(
			('mg','mg'),
			('ml','ml'),
			('mm','mm'),
			('mmol','mmol'),
			('g','g'),
			('kg','kg'),
			('mmol','mmol'),
			
		)

	drug = models.ForeignKey(Dosage,  on_delete= models.SET_NULL, null=True,blank=True)
	units_per_take = models.IntegerField(max_length=200, null=True,blank=True)
	frequency = models.IntegerField(max_length=200, null=True,blank=True)
	frequency_unit =models.CharField( max_length=200, choices=frequency_units, null=True, blank=True) 
	duration = models.IntegerField(null=True,blank=True)
	duration_unit = models.CharField( max_length=200, choices=time_units,blank=True)
	def __str__(self):
		return str(self.drug) + " - " + str(self.units_per_take) + " Units Per Take - " + str(self.frequency) + " Times " + str(self.frequency_unit) + " For " + str(self.duration) + " " + str(self.duration_unit)



class DrugImage(models.Model):
	active_status = {
		('active','active'),
		('not_active','not_active'),	
	}
	drug = models.ForeignKey(Dosage,  on_delete= models.SET_NULL, null=True)
	image = models.ImageField(null=True)
	active = models.CharField(max_length=100, null=True, choices=active_status)
class DrugAvailabilityStatus(models.Model):
	stock_status = (
		('Available','Available'),
		('Unavailable','Unavailable'),
		('Re-Order Level','Re-Order Level'),
		)
	drug = models.ForeignKey(Dosage,  on_delete= models.SET_NULL, null=True)
	availability_status = models.CharField(max_length=200, choices= stock_status, default='Available')

#holds information about different types of relationship a drug has with drugs, food , alcohol and diseases
class DrugCorelation(models.Model):
	"""
	drug : 
	pathological_findings : foreign key of model 'PathologicalFindings' which holds diseases
	food : 
	alcohol:
	relation: relationship between the above feilds. 
	"""
	drug = models.ForeignKey(Dosage, on_delete= models.SET_NULL, null=True, blank=True)
	pathological_findings = models.ForeignKey(PathologicalFindings, on_delete= models.SET_NULL, null=True, blank=True)
	food = models.CharField(max_length=500, blank=True)
	alcohol = models.CharField(max_length=500, blank=True)
	relation = models.CharField(max_length=2000, blank=True)

class DrugInteraction(models.Model):
	effector_drug = models.ForeignKey(Dosage, on_delete= models.SET_NULL, null=True, related_name='effector_drug')
	affected_drug = models.ForeignKey(Dosage, on_delete= models.SET_NULL, null=True, blank=True, related_name='affected_drug')
	relation = models.CharField(max_length=2000, blank=True)
#	def __str__(self):
#		drug_string = str(self.drug)
#		return  drug_string
	"""
class SimilarDrugs(models.Model):
	pathological_findings = models.ForeignKey(PathologicalFindings, on_delete= models.SET_NULL, null=True)
	drug = models.ManyToManyField(DrugProfile, null=True)
	"""

#holds additional information about how to take drugs
class IntakeMode(models.Model):
	"""
	drug:
	food : whether the drug is taken with empty stomach or with food
	additional_info : 
	"""
	food_or_no_food = (
		('Empty stomach','Empty stomach'),
		('With food','With food'),
		)
	drug = models.ManyToManyField(Dosage, null=True)
	food = models.CharField(max_length=200, null=True, choices= food_or_no_food)
	additional_info = models.CharField(max_length=5000, blank=True, null=True)



class DrugInventory(models.Model):
	pharmacy_name = models.CharField(max_length=1000, null=True)#needs choices
	
class InStock(models.Model):
	inventory = models.ForeignKey(DrugInventory, on_delete=models.SET_NULL, null=True, blank =True)
	stock_name = models.CharField(max_length=500,null=True)
	def __str__(self):
#		stock_no_string = str(self.stock_no)
		return  self.stock_name
class InStockShelf(models.Model):
	shelf_no = models.IntegerField(null=True)
	stock_name = models.ForeignKey(InStock, on_delete= models.SET_NULL,null=True)
	def __str__(self):
		shelf_no_string = str(self.shelf_no)
		stock_no_string = str(self.stock_name)
		return stock_no_string + " Shelf " + shelf_no_string

class InStockSlot(models.Model):
	
	slot_no = models.IntegerField(null=True)
	shelf_no = models.ForeignKey(InStockShelf, on_delete= models.SET_NULL, null=True)
	def __str__(self):
		slot_no_string = str(self.slot_no)
		shelf_no_string = str(self.shelf_no)
		return shelf_no_string + " Slot " + slot_no_string



class InStockSlotDrug(models.Model):
	slot_no = models.ForeignKey(InStockSlot, on_delete=models.SET_NULL, null=True)
	drug = models.ForeignKey(Dosage, on_delete= models.SET_NULL, null=True)	
	quantity = models.IntegerField(null=True)	
	product = models.ForeignKey(OtherProducts, on_delete= models.SET_NULL, null=True)

	def __str__(self):
		drug_string = str(self.drug)
		return drug_string

	@property
	def display_quantity_str(self):
		drug_string = str(self.drug)
		quantity_string = str(self.quantity)
		return drug_string + ", quantity: " + quantity_string  

class Dispensary(models.Model):
	dispensary_name = models.CharField(max_length=100, null=True)
	stock = models.ForeignKey(InStock, on_delete= models.SET_NULL,null=True)

	def __str__(self):
		return  self.dispensary_name

class DispensaryShelf(models.Model):
	shelf_no = models.CharField(null=True, max_length=1000)
	dispensary = models.ForeignKey(Dispensary, on_delete=models.SET_NULL, null=True)
	def __str__(self):
		shelf_no_string = str(self.shelf_no)
		return "Shelf " + shelf_no_string

class DispensarySlot(models.Model):
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

class DispensaryDrug(models.Model):
	slot_no = models.ForeignKey(DispensarySlot, on_delete=models.SET_NULL, null=True)
	drug = models.ForeignKey(Dosage, on_delete= models.SET_NULL, null=True)	
	quantity = models.IntegerField(null=True)	

	def __str__(self):
		drug_string = str(self.drug)
		return drug_string 


class DrugRelocationTemp(models.Model):
	drug = models.ForeignKey(Dosage, on_delete= models.SET_NULL, null=True)	
	quantity = models.IntegerField(null=True)	
	
class DrugSupplyToDispensary(models.Model):
	drug = models.ForeignKey(Dosage, on_delete= models.SET_NULL, null=True)	
	quantity = models.IntegerField(null=True)	
	dispensary = models.ForeignKey(Dispensary, on_delete= models.SET_NULL, null=True)	
	registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
	registered_on = models.DateTimeField(auto_now_add=True, null=True)

	"""
class Pharmacy(models.Model):
	pharmacy_name= models.CharField(max_length=1000, null=True)#needs choices
	on_shelf = models.ForeignKey(DispensaryShelf, on_delete=models.SET_NULL, null=True)
	in_stock = models.ForeignKey(InStock, on_delete=models.SET_NULL, null=True)
	"""

#	drug = models.ForeignKey(Dosage, on_delete= models.SET_NULL, null=True)	
#	quantity = models.IntegerField()
	
class InventoryThreshold(models.Model):
	drug = models.ForeignKey(Dosage,  on_delete= models.SET_NULL, null=True)
	threshold = models.IntegerField(null=True)
"""
class Doctor(models.Model):
	name = models.ForeignKey(User, on_delete= models.SET_NULL, null=True)

	def __str__(self):
		name_string = str(self.name)
		return name_string
"""
class Hospital(models.Model):
	name = models.CharField(max_length=1000, null=True)

	def __str__(self):
		return name

class DrugPrescription(models.Model):
	order_categories = (
			('Emergency','Emergency'),
			('Non_Emergency','Non_Emergency')
			)


	route_types=(
			('oral','oral'),
			('sublingual','sublingual'),
			('rectal','rectal'),
			('intravenous','intravenous'),
			('intramuscular','intramuscular'),
			('subcutaneous','subcutaneous'),
			('intranasal','intranasal'),
			('inhaled','inhaled'),
			('vaginal','vaginal'),
			)

	time_units=(
			
			('days','days'),
			('weeks','weeks'),
			('months','months'),
		
		)

	frequency_units=(
			
			('a day','a day'),
			('a week','a week'),
			('a month','a month'),
		
		)

	dosage_unit_types=(
			('mg','mg'),
			('ml','ml'),
			('mm','mm'),
			('mmol','mmol'),
			('g','g'),
			('kg','kg'),
			('mmol','mmol'),
			
		)
	dispensed=(
			('true','true'),
			('false','false'),
			
		)
	inpatient=(
			('true','true'),
			('false','false'),
			
		)
	department_choices=(
			(1,'Ward'),
			(2,'OPD'),
			(3,'Emergency'),
			
		)

	"""
	diagnosis : identified disease of the patient   	
	frequency : amount of times the drug is taken in a single day
	duration_amount and duration_unit: info for how long the drug is to be taken
	order_category: info regarding whether it is Emergency or Non_Emergency prescription
	registered_on: the time when it was prescribed
	""" 

	units_per_take = models.IntegerField(max_length=200, null=True,blank=True)
	frequency = models.IntegerField(max_length=200, null=True, blank=True)
	frequency_unit =models.CharField( max_length=200, choices=frequency_units, null=True, blank=True) 
	duration_amount = models.IntegerField(null=True, blank=True)
	duration_unit = models.CharField( max_length=200, choices=time_units, blank=True)
	prescriber = models.ForeignKey(Employee, on_delete= models.SET_NULL,  related_name ='prescriber', null=True, blank=True)
	patient = models.ForeignKey(Patient, on_delete= models.SET_NULL, null=True)	
	diagnosis = models.CharField(max_length=1000, null=True, blank=True)
	info = models.ForeignKey(DrugPrescriptionInfo, on_delete= models.SET_NULL,null=True,blank=True) 
	drug = models.ForeignKey(Dosage, on_delete= models.SET_NULL,  related_name ='DrugProfile_name', null=True, blank=True) 
	hospital = models.CharField(max_length=200, null=True)
	order_category = models.CharField(max_length= 200, choices=order_categories, null=True, blank=True)
	registered_on = models.DateTimeField(auto_now_add=True)
	comments = models.CharField(max_length=5000, blank=True)
	dispensed = models.CharField(max_length=5000, blank=True , choices=dispensed, default='false')
	inpatient = models.CharField(max_length=5000, blank=True , choices=inpatient, default='false')
	department = models.CharField(max_length=5000, blank=True , choices=department_choices, default='false')
	prescribed = models.BooleanField(default=False)
	active = models.BooleanField(default=False)
	
	"""
	@property
	def dosage(self):
		return "%s - %s" % ( self.dosage_amount, self.dosage_unit )

	"""
#holds info about groups of the same drug with the same expiration date
class DrugExpiration(models.Model):
	"""
	manufacturing_date: date when drug was manufactered
	expiration_date: date when drug will expire 
	drug: foreign key
	quantity: amount of drugs of the same type with same expiration_date
	"""
	manufacturing_date = models.DateTimeField(null=True)
	expiration_date = models.DateTimeField(null=True)
	drug = models.ForeignKey(Dosage, on_delete= models.SET_NULL, null=True)
	quantity = models.IntegerField()

class RandomRecord(models.Model):
	value = models.CharField(max_length=100, null=True)


class ExpiredDrug(models.Model):
	"""
	drug:
	expiration: takes model 'DrugExpiration' as FK to get quantity and date of drug that expired
	"""	
	drug = models.ForeignKey(DispensaryDrug, on_delete= models.SET_NULL, null=True)
	stock_drug = models.ForeignKey(InStockSlotDrug, on_delete= models.SET_NULL, null=True)
	expiration = models.ForeignKey(DrugExpiration, on_delete= models.SET_NULL, null=True)
	date_expired = models.DateTimeField(null=True)
	expired_quantity = models.PositiveIntegerField(null=True, default=7)

#	def __str__(self):
#		drug_string = (self.drug.drug)
#		return drug_string


	"""
	
	def expiring(self):
		expired_drugs = ExpiredDrug()
		de = DrugExpiration.objects.get(drug=self.drug)
		expiry_date = de.expiration_date
		now = timezone.now()
		if (now - expiry_date).days >0:
			expired_drugs.drug = de.drug
			expired_drugs.expiration = de
			expired_drugs.expired_quantity = expired_drugs.expired_quantity + de.quantity
			expired_drugs.date_expired = de.expiration_date
			expired_drugs.save()	


	"""
				

	
class Procurement(models.Model):

	procurement_no = models.IntegerField(primary_key =True, default=0)
	status = models.CharField( max_length=20, default='pending')
	dispensary = models.ForeignKey(Dispensary, on_delete=models.SET_NULL, null=True)

	def __str__(self):
		procurement_no_string = str(self.procurement_no)
		return "Procurement " + procurement_no_string 

class ProcurementDetail(models.Model):
	procurement_no = models.ForeignKey(Procurement, on_delete= models.SET_NULL, null=True) 
	drug = models.ForeignKey(Dosage, on_delete= models.SET_NULL, null=True)
	quantity = models.IntegerField(null=True)

#this holds info about batch of drugs when a drug is supplied
class Batch(models.Model):

#	batch_no :
	batch_no = models.IntegerField(null=True, blank=True)
	procurement = models.ForeignKey(Procurement, on_delete= models.SET_NULL, null=True, blank=True)
	drug = models.ForeignKey(Dosage, on_delete= models.SET_NULL, null=True)	
	quantity = models.IntegerField(null=True)
	def __str__(self):
		batch_no_str = str(self.batch_no)
		return batch_no_str
 
class Insurance(models.Model):
    insurance_name = models.CharField(db_index=True, primary_key=True, max_length=10)
    patient = models.ForeignKey(Patient,on_delete= models.DO_NOTHING, blank=True, null=True)


class DrugSupply(models.Model):
	drug = models.ForeignKey(Dosage,  on_delete= models.SET_NULL, null=True)
	batch = models.ForeignKey(Batch,  on_delete= models.SET_NULL, null=True,blank=True)
	expiration_date = models.ForeignKey(DrugExpiration, on_delete= models.SET_NULL, null=True)
	supplied_quantity = models.IntegerField(null=True)
	purchasing_cost = models.FloatField(null=True)
	supplier = models.CharField(max_length=200)
#	manufacturer = models.CharField(max_length=200, null=True)
	slot_no = models.ForeignKey(DispensarySlot,  on_delete= models.SET_NULL, null=True, blank=True)
	stock_slot_no = models.ForeignKey(InStockSlot,  on_delete= models.SET_NULL, null=True)
#	shelf_no = models.ForeignKey(DispensaryShelf,  on_delete= models.SET_NULL, null=True)
	registered_on = models.DateTimeField( null=True)
	registered_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

#takes drug as FK and adds sellingprice information
class DrugPrice(models.Model):
	"""
	drug : 
	selling_price : 
	effective_date : date since when the drug is sold with this price 
	"""
	DrugPriceActive=(
		('active','active'),
		('not_active','not_active'),
		)

	
	drug = models.ForeignKey(Dosage,  on_delete= models.SET_NULL, null=True)
#	product = models.ForeignKey(OtherProducts, on_delete= models.SET_NULL, null=True, blank=True)
	selling_price = models.FloatField(null=True)
	discounted_price = models.FloatField(null=True)
	effective_date = models.DateTimeField( null=True)
	active = models.CharField(choices=DrugPriceActive, max_length = 50, blank=True)

	def __str__(self):
		drug_string = str(self.selling_price)
		return drug_string

#generated when drugs are sold	
class Bill(models.Model):
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

class BillDetail(models.Model):
	departments = {('Outpatient','Outpatient'),
				('Inpatient','Inpatient'),
				('Emergency','Emergency'),
	}
	bill = models.ForeignKey(Bill, on_delete=models.CASCADE,null=True, blank=True)	
	drug = models.ForeignKey(Dosage, on_delete=models.CASCADE)
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

	"""
	def get_total_price(self):
		dispensed_drugs = DrugDispensed.objects.filter(bill_no=self)
		total = 0
		for drug in dispensed_drugs:
			total += drug.bill_no.selling_price.selling_price
		return total
	"""
#holds info about drugs that are sold
class DrugDispensed(models.Model):
	"""	
	drug : 
	bill_no: foreign key of model 'Bill'
	prescription:
	sold_quantity: amount that is sold
	selling_price:
	insurance : 
	payment_type: whether cash, credit or insurance was used for payment
	"""	
	payment_types= (
		
		('cash','cash'),
		('credit','credit'),
		)
	drug = models.ForeignKey(Dosage, on_delete= models.SET_NULL, null=True)
	bill_no = models.ForeignKey(BillDetail, on_delete=models.SET_NULL, null=True)
	dispensary = models.ForeignKey(Dispensary, on_delete = models.CASCADE, null=True)
#	sold_quantity = models.IntegerField(null=True)
#	selling_price = models.ForeignKey(DrugPrice, on_delete=models.SET_NULL, null=True)
	payment_type = models.CharField(max_length=500, choices=payment_types)
	insurance = models.ForeignKey(Insurance, on_delete= models.SET_NULL, null=True, blank=True)
	sold_on = models.DateTimeField(auto_now_add=True, null=True)
	clerk = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
	registered_on=models.DateTimeField(auto_now_add=True,null=True, blank=True)

class PatientCredit(models.Model):
	patient =models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)
	credit_amount = models.IntegerField(null=True)

class Symptom(models.Model):
	description = models.CharField(max_length=5000, null=True)

#this holds records regarding drug administration of inpatients
class MedicalAdministrationRecord(models.Model):
	"""
	prescription:
	administered_by: user(usually nurse) that administers the drug
	administration_time: the time that patient takes the drug
	"""
	prescription = models.ForeignKey(DrugPrescription, on_delete = models.CASCADE, null=True)
	administered_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	administration_time = models.DateTimeField(auto_now_add=True, null=True)
	administration_check = models.BooleanField(default=False)

class DispensaryPharmacist(models.Model):
	dispensary = models.ForeignKey(Dispensary, on_delete = models.CASCADE, null=True)
	pharmacist = models.ForeignKey(to=Employee, on_delete=models.SET_NULL, null=True, blank=True)
	active = models.BooleanField(default=True)

class DispensaryCashier(models.Model):
	dispensary = models.ForeignKey(Dispensary, on_delete = models.CASCADE, null=True)
	cashier = models.ForeignKey(to=Employee, on_delete=models.SET_NULL, null=True, blank=True)
	active = models.BooleanField(default=True)

class DispensaryProcurementRequest(models.Model):
	dispensary = models.ForeignKey(DispensaryPharmacist, on_delete = models.CASCADE, null=True)
	#pharmacist = models.ForeignKey(to=Employee, on_delete=models.SET_NULL, null=True, blank=True)
	drug = models.ForeignKey(Dosage, on_delete= models.SET_NULL, null=True)
	quantity = models.IntegerField(null=True)
	active = models.BooleanField(default=True)
	first_approval = models.BooleanField(default=False)
	second_approval = models.BooleanField(default=False)

"""
class SingleProcurementRequest(models.Model):
	request = models.ForeignKey(DispensaryPharmacist, on_delete = models.CASCADE, null=True)
	#pharmacist = models.ForeignKey(to=Employee, on_delete=models.SET_NULL, null=True, blank=True)
	drug = models.ForeignKey(Dosage, on_delete= models.SET_NULL, null=True)
	quantity = models.IntegerField(null=True)
	active = models.BooleanField(default=True)
	first_approval = models.BooleanField(default=False)
	second_approval = models.BooleanField(default=False)
"""