from background_task import background
from .models import *
from django.db.models import Sum

#from django.contrib.auth.models import User
"""
@background(schedule=5)
def create_random_record():
    random_record = RandomRecord.objects.all()
    print(random_record)
"""
@background(schedule=10)
def low_stock_level_alert(threshold_id):
#	print(threshold_id)
	thresholds = InventoryThreshold.objects.all()
	drug_array = []
	for threshold in thresholds:
		drug_array.append(threshold.drug)
	for drug in drug_array:
		print(drug) 

#	for threshold in thresholds:
#		if threshold.threshold <
#		print(threshold.drug, threshold.threshold)

	all_drugs = Dosage.objects.all()
	stock_quantity_array = []

	for drug in drug_array:
		drug_in_stock = InStockSlotDrug.objects.filter(drug=drug)
		stock_quantity_dict = drug_in_stock.aggregate(Sum('quantity'))
		stock_quantity = stock_quantity_dict['quantity__sum']
		stock_quantity_array.append(stock_quantity)
#		print(drug_in_stock.drug, 'stock quantity: ', stock_quantity,'\n')				
#		drug_array.append(drug)
		if 1==1:			
			threshold = InventoryThreshold.objects.get(drug=drug)
			if threshold:
				if 0 < stock_quantity < threshold.threshold:
					availability_status = DrugAvailabilityStatus.objects.get(drug=drug)
					availability_status.availability_status = 'Re-Order Level'
					availability_status.save()
					print(availability_status.availability_status, availability_status.drug)
					print('low level alert', stock_quantity, '<', threshold.threshold)
				elif stock_quantity==0 :
					availability_status = DrugAvailabilityStatus.objects.get(drug=drug)
					availability_status.availability_status = 'Unavailable'
				else:
					print('high level alert', stock_quantity, '<', threshold.threshold)
#		for stock_drug in drug_in_stock:
#			print(stock_drug.drug, stock_drug.quantity)
