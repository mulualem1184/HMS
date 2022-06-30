from django.db.models.signals import * 
from .models import *
from django.dispatch import receiver
from datetime import datetime
#from datetime import timezone
from django.utils import timezone
from .forms import *
from django.db.models import Sum








@receiver(pre_save, sender=DrugSupply)
def DrugSupplySignal(sender, **kwargs):
	instance : DrugSupply = kwargs.get('instance')
	count1 = 0
	count2 = 0
	if instance.stock_slot_no is None:
		slot_objects = OnShelfSlotDrug.objects.filter(slot_no= instance.slot_no)
		
		for slot_object in slot_objects:
			if instance.drug == slot_object.drug:
#				print("yea")
				quantity_before = slot_object.quantity
				quantity_after = quantity_before + instance.supplied_quantity
				slot_object.quantity = quantity_after
				slot_object.save()
				count1 = 1
				expired_drug = ExpiredDrug()
				expired_drug.drug = slot_object
				expired_drug.expiration = instance.expiration_date
				expired_drug.expired_quantity = 0
				expired_drug.save()

		if count1 == 0 :
			new_slot_object = OnShelfSlotDrug()
			new_slot_object.slot_no = instance.slot_no
			new_slot_object.drug = instance.drug
			new_slot_object.quantity = instance.supplied_quantity
			new_slot_object.save()
			expired_drug = ExpiredDrug()
			expired_drug.drug = new_slot_object
			expired_drug.expiration = instance.expiration_date
			expired_drug.expired_quantity = 0
			expired_drug.save()

	else:
#		print('111')
		stock_slot_objects = InStockSlotDrug.objects.filter(slot_no=instance.stock_slot_no)
		
		for stock_slot_object in stock_slot_objects:
#			print(instance.drug, " and ", stock_slot_object.drug,'\n')
			if instance.drug == stock_slot_object.drug:
#				print("eyeah")
				quantity_before = stock_slot_object.quantity
				quantity_after = quantity_before + instance.supplied_quantity
				stock_slot_object.quantity = quantity_after
				stock_slot_object.save()
				count2 = 1
				expired_drug = ExpiredDrug()
				expired_drug.stock_drug = stock_slot_object
				expired_drug.expiration = instance.expiration_date
				expired_drug.expired_quantity = 0
				expired_drug.save()

		if count2 == 0 :
			new_stock_slot_object = InStockSlotDrug()
			new_stock_slot_object.slot_no = instance.stock_slot_no
			new_stock_slot_object.drug = instance.drug
			new_stock_slot_object.quantity = instance.supplied_quantity
#			print(" this is: ", new_stock_slot_object,"\n")
			new_stock_slot_object.save()
			expired_drug = ExpiredDrug()
			expired_drug.stock_drug = new_stock_slot_object
			expired_drug.expiration = instance.expiration_date
			expired_drug.expired_quantity = 0
			expired_drug.save()

@receiver(post_save, sender=DrugSupply)
def DrugSupplySignal(sender, **kwargs):
	instance : DrugSupply = kwargs.get('instance')
	procurement = Procurement.objects.get(procurement_no=instance.batch.procurement.procurement_no)
	
	procurement_details = ProcurementDetail.objects.filter(procurement_no=procurement)
	
	drug_supply = DrugSupply.objects.filter(batch__procurement=procurement)
	procurement_quantity = procurement_details.aggregate(Sum('quantity'))
	procurement_quantity = procurement_quantity['quantity__sum']
	drug_supply_quantity = drug_supply.aggregate(Sum('supplied_quantity'))
	drug_supply_quantity = drug_supply_quantity['supplied_quantity__sum']
	if procurement_quantity - drug_supply_quantity  == 0:
		procurement.status='recieved'
		procurement.save()
	
	remaining_quantity = 0
	supplied_quantity = 0
	total_remaining_quantity = 0
	for procurement_detail in procurement_details:
		drug_supply = DrugSupply.objects.filter(batch__procurement=procurement)
		for drug_supply in drug_supply:
			supplied_quantity = supplied_quantity + drug_supply.supplied_quantity
		remaining_quantity = procurement_detail.quantity - supplied_quantity
		print(procurement_detail.drug,'\n' ,'ordered quantity: ', procurement_detail.quantity, '\n',
		'supplied_quantity: ',supplied_quantity,'\n','remainng quantity : ', remaining_quantity,'\n')
		supplied_quantity = 0		
		total_remaining_quantity = total_remaining_quantity + remaining_quantity
		print(total_remaining_quantity,'\n')
	"""	
		if total_remaining_quantity == 0:
			procurement.status = 'recieved'
			procurement.save()
			print(procurement, procurement.status)
	"""	
@receiver(post_save, sender=BillDetail)
def BillSignal(sender, **kwargs):
	instance : BillDetail = kwargs.get('instance')
	drug_dispensed_model = DrugDispensed()
	drug_dispensed_model.drug = instance.drug 
	drug_dispensed_model.bill_no = instance
	drug_dispensed_model.payment_type = 'cash'
	drug_dispensed_model.sold_on = instance.registered_on
#	drug_dispensed_model.clerk = request.user
	drug_dispensed_model.save() 

"""

@receiver(post_save, sender=DrugSupply)
def DrugSupplySignal(sender, **kwargs):
	instance : DrugSupply = kwargs.get('instance')
	di = DrugInventory.objects.get(drug=instance.drug)
	quantity_before=di.quantity
	quantity_after = quantity_before + instance.supplied_quantity
	di.quantity=quantity_after
	di.save()

	



@receiver(post_save, sender=DrugDispensed)
def DrugDispensedSignal(sender, **kwargs):
	instance : DrugDispensed = kwargs.get('instance')
	di = DrugInventory.objects.get(drug=instance.drug)
	quantity_before=di.quantity
	quantity_after = quantity_before - instance.sold_quantity
	di.quantity=quantity_after
	di.save()

@receiver(post_save, sender=ExpiredDrug)
def DrugDispensedSignal(sender, **kwargs):
	instance : ExpiredDrug = kwargs.get('instance')
	di = DrugInventory.objects.get(drug=instance.drug)
	quantity_before=di.quantity
	quantity_after = quantity_before - instance.expired_quantity
	di.quantity=quantity_after
	di.save()

"""
"""
@receiver(post_save, sender=DrugExpiration)
def DrugExpiredSignal(sender, **kwargs):
	instance : DrugExpiration = kwargs.get('instance')
	expired_drugs = ExpiredDrug()
	expiry_date = instance.expiration_date
	now = timezone.now()
	if (now - expiry_date).days >0:
		expired_drugs.drug = instance.drug
		expired_drugs.expiration = instance
		expired_drugs.expired_quantity = expired_drugs.expired_quantity + instance.quantity
		expired_drugs.date_expired = instance.expiration_date
		expired_drugs.save()


@receiver(post_save, sender=DrugExpiration)
def DrugReorderSignal(sender, **kwargs):

"""

"""
			
@receiver(post_save, sender=DrugDispensed)
def DrugDispensedSignal(sender, **kwargs):
	instance : DrugDispensed = kwargs.get('instance')
	di = DrugInventory.objects.get(drug=instance.drug)
	quantity_before=di.quantity
	quantity_after = quantity_before - instance.sold_quantity
	di.quantity=quantity_after
	di.save()
	it = InventoryThreshold.objects.get(drug=instance.drug)
	if di.quantity > it.threshold:
		return 

"""
