from django.shortcuts import render
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from django.http import JsonResponse

from .models import *
from outpatient_app.models import OutpatientMedication, PatientVisit
from core.models import PatientPaymentStatus
from billing_app.models import CashierDebt, CashierReconcilation
from django.db.models import Sum
from .forms import *
from datetime import datetime

from .tasks import *
from django.contrib import messages

from django.forms.models import modelformset_factory
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa

from django.urls import reverse
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render, get_object_or_404
from collections import OrderedDict
from .fusioncharts import FusionCharts

def render_to_pdf(template_src, context_dict={}):
	template = get_template(template_src)
	html  = template.render(context_dict)
	result = BytesIO()
	pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
	if not pdf.err:
		return HttpResponse(result.getvalue(), content_type='application/pdf')
	return None

"""
data = {
	"company": "Dennnis Ivanov Company",
	"address": "123 Street name",
	"city": "Vancouver",
	"state": "WA",
	"zipcode": "98663",


	"phone": "555-555-2345",
	"email": "youremail@dennisivy.com",
	"website": "dennisivy.com",
	}
"""
#Opens up page as PDF
class ViewPDF(View):
	def get(self, request, *args, **kwargs):

		pdf = render_to_pdf('pharmacy_app/daily_rx_report3.html', data)
		return HttpResponse(pdf, content_type='application/pdf')


#Automaticly downloads to PDF file
class DownloadPDF(View):
	def get(self, request, *args, **kwargs):
		all_drugs = Dosage.objects.all()
		slot_drugs = DispensarySlot.objects.all()
		drug_array = []
		shelf_quantity_array = []
		stock_quantity_array = []
		total_quantity_array = []
		stock_array = []
		alert_array = []
		alert_drug_array = []
		for drug in all_drugs:
			#drug on slot is drugs that are in dispensaries
			#drug in stock are drugs in stocks
			drug_on_slot = DispensaryDrug.objects.filter(drug=drug)
			drug_in_stock = InStockSlotDrug.objects.filter(drug=drug)

			#shelf quantity is quantity of drug in dispensaries
			shelf_quantity_dict = drug_on_slot.aggregate(Sum('quantity'))
			shelf_quantity = shelf_quantity_dict['quantity__sum']
			if shelf_quantity is None:
				shelf_quantity = 0
			shelf_quantity_array.append(shelf_quantity)
			print(drug, 'shelf quantity:',shelf_quantity,'\n')

			#stock quantity is quantity of drug in stocks
			stock_quantity_dict = drug_in_stock.aggregate(Sum('quantity'))
			stock_quantity = stock_quantity_dict['quantity__sum']
			if stock_quantity is None:
				stock_quantity = 0
			stock_quantity_array.append(stock_quantity)

			print(drug, 'stock quantity: ', stock_quantity,'\n')

			total_quantity = shelf_quantity + stock_quantity
			total_quantity_array.append(total_quantity)
			print('total_quantity :', total_quantity,'\n')

			drug_array.append(drug)
			inventory_zip = zip(drug_array, total_quantity_array)
			data = {'inventory_zip': inventory_zip}

			total_quantity = 0
			shelf_quantity = 0 
			stock_quantity = 0
		
		pdf = render_to_pdf('pharmacy_app/daily_rx_report3.html', data)

		response = HttpResponse(pdf, content_type='application/pdf')
		filename = "Report_%s.pdf" %("12341231")
		content = "attachment; filename=%s" %(filename)
		response['Content-Disposition'] = content
		return response

def DailyRxReport(request):

	all_drugs = Dosage.objects.all()
	slot_drugs = DispensarySlot.objects.all()
	drug_array = []
	shelf_quantity_array = []
	stock_quantity_array = []
	total_quantity_array = []
	stock_array = []
	alert_array = []
	alert_drug_array = []
	for drug in all_drugs:
		#drug on slot is drugs that are in dispensaries
		#drug in stock are drugs in stocks
		drug_on_slot = DispensaryDrug.objects.filter(drug=drug)
		drug_in_stock = InStockSlotDrug.objects.filter(drug=drug)

		#shelf quantity is quantity of drug in dispensaries
		shelf_quantity_dict = drug_on_slot.aggregate(Sum('quantity'))
		shelf_quantity = shelf_quantity_dict['quantity__sum']
		if shelf_quantity is None:
			shelf_quantity = 0
		shelf_quantity_array.append(shelf_quantity)
		print(drug, 'shelf quantity:',shelf_quantity,'\n')

		#stock quantity is quantity of drug in stocks
		stock_quantity_dict = drug_in_stock.aggregate(Sum('quantity'))
		stock_quantity = stock_quantity_dict['quantity__sum']
		if stock_quantity is None:
			stock_quantity = 0
		stock_quantity_array.append(stock_quantity)

		print(drug, 'stock quantity: ', stock_quantity,'\n')

		total_quantity = shelf_quantity + stock_quantity
		total_quantity_array.append(total_quantity)
		print('total_quantity :', total_quantity,'\n')

		drug_array.append(drug)
		if InventoryThreshold.objects.get(drug=drug):
			threshold = InventoryThreshold.objects.get(drug = drug)
		print('ddddddddddd',total_quantity, 'ccccccccccccc',threshold.threshold)
		#if drug quantity in shelf and dispensary is less than its threshold it is in low stock level
		if total_quantity < threshold.threshold:
			alert_array.append(threshold.threshold - total_quantity)
			alert_drug_array.append(drug)
			alert_zip = zip(alert_drug_array, alert_array)
			inventory_zip = zip(drug_array, total_quantity_array)
			for a,b in alert_zip:
				print('\n',a,b,'\n')
			context = {'inventory_zip': inventory_zip, 'alert_zip':alert_zip}
		else:
			inventory_zip = zip(drug_array, total_quantity_array)
			context = {'inventory_zip': inventory_zip}

		total_quantity = 0
		shelf_quantity = 0 
		stock_quantity = 0
		"""
		except:
			drug_array.append(drug)
			total_quantity_array.append(0)
			inventory_zip = zip(drug_array, total_quantity_array)
			context = {'inventory_zip': inventory_zip}
		"""
	return render(request, 'pharmacy_app/daily_rx_report3.html', context)

def PharmacyReport(request):

	all_drugs = Dosage.objects.all()
	slot_drugs = DispensarySlot.objects.all()
	drug_array = []
	shelf_quantity_array = []
	stock_quantity_array = []
	total_quantity_array = []
	stock_array = []
	alert_array = []
	alert_drug_array = []
	for drug in all_drugs:
		#drug on slot is drugs that are in dispensaries
		#drug in stock are drugs in stocks
		drug_on_slot = DispensaryDrug.objects.filter(drug=drug)
		drug_in_stock = InStockSlotDrug.objects.filter(drug=drug)

		#shelf quantity is quantity of drug in dispensaries
		shelf_quantity_dict = drug_on_slot.aggregate(Sum('quantity'))
		shelf_quantity = shelf_quantity_dict['quantity__sum']
		if shelf_quantity is None:
			shelf_quantity = 0
		shelf_quantity_array.append(shelf_quantity)
		print(drug, 'shelf quantity:',shelf_quantity,'\n')

		#stock quantity is quantity of drug in stocks
		stock_quantity_dict = drug_in_stock.aggregate(Sum('quantity'))
		stock_quantity = stock_quantity_dict['quantity__sum']
		if stock_quantity is None:
			stock_quantity = 0
		stock_quantity_array.append(stock_quantity)

		print(drug, 'stock quantity: ', stock_quantity,'\n')

		total_quantity = shelf_quantity + stock_quantity
		total_quantity_array.append(total_quantity)
		print('total_quantity :', total_quantity,'\n')

		drug_array.append(drug)
		if InventoryThreshold.objects.get(drug=drug):
			threshold = InventoryThreshold.objects.get(drug = drug)
		print('ddddddddddd',total_quantity, 'ccccccccccccc',threshold.threshold)
		#if drug quantity in shelf and dispensary is less than its threshold it is in low stock level
		if total_quantity < threshold.threshold:
			alert_array.append(threshold.threshold - total_quantity)
			alert_drug_array.append(drug)
			alert_zip = zip(alert_drug_array, alert_array)
			inventory_zip = zip(drug_array, total_quantity_array)
			#for a,b in alert_zip:
			#	print('\n',a,b,'\n')
			context = {'inventory_zip': inventory_zip, 'alert_zip':alert_zip}
		else:
			inventory_zip = zip(drug_array, total_quantity_array)
			context = {'inventory_zip': inventory_zip}
		"""
		inventory_zip = zip(drug_array, total_quantity_array)
		context = {'inventory_zip': inventory_zip}
		"""
		total_quantity = 0
		shelf_quantity = 0 
		stock_quantity = 0

	return render(request, 'pharmacy_app/pharmacy_report.html', context)

def BillFormPage(request,pk, pk2):
	"""
	This function generates bill model object as clerk dispenses drug from prescriptions
	pk: primary key of DrugPrescription 
	"""
	last_bill_no = pk2
	new_pk = pk2 + 1
	bill = Bill()
	bill.bill_no = new_pk
	if ( bill.bill_no - pk2 == 1):
		bill.save()
	bill_number = bill.bill_no
#	print('\n','bill no equals ',bill.bill_no,'\n')
	prescription = DrugPrescription.objects.get(id=pk) 
	stock_slot_id_array = []
#	stock_slot = InStockSlot.objects.first()

	dispension_form = DispensionForm()
	
	
#	bill_formset = BillFormSet(request.POST or None)
	qr = DispensaryDrug.objects.none()
	DispensionFormset = modelformset_factory(DispensaryDrug, form=DispensionForm, extra=0)
	dispension_formset = DispensionFormset(request.POST or None, queryset=qr)
	
	"""
	small bill formset is used in case clerk has to dispense drugs outside
	the ones that were prescribed.
	"""
	qs = BillDetail.objects.none()
	SmallBillFormset = modelformset_factory(BillDetail, form=SmallBillForm, extra=0)
	small_bill_formset = SmallBillFormset(request.POST or None, queryset=qs)
	
	"""
	the code below appends ids of shelf slots that contain the drug that was prescribed
	to 'stock_slot_id_array' variable  
	"""
	stock_slots = DispensarySlot.objects.all()		
	for stock_slot in stock_slots:	
		slot_drug = stock_slot.dispensarydrug_set.filter(drug_id=prescription.info.drug.id).first()
		if slot_drug:
			stock_slot_id_array.append(stock_slot.id)			



	"""
	below the code assigns a queryset of slot objects whose ids are in 'stock_slot_id_array' 
	variable to 'stock_slots' variable
	Then the queryset of form 'dispension_form' field 'slot_no' is reduced to just the above 
	queryset in variable 'stock_slots' (only the slots that contain prescribed drug)  
	"""
	stock_slots = DispensarySlot.objects.filter(id__in=stock_slot_id_array)
	#check later	dispension_form.fields["slot_no"].queryset = stock_slots
	"""
	form 'bill_form' attributes 'bill' and 'drug' are initialized with the 
	newly generated bill attribute and prescribed drug, respectively.
	"""
	nedded_unit = 0
	if prescription.info.duration_unit == 'months':
		da = prescription.info.duration
		fq = int(prescription.info.frequency)
		nedded_unit = da * fq * 30 
	elif prescription.info.duration_unit == 'weeks':
		da = prescription.info.duration
		fq = int(prescription.info.frequency)
		nedded_unit = da * fq * 7
	else:
		da = prescription.info.duration
		fq = int(prescription.info.frequency)
		nedded_unit = da * fq 	
		print('needed unit is : ', nedded_unit,'\n', 'unit per take is ', prescription.info.units_per_take)
	prescribed_drug_quantity = nedded_unit / int(prescription.info.drug.unit)
	print('\n',prescribed_drug_quantity)

	bill_detail = BillDetail()
	bill_detail.drug = prescription.info.drug
	payment_status = PatientPaymentStatus.objects.get(patient=prescription.patient,active=True)
	price = DrugPrice.objects.get(drug=prescription.info.drug,active='active')
	bill_detail.selling_price = price

	if payment_status.payment_status=='Free':
		bill_detail.free = True
		bill_detail.discount = False
		bill_detail.insurance = False
		bill_detail.credit = False
		bill_detail.selling_price = None

	elif payment_status.payment_status == 'Insurance':
		bill_detail.free = False
		bill_detail.discount = False
		bill_detail.insurance = True
		bill_detail.credit = False

	elif payment_status.payment_status == 'discount':
		bill_detail.free = False
		bill_detail.discount = True
		bill_detail.insurance = False
		bill_detail.credit = False

	else:
		bill_detail.free = False
		bill_detail.discount = False
		bill_detail.insurance = False
		bill_detail.credit = False
	bill_detail.department = 'Outpatient'
	bill_detail.registered_on = datetime.now()
	bill_detail.patient = prescription.patient
	bill_detail.quantity = prescribed_drug_quantity

	bill_detail.registered_by = Employee.objects.get(user_profile=request.user, designation__name='Cashier')
	today = datetime.today()
	#today = now.day
	if CashierDebt.objects.filter(cashier__user_profile=request.user, reconciled=False, debt_date=today).last():
		cashier_debt = CashierDebt.objects.get(cashier__user_profile=request.user, reconciled=False, debt_date=today)
		cashier_debt.cash_debt = cashier_debt.cash_debt + (bill_detail.selling_price.selling_price * bill_detail.quantity)
	else:
		cashier_debt = CashierDebt()
		cashier_debt.cashier = 	Employee.objects.get(user_profile=request.user, designation__name='Cashier')
		cashier_debt.cash_debt = bill_detail.selling_price.selling_price * bill_detail.quantity 
		cashier_debt.date = today


	slot_form = DispensionForm()
	slot_form.fields["slot_no"].queryset = stock_slots	
	if request.method == 'POST':
		slot_form = DispensionForm(request.POST)
		if slot_form.is_valid():
			slot_model = slot_form.save(commit=False)
			slot_drug = DispensaryDrug.objects.get(slot_no=slot_model.slot_no, drug = bill_detail.drug)
			if slot_drug.quantity - bill_detail.quantity > 0:
				slot_drug.quantity = slot_drug.quantity - bill_detail.quantity
				prescription.dispensed = 'true'
				cashier_debt.save()
				slot_model.save()
				prescription.save()		
				bill_detail.save()
				messages.success(request,'Successful!')
				return redirect('prescription_list')

			else:
				messages.error(request, str(slot_drug.slot_no) + " Doesn't Have Enough Quantity!")

	"""
	
	discount_form = DiscountForm(initial={'discount':'No'})
	payment_type_form = PaymentTypeForm(initial={'payment_type':'cash'})
	total_price = 0
	#prescription_quantity = (prescription.drug.unit % (prescription.units_per_take * prescription.frequency))
	bill_form = BillForm(initial={'bill':bill,'drug':prescription.drug,'quantity':int(prescribed_drug_quantity)})
	
	if request.method == 'POST':
		bill_form = BillForm(request.POST, initial={'bill':bill, 'drugs':prescription.drug})
		small_bill_formset = SmallBillFormset(request.POST)
		discount_form = DiscountForm(request.POST,initial={'discount':'Yes'} )
		payment_type_form = PaymentTypeForm(request.POST)
		if all([bill_form.is_valid(), small_bill_formset.is_valid()]):
			bill_detail_model = bill_form.save(commit=False)
			discount_object = discount_form.save(commit=False)			
#			bill_detail_model.drug = prescription.drug 
			'selling_price' field on Bill model is a foreign key object of DrugPrice model
			DrugPrice model holds past and present prices of all drugs in the hospital and has 'active' field to identify which price is the current price
			drug_price = DrugPrice.objects.get(drug=bill_detail_model.drug, active='active')
			if discount_object.discount =='Yes':
				bill_detail_model.discount = 'Yes'
			else:
				bill_detail_model.discount = 'No'
			bill_detail_model.selling_price = drug_price
			bill_detail_model.patient = prescription.patient
			bill_detail_model.registered_on = datetime.now()
			bill_detail_model.save()
			total_price = total_price + (drug_price.selling_price * bill_detail_model.quantity)
			dispension_form = DispensionForm(request.POST)
			stock_slot_model = dispension_form.save(commit=False)
			slot_drug = DispensaryDrug.objects.get(slot_no=stock_slot_model.slot_no, drug = bill_detail_model.drug)
			
			for form in small_bill_formset:
				small_bill_detail_model = form.save(commit=False)
				small_bill_detail_model.bill = bill 
				drug_price = DrugPrice.objects.get(drug=small_bill_detail_model.drug, active='active')
				if discount_form:
					small_bill_detail_model.selling_price = drug_price
					small_bill_detail_model.discount = 'Yes'

				else:
					small_bill_detail_model.selling_price = drug_price
				small_bill_detail_model.patient = prescription.patient
				small_bill_detail_model.registered_on = datetime.now()
				small_bill_detail_model.save()
				total_price = total_price + (drug_price.selling_price * small_bill_detail_model.quantity)
				print('\n', total_price,'llllss', drug_price.selling_price, 'qu', small_bill_detail_model.quantity,'\n')
			#after bill is saved 'dispensed' attribute of the prescription is set to true 
			payment_type_form = payment_type_form.save(commit=False)
			if payment_type_form.payment_type == 'credit':
				try:
					patient_credit = PatientCredit.objects.get(patient=prescription.patient)
					patient_credit.credit_amount = patient_credit.credit_amount + total_price
					print('\n', total_price,'llllss')
					
					patient_credit.save()
				except:
					new_patient_credit = PatientCredit()
					new_patient_credit.patient = prescription.patient
					new_patient_credit.credit_amount =  total_price
					print('\n', total_price,'lllls4s')
					new_patient_credit.save()

			prescription.dispensed = 'true'
			prescription.save()		
			return redirect('bill_detail', pk = bill.bill_no)
			#slot_drug.save()
#			bill_model.selling_price = 
		else:
			print('bill form error ', bill_form.errors)

#		dispension_form = Dispe

	context = {'bill_form':bill_form,'dispension_form':dispension_form, 'bill':bill,'small_bill_formset':small_bill_formset,
				'dispension_formset': dispension_formset, 'discount_form':discount_form, 'payment_type_form':payment_type_form  }
			"""

	context = {'slot_form':slot_form,
				'bill':bill,
	}
	return render(request, 'pharmacy_app/bill_form2.html', context)


#this function shows where in the inventory the drug can be found
def DrugLocation(request, pk):
	stock_quantity_array = []
	shelf_quantity_array = []
	drug_array = []
	stock_array = []
	shelf_array = []
	stock_quantity = 0
	shelf_quantity = 0
	stocks = InStock.objects.all()
	drug_image_form = DrugImageForm()
	drug = Dosage.objects.get(id=pk)
	for stock in stocks: 
		stock_shelfs = InStockShelf.objects.filter(stock_name=stock)		
		for stock_shelf in stock_shelfs:
			stock_slots = InStockSlot.objects.filter(shelf_no=stock_shelf)		
			for stock_slot in stock_slots:	
				slot_drugs = stock_slot.instockslotdrug_set.filter(drug_id=pk)
				if slot_drugs:
					if stock not in stock_array:
						stock_array.append(stock)
						for slot_drug in slot_drugs:
							stock_quantity = stock_quantity + slot_drug.quantity
					else:
						for slot_drug in slot_drugs:
							stock_quantity = stock_quantity + slot_drug.quantity
		if stock_quantity > 0 :
			stock_quantity_array.append(stock_quantity)

		stock_quantity = 0
		stock_zip = zip(stock_array, stock_quantity_array)
	"""
	shelfs = OnShelf.objects.all()
	for shelf in shelfs: 
		shelf_slots = DispensarySlot.objects.filter(shelf_no=shelf)		
		for shelf_slot in shelf_slots:	
			slot_drugs = shelf_slot.onshelfslotdrug_set.filter(drug_id=pk)
			if slot_drugs:
				print("yea")
				if shelf not in shelf_array:
					shelf_array.append(shelf)
					for slot_drug in slot_drugs:
						shelf_quantity = shelf_quantity + slot_drug.quantity
				
				else:
					for slot_drug in slot_drugs:
						shelf_quantity = shelf_quantity + slot_drug.quantity
						print(shelf_quantity)
		if shelf_quantity > 0 :
			shelf_quantity_array.append(shelf_quantity)
		shelf_quantity = 0
		
		shelf_zip = zip(shelf_array, shelf_quantity_array)
	
	if request.method == 'POST':
		drug_image_form = DrugImageForm(request.POST)
		if drug_image_form.is_valid():
			drug_image_model = drug_image_form.save(commit=False)
			drug_image_model.drug = Dosage.objects.filter(id=pk)
			drug_image_model.save()
			print(drug_image_model)
	"""		
#	print("nnn",drug_image_form," + ", stock_quantity_array)
#	image = DrugImage.objects.filter(drug_id=pk)
	context = {'stock_zip':stock_zip,'pk2':pk,'drug':drug}
	return render(request, 'pharmacy_app/drug_location.html', context)


# Create your views here.
def SupplyReportPage(request):
	
	
	context = {}
	return render(request, 'pharmacy_app/drug_supply_report.html')

#this function allows user to create drug profiles
def DrugProfileFormPage(request):
	drug_profile_form = DrugProfileForm()
	route_form = RouteForm()
	dosage_model_form = DosageForm()
	route_model = None
	drug_profile_model = None


	qs = PathologicalFindings.objects.none()
	DiseaseFormset = modelformset_factory(PathologicalFindings, form=DiseaseForm, extra=0)
	disease_formset = DiseaseFormset(request.POST or None, queryset=qs)
	
	qr = ContraIndication.objects.none()
	ContraIndicationFormset = modelformset_factory(ContraIndication, form=ContraIndicationForm, extra=0)
	contraindication_formset = ContraIndicationFormset(request.POST or None, queryset=qr)

	qt = SideEffect.objects.none()
	SideEffectFormset = modelformset_factory(SideEffect, form=SideEffectForm, extra=0)
	side_effect_formset = SideEffectFormset(request.POST or None, queryset=qt)

	all_drugs = DrugProfile.objects.all()
	drug_list = Dosage.objects.all()
	if request.method == 'POST':
		drug_profile_form= DrugProfileForm(request.POST)
		if drug_profile_form.is_valid():
			for drug in all_drugs:
#				if drug_profile_model.commercial_name == drug.commercial_name:
#					print('nothin')
#				else:
				drug_profile_model = drug_profile_form.save()
		else:
			print('drug profile form error', drug_profile_form.errors)
		
		route_form = RouteForm(request.POST)
		if route_form.is_valid():
			route_model = route_form.save()
			route_model.drug = drug_profile_model
			route_model.registered_by = request.user
			route_model.save()
		else:
			print('route form error', route_form.errors)
		
		dosage_model_form = DosageForm(request.POST)
		if dosage_model_form.is_valid():
			dosage_model = dosage_model_form.save()
			dosage_model.drug = route_model
			dosage_model.save()
			messages.success(request,'Drug Successfully Created!')
		else:
			print('dosage error is' , dosage_model_form.errors)

	context = {'drug_profile_form' : drug_profile_form, 'route_form':route_form,
				'dosage_model_form' :dosage_model_form, 'disease_formset':disease_formset,
				'contraindication_formset':contraindication_formset, 
				'side_effect_formset': side_effect_formset,
				'drug_list': drug_list,

				}
	return render(request,'pharmacy_app/drug_profile_form_page.html',context)		


def PrescriptionInfoFormPage(request, drug_id,row):
	if row==None:
		row=1	
	drug = Dosage.objects.get(id=drug_id)
	prescription_info = DrugPrescriptionInfo.objects.filter(drug=drug)

	info_form = PrescriptionInfoForm()
	"""
	if request.method == 'POST':
		print('here333')
		fr_list = request.POST.getlist('frequency')
		for f in fr_list:
			print(f,'Yeah','\n')
		info_form = PrescriptionInfoForm()
		context = {'info_form':info_form, 'row':row, 'drug':drug}
		return render(request,'pharmacy_app/partials/prescription_info_form_partial.html', context)
	"""
	if request.htmx:
		row=row
		print('here111')
		info_form = PrescriptionInfoForm(request.POST) 
		if info_form.is_valid():
			print('here222')

			info_model = info_form.save(commit=False)
			info_model.drug = drug
			info_model.save()
		info_form = PrescriptionInfoForm()
		context = {'info_form':info_form, 'row':row, 'drug':drug}
		return render(request,'pharmacy_app/partials/prescription_info_form_partial.html', context)

	context = {'drug':drug,'info_form':info_form ,'prescription_info':prescription_info, 'row':row}
	return render(request, 'pharmacy_app/prescription_info_form.html', context)

#this function allows users to create one to many relationships between drugs and diseases 
def DiseaseDrugFormPage(request):

	qs = PathologicalFindings.objects.none()
	DiseaseFormset = modelformset_factory(PathologicalFindings, form=DiseaseForm, extra=0)
	disease_formset = DiseaseFormset(request.POST or None, queryset=qs)


#	drug_form = DrugFieldForm()
	disease_drug_form = DiseaseDrugForm()
	if request.method == 'POST':
#		drug_form = DrugFieldForm(request.POST)
		disease_drug_form = DiseaseDrugForm(request.POST)
		disease_formset = DiseaseFormset(request.POST)
		if all([ disease_drug_form.is_valid, disease_formset.is_valid]):
			disease_drug_model = disease_drug_form.save()

			for form in disease_formset:
				disease_formset_entry = form.save(commit=False)
				disease = disease_formset_entry.disease				
				disease_drug_model.pathological_findings.add(disease)
			disease_drug_model.save()
		else:
			print('\n',disease_drug_form.errors, disease_formset.errors,'\n')
	context = {'disease_formset':disease_formset,  'disease_drug_form':disease_drug_form}
	return render(request,'pharmacy_app/disease_drug_form.html',context)

#this function allows users to create one to many relationships between drugs and contraindication
def ContraIndicationDrugFormPage(request):
	qr = ContraIndication.objects.none()
	ContraIndicationFormset = modelformset_factory(ContraIndication, form=ContraIndicationForm, extra=0)
	contraindication_formset = ContraIndicationFormset(request.POST or None, queryset=qr)

	
	contraindication_drug_form = ContraIndicationDrugForm()
	if request.method == 'POST':
		contraindication_drug_form = ContraIndicationDrugForm(request.POST)
		if all([contraindication_drug_form.is_valid]):
			contraindication_drug_model = contraindication_drug_form.save()
			"""
			for form in disease_formset:
				disease_formset_entry = form.save(commit=False)
				disease = disease_formset_entry.disease				
				drug_profile_object.pathological_findings.add(disease)
			drug_profile_object.save()
			"""
	context = {'contraindication_drug_form':contraindication_drug_form}
	return render(request,'pharmacy_app/contraindication_drug_form.html',context)

#this function allows users to create one to many relationships between drugs and side effects
def SideEffectDrugFormPage(request):
	qt = SideEffect.objects.none()
	SideEffectFormset = modelformset_factory(SideEffect, form=SideEffectForm, extra=0)
	side_effect_formset = SideEffectFormset(request.POST or None, queryset=qt)

	
	side_effect_drug_form = SideEffectDrugForm()
	if request.method == 'POST':
		side_effect_drug_form = SideEffectDrugForm(request.POST)
		if all([side_effect_drug_form.is_valid]):
			side_effect_drug_model = side_effect_drug_form.save()
			"""
			for form in disease_formset:
				disease_formset_entry = form.save(commit=False)
				disease = disease_formset_entry.disease				
				drug_profile_object.pathological_findings.add(disease)
			drug_profile_object.save()
			"""
	context = { 'side_effect_drug_form':side_effect_drug_form}
	return render(request,'pharmacy_app/side_effect_drug_form.html',context)


	"""
def (request):
	return render(request,'pharmacy_app/trial.html')
	"""
#this function allows users to create a variant of an already existing drug profile by giving it different dosage attributes  
def DosageFormPage(request):
	drug_profile_list=DrugProfile.objects.all()
	full_route_form = FullRouteForm()
#	full_route_form.fields["drug"].queryset = DrugProfile.objects.filter(NDC=1245487)

	dosage_form = DosageForm()
	print(request.user)
	if request.method == 'POST':
		full_route_form = FullRouteForm(request.POST)
#		full_route_form.fields["drug"].queryset = Dosage.objects.filter(id=4)

		if full_route_form.is_valid():
			route_model = full_route_form.save(commit=False)
			route_model.registered_by = request.user
			route_model.save()
		else:
			print(full_route_form.errors)
		dosage_form = DosageForm(request.POST)
		if dosage_form.is_valid():
			dosage_model = dosage_form.save(commit=False)
			dosage_model.drug = route_model 
			dosage_model.save()

	context = {'full_route_form':full_route_form,'dosage_form':dosage_form}
	return render(request,'pharmacy_app/dosage_form.html',context)

#this function would display available drugs and their amount in the hospital
def DrugInventory(request):
	all_drugs = Dosage.objects.all()
	slot_drugs = DispensarySlot.objects.all()
	drug_array = []
	shelf_quantity_array = []
	stock_quantity_array = []
	total_quantity_array = []
	stock_array = []
	alert_array = []

	for drug in all_drugs:
		try:
			#drug on slot is drugs that are in dispensaries
			#drug in stock are drugs in stocks
			drug_on_slot = DispensaryDrug.objects.filter(drug=drug)
			drug_in_stock = InStockSlotDrug.objects.filter(drug=drug)

			#shelf quantity is quantity of drug in dispensaries
			shelf_quantity_dict = drug_on_slot.aggregate(Sum('quantity'))
			shelf_quantity = shelf_quantity_dict['quantity__sum']
			shelf_quantity_array.append(shelf_quantity)
			print(drug, 'shelf quantity:',shelf_quantity,'\n')

			#stock quantity is quantity of drug in stocks
			stock_quantity_dict = drug_in_stock.aggregate(Sum('quantity'))
			stock_quantity = stock_quantity_dict['quantity__sum']
			stock_quantity_array.append(stock_quantity)
			print(drug, 'stock quantity: ', stock_quantity,'\n')

			total_quantity = shelf_quantity + stock_quantity
			total_quantity_array.append(total_quantity)
			print('total_quantity :', total_quantity,'\n')
	#		temp = InStockSlotDrug.objects.filter(slot_no__shelf_no__stock_name__stock_name = not )
	#		for t in temp:
	#			print(t, t.quantity,'\n')
			if InventoryThreshold.objects.get(drug=drug):
				threshold = InventoryThreshold.objects.get(drug = drug)
			
			#if drug quantity in shelf and dispensary is less than its threshold it is in low stock level
			if total_quantity < threshold.threshold:
				alert_array.append("Low Stock Level")
			else:
				alert_array.append("") 			
			drug_array.append(drug)
			inventory_zip = zip(drug_array, total_quantity_array, alert_array)
			context = {'inventory_zip': inventory_zip}
			total_quantity = 0
			shelf_quantity = 0 
			stock_quantity = 0
		except:
			drug_array.append(drug)
			total_quantity_array.append(0)
			alert_array.append("Low Stock Level")
			inventory_zip = zip(drug_array, total_quantity_array, alert_array)
			context = {'inventory_zip': inventory_zip}

		print (inventory_zip, '\n')
		#	print('drug :',drug_array, 'quantity: ', quantity_now_array ,'\n','\n')
	return render(request,'pharmacy_app/drug_inventory.html', context)

def DrugLocationStockShelf(request,pk,pk2):
	print('stock pk :',pk,' drug pk:',pk2,'\n')
	
	shelf_quantity_array = []
	stock_shelf_array = []
	stock_quantity = 0
	stock_shelf_quantity = 0
	drug = Dosage.objects.get(id=pk2)
	stock_shelfs = InStockShelf.objects.filter(stock_name_id=pk)		
	for stock_shelf in stock_shelfs:
		stock_slots = InStockSlot.objects.filter(shelf_no=stock_shelf)		
		for stock_slot in stock_slots:	
			slot_drugs = stock_slot.instockslotdrug_set.filter(drug_id=pk2)
			if slot_drugs:
				if stock_shelf not in stock_shelf_array:
					stock_shelf_array.append(stock_shelf)
					for slot_drug in slot_drugs:
						stock_shelf_quantity = stock_shelf_quantity + slot_drug.quantity
				else:
					for slot_drug in slot_drugs:
						stock_shelf_quantity = stock_shelf_quantity + slot_drug.quantity
		if stock_shelf_quantity > 0 :
			shelf_quantity_array.append(stock_shelf_quantity)
		stock_shelf_quantity = 0
	print(shelf_quantity_array, stock_shelf_array,'\n')
	stock_shelf_zip = zip(stock_shelf_array, shelf_quantity_array)
	
	context = {'stock_shelf_zip':stock_shelf_zip,'pk2':pk2,'drug':drug}
	return render(request,'pharmacy_app/drug_location_stock_shelf.html', context)

def DrugLocationStockSlot(request,pk,pk2):
#	print('stock pk :',pk,' drug pk:',pk2,'\n')
	
	slot_quantity_array = []
	stock_slot_array = []
	stock_quantity = 0
	stock_slot_quantity = 0
	drug = Dosage.objects.get(id=pk2)
	stock_slots = InStockSlot.objects.filter(shelf_no=pk)		
	for stock_slot in stock_slots:	
		slot_drugs = stock_slot.instockslotdrug_set.filter(drug_id=pk2)
		print('slot drugs:',slot_drugs)
		if slot_drugs:
			if stock_slot not in stock_slot_array:
				stock_slot_array.append(stock_slot)
				for slot_drug in slot_drugs:
					stock_slot_quantity = stock_slot_quantity + slot_drug.quantity
			else:
				for slot_drug in slot_drugs:
					stock_slot_quantity = stock_slot_quantity + slot_drug.quantity
		if stock_slot_quantity > 0 :
			slot_quantity_array.append(stock_slot_quantity)
		stock_slot_quantity = 0
	print("slot quantity array :",slot_quantity_array,'stock_slot_array: ', stock_slot_array,'\n')
	stock_slot_zip = zip(stock_slot_array, slot_quantity_array)
	context = {'stock_slot_zip':stock_slot_zip,'drug':drug}
	return render(request,'pharmacy_app/drug_location_stock_slot.html', context)

def DrugReport(request):
	all_drugs = Dosage.objects.all()
	slot_drugs = DispensarySlot.objects.all()
	drug_array= []
	quantity_recieved_array = []
	quantity_now_array=[]
	expired_drugs_quantity_array = []
	sold_drugs_quantity_array = []
	begin_balance_array=[]
	consumption_array=[]
	quantity_until_maximum_array = []
	maximum_array =[]

	for drug in all_drugs:
		drug_array.append(drug)

		drug_on_slot = DispensaryDrug.objects.filter(drug=drug)
		quantity_now_dict = drug_on_slot.aggregate(Sum('quantity'))
		quantity_now = quantity_now_dict['quantity__sum']
		quantity_now_array.append(quantity_now)


		supplied_this_month= DrugSupply.objects.filter(registered_on__year='2022', registered_on__month='1').filter(drug=drug)
		supplied_this_month_quantity = supplied_this_month.aggregate(Sum('supplied_quantity'))
		quantity_recieved = supplied_this_month_quantity['supplied_quantity__sum']
		if quantity_recieved is None:
			quantity_recieved = 0
		quantity_recieved_array.append(quantity_recieved)

#		expired_drugs = ExpiredDrug.objects.filter(date_expired__year='2021', date_expired__month='11').filter(drug__id__in=drug_on_slot) 
		expired_drugs = ExpiredDrug.objects.all()
		expired_drugs_quantity_dict = expired_drugs.aggregate(Sum('expired_quantity'))
		expired_drugs_quantity = expired_drugs_quantity_dict['expired_quantity__sum']
		expired_drugs_quantity_array.append(expired_drugs_quantity)

		sold_drugs = BillDetail.objects.filter(drug=drug)
		sold_drugs_quantity_dict = sold_drugs.aggregate(Sum('quantity'))
		sold_drugs_quantity = sold_drugs_quantity_dict['quantity__sum']
		sold_drugs_quantity_array.append(sold_drugs_quantity)

		print('Drug: ', drug, '\n','expired_quantity :', expired_drugs_quantity)	
		print('quantity_now equals', quantity_now, '\n', 'quantity_recieved', quantity_recieved, 'expired_drugs_quantity', expired_drugs_quantity )	
		begin_balance = quantity_now - quantity_recieved  + expired_drugs_quantity + sold_drugs_quantity
		
		begin_balance_array.append(begin_balance)
#		print(begin_balance_array)

		report_zip = zip(drug_array, begin_balance_array, quantity_recieved_array , expired_drugs_quantity_array, 
						sold_drugs_quantity_array,quantity_now_array )

		consumption = begin_balance +  quantity_recieved - expired_drugs_quantity - quantity_now 
		consumption_array.append(consumption)

		maximum = 2 * consumption
		maximum_array.append(maximum)

		quantity_until_maximum = maximum - quantity_now
		quantity_until_maximum_array.append(quantity_until_maximum)

		if quantity_until_maximum <0:
			quantity_until_maximum_str = "More than maximum"
		else:
			quantity_until_maximum_str = ""

		print('Drug', drug, " \n", 'Begin Balance :', begin_balance,'\n', "End Balance : ", quantity_now, '\n', 'Quantity Recieved : ', quantity_recieved, '\n', 'Quantity Expired : ',expired_drugs_quantity,'\n')
		context = {'report_zip' : report_zip ,'consumption':consumption_array, 'qum':quantity_until_maximum_array,'maximum':maximum_array}
	return render(request,'pharmacy_app/drug_report.html', context)


def SupplyFormPage(request, pk):

	supply_form = SupplyForm( )
	batch_form = BatchForm()
	procurement_form = ProcurementForm()
	drug_expiration_form = ExpirationDateForm()
	if request.method == 'POST':		
		batch_form = BatchForm(request.POST)	
		if batch_form.is_valid():
			batch_model = batch_form.save()
		else:
			print('batch form error:', batch_form.errors)

		drug_expiration_form = ExpirationDateForm(request.POST)
		if drug_expiration_form.is_valid():	
			drug_expiration_model = drug_expiration_form.save(commit=False)
			drug_expiration_model.drug = batch_model.drug
			drug_expiration_model.quantity = batch_model.quantity
			drug_expiration_model.save()
			
		else:
			print('expiration errors are:', drug_expiration_form.errors)

		supply_form = SupplyForm(request.POST)
		if supply_form.is_valid():					
			drug_supply_model = supply_form.save()
			drug_supply_model.drug = batch_model.drug
			drug_supply_model.batch = batch_model
			drug_supply_model.expiration_date = drug_expiration_model
			drug_supply_model.supplied_quantity = batch_model.quantity
			drug_supply_model.registered_on = datetime.now()
			drug_supply_model.registered_by = request.user
			drug_supply_model.save()			
		else:
			print('supply form error:', supply_form.errors)
	

	context = { 'batch_form':batch_form,'drug_expiration_form':drug_expiration_form,'supply_form':supply_form}
	return render(request, 'pharmacy_app/supply_form.html', context)

def StockSupplyFormPage(request,procurement_pk):
	procurement = Procurement.objects.get(procurement_no=procurement_pk)
	procurement_details = ProcurementDetail.objects.filter(procurement_no=procurement)

	slot_form = StockSlotForm()

	#Remaining and Supplied drugn info
	remaining_quantity = 0
	supplied_quantity_array = []
	remaining_quantity_array = []
	supplied_quantity = 0
	total_remaining_quantity = 0
	procurement_zip = None
	for procurement_detail in procurement_details:
		#below code retrieves supplied drugs for a particular request(procurement)

		drug_supply = DrugSupply.objects.filter(batch__procurement=procurement, drug=procurement_detail.drug)
		
		#then for each supplied drug get how much was supplied (quantity)
		for drug_supply in drug_supply:
			supplied_quantity = supplied_quantity + drug_supply.supplied_quantity
		supplied_quantity_array.append(supplied_quantity)	 
		#remaining quantity holds how much of the requested amount of drug hasnot been supplied
		remaining_quantity = procurement_detail.quantity - supplied_quantity
		remaining_quantity_array.append(remaining_quantity)

		procurement_zip = zip(procurement_details, supplied_quantity_array, remaining_quantity_array)
		#print(supplied_quantity_array, remaining_quantity_array)
		supplied_quantity = 0		
		total_remaining_quantity = total_remaining_quantity + remaining_quantity

#	create_random_record(schedule=5, repeat=5)
	stock_supply_form = StockSupplyForm()
	batch_form = BatchForm(initial={'procurement':procurement})

	procurement_drug_id = []
	procurement_details = ProcurementDetail.objects.filter(procurement_no=procurement)
	for pd in procurement_details:
		procurement_drug_id.append(pd.drug.id)
	procurement_drugs = Dosage.objects.filter(id__in=procurement_drug_id)
	#filter 'batch_form' field 'procurement' to only include procurements that are pending
#	batch_form.fields["procurement"].queryset = Procurement.objects.filter(status='pending')
	batch_form.fields["drug"].queryset = procurement_drugs
	p = Procurement.objects.all()
	for p in p:
		print(p,p.status)
	drug_expiration_form = ExpirationDateForm()
	if request.method == 'POST':		
		batch_form = BatchForm(request.POST)	
		if batch_form.is_valid():
			batch_model = batch_form.save(commit=False)
			batch_model.procurement = procurement
			batch_model.save()
		else:
			messages.error(request,'Enter Form Correctly!')
			print('batch form error:', batch_form.errors)

		drug_expiration_form = ExpirationDateForm(request.POST)
		if drug_expiration_form.is_valid():	
			drug_expiration_model = drug_expiration_form.save(commit=False)
			drug_expiration_model.drug = batch_model.drug
			drug_expiration_model.quantity = batch_model.quantity
			drug_expiration_model.save()
			
		else:
			messages.error(request,'Enter Form Correctly!')			
			print('expiration errors are:', drug_expiration_form.errors)

		stock_supply_form = StockSupplyForm(request.POST)
		if stock_supply_form.is_valid():					
			drug_supply_model = stock_supply_form.save(commit=False)
			drug_supply_model.drug = batch_model.drug
			drug_supply_model.batch = batch_model
			drug_supply_model.expiration_date = drug_expiration_model
			drug_supply_model.supplied_quantity = batch_model.quantity
			drug_supply_model.registered_on = datetime.now()
			drug_supply_model.registered_by = request.user
			drug_supply_model.save()
			messages.success(request, str(batch_model.quantity) + " " + str(drug_supply_model.drug) + ' supplied to ' + str(drug_supply_model.stock_slot_no) + ' successfully!')
			return redirect('stock_supply_form', procurement_pk)
		else:
			messages.error(request,'Enter Form Correctly!')
			print('supply form error:', stock_supply_form.errors)
	context = {'batch_form':batch_form,
				'drug_expiration_form':drug_expiration_form,
				'stock_supply_form':stock_supply_form,
				'procurement_zip':procurement_zip, 
				'slot_form':slot_form
				}
	return render(request, 'pharmacy_app/stock_supply_form.html',context)

def NoProcurementSupplyPage(request):

	#Remaining and Supplied drugn info

#	create_random_record(schedule=5, repeat=5)
	supply_form = StockSupplyForm()
	slot_form = StockSlotForm()
	batch_form = NoProcurementBatchForm()
	drug_expiration_form = ExpirationDateForm()

	if request.method == 'POST':		
		batch_form = BatchForm(request.POST)	
		if batch_form.is_valid():
			batch_model = batch_form.save(commit=False)
			batch_model.save()
		else:
			messages.error(request,'Enter Form Correctly!')
			print('batch form error:', batch_form.errors)

		drug_expiration_form = ExpirationDateForm(request.POST)
		if drug_expiration_form.is_valid():	
			drug_expiration_model = drug_expiration_form.save(commit=False)
			drug_expiration_model.drug = batch_model.drug
			drug_expiration_model.quantity = batch_model.quantity
			drug_expiration_model.save()
			
		else:
			messages.error(request,'Enter Form Correctly!')			
			print('expiration errors are:', drug_expiration_form.errors)

		stock_supply_form = StockSupplyForm(request.POST)
		if stock_supply_form.is_valid():					
			drug_supply_model = stock_supply_form.save(commit=False)
			drug_supply_model.drug = batch_model.drug
			drug_supply_model.batch = batch_model
			drug_supply_model.expiration_date = drug_expiration_model
			drug_supply_model.supplied_quantity = batch_model.quantity
			drug_supply_model.registered_on = datetime.now()
			drug_supply_model.registered_by = request.user
			drug_supply_model.save()
			messages.success(request, str(batch_model.quantity) + " " + str(drug_supply_model.drug) + ' supplied to ' + str(drug_supply_model.stock_slot_no) + ' successfully!')
			#return redirect('procurement_detail', procurement_pk)
		else:
			messages.error(request,'Enter Form Correctly!')
			print('supply form error:', stock_supply_form.errors)
	context = {'batch_form':batch_form,
				'drug_expiration_form':drug_expiration_form,
				'stock_supply_form':supply_form,
				'slot_form':slot_form,
				}
	return render(request, 'pharmacy_app/no_procurement_supply_form.html',context)

def DrugRelatedInfo(request):
	disease_form = DiseaseForm()
	contraindication_objects = ContraIndication.objects.all()
	contraindication_form = ContraIndicationForm()
	if request.method == 'POST':
		contraindication_form = ContraIndicationForm(request.POST)
		contraindication_form.save()

	context = {'disease_form': disease_form, 'contraindication_form': contraindication_form, 'contraindication_objects':contraindication_objects}
	return render(request, 'pharmacy_app/drug_related_info.html', context)

def Disease(request):
	disease_form = DiseaseForm()
	diseases = PathologicalFindings.objects.all()
	if request.method == 'POST':
		disease_form = DiseaseForm(request.POST)
		disease_form.save()

	context = {'disease_form':disease_form, 'diseases':diseases}
	return render(request, 'pharmacy_app/pathological_finding.html', context)

def  DrugInteractionPage(request):
	drug_interaction_form = DrugInteractionForm()
	drug_interaction_list = DrugInteraction.objects.all()
#	print(" List is :", drug_interaction_list)
	
#	milk = DrugCorelation.objects.get(food='Milk')
#	for m in milk.drug.all():
#		print(m)
	drugs = []
	drug_int_temp_first = None
	drug_int_temp_second = None
	count = 0
	"""
	for drug_interaction in drug_interaction_list:
#		drugs.append(drug_interaction.drug)
	
		for m in drug_interaction.drug.all():
			if (count == 0):
				drug_int_temp_first = m
				count = 1
			drug_int_temp_second = m
#			print(m, drug_interaction.id)
#		print('\n', 'first :', drug_int_temp_first, 'second :', drug_int_temp_second)
		count = 0
	print('\n','drugs are',)
	"""
	if request.method == 'POST':
		drug_interaction_form = DrugInteractionForm(request.POST)
		drug_interaction_form.save()

	context = {'drug_interaction_form':drug_interaction_form, 'drug_interaction_list':drug_interaction_list}

	return render(request, 'pharmacy_app/drug_interaction.html', context)

def AlcoholInteraction(request):
	alcohol_interaction_form = AlcoholInteractionForm()
	alcohol_interaction_lists = DrugCorelation.objects.filter(alcohol__isnull=False)
	for i in alcohol_interaction_lists:
		print('alcohol :', i.alcohol)
	if request.method == 'POST':
		alcohol_interaction_form = AlcoholInteractionForm(request.POST)
		alcohol_interaction_form.save()

	context = {'alcohol_interaction_form':alcohol_interaction_form, 'alcohol_interaction_lists':alcohol_interaction_lists}
	return render(request, 'pharmacy_app/alcohol_interaction.html', context)

def FoodInteraction(request):
	food_interaction_form = FoodInteractionForm()
	food_interaction_lists = DrugCorelation.objects.filter(food__isnull=False)
	for i in food_interaction_lists:
		print('food :', i.food)
	if request.method == 'POST':
		food_interaction_form = FoodInteractionForm(request.POST)
		food_interaction_form.save()

	context = {'food_interaction_form':food_interaction_form, 'food_interaction_lists':food_interaction_lists}
	return render(request, 'pharmacy_app/food_interaction.html', context)

def DiseaseInteraction(request):
    disease_interaction_form = DiseaseInteractionForm()
    disease_interaction_lists = DrugCorelation.objects.filter(pathological_findings__isnull=False)
    print(disease_interaction_lists)
#   for i in disease_interaction_lists:
#        print('disease :', i.disease)
    if request.method == 'POST':
        disease_interaction_form = DiseaseInteractionForm(request.POST)
        disease_interaction_form.save()

    context = {'disease_interaction_form':disease_interaction_form, 'disease_interaction_lists':disease_interaction_lists}
    return render(request, 'pharmacy_app/disease_interaction.html', context)

def SideEffectPage(request):
    side_effect_form = SideEffectForm()
    side_effect_lists = SideEffect.objects.all()
    print(side_effect_lists)
#   for i in side_effect_lists:
#        print('side_effect :', i.side_effect)
    if request.method == 'POST':
        side_effect_form = SideEffectForm(request.POST)
        side_effect_form.save()

    context = {'side_effect_form':side_effect_form, 'side_effect_lists':side_effect_lists}
    return render(request, 'pharmacy_app/side_effect.html', context)

def AgeRangePage(request):
    age_range_form = AgeRangeForm()
    age_range_lists = AgeRange.objects.all()
    print(age_range_lists)
#   for i in age_range_lists:
#        print('age_range :', i.age_range)
    if request.method == 'POST':
        age_range_form = AgeRangeForm(request.POST)
        age_range_form.save()

    context = {'age_range_form':age_range_form, 'age_range_lists':age_range_lists}
    return render(request, 'pharmacy_app/age_range.html', context)

def WeightRangePage(request):
    weight_range_form = WeightRangeForm()
    weight_range_lists = WeightRange.objects.all()
    print(weight_range_lists)
    if request.method == 'POST':
        weight_range_form = WeightRangeForm(request.POST)
        weight_range_form.save()

    context = {'weight_range_form':weight_range_form, 'weight_range_lists':weight_range_lists}
    return render(request, 'pharmacy_app/weight_range.html', context)

def IntakeModePage(request):
	intake_mode_form = IntakeModeForm()
	intake_mode_lists = IntakeMode.objects.all()
	print(intake_mode_lists)
#   for i in intake_mode_lists:
#        print('intake_mode :', i.intake_mode)
	if request.method == 'POST':
		intake_mode_form = IntakeModeForm(request.POST)
		if intake_mode_form.is_valid():
			print('yah')
			intake_mode_form.save()
		else:
			print('intake_mode_form error is:', intake_mode_form.errors, '\n')
	context = {'intake_mode_form':intake_mode_form, 'intake_mode_lists':intake_mode_lists}
	return render(request, 'pharmacy_app/intake_mode.html', context)

def PrescriptionFormPage(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	prescription_form = PrescriptionForm()
	info_form = PrescriptionInfoForm()

	print(request.user)
	if request.method == 'POST':
		prescription_form = PrescriptionForm(request.POST)
		if prescription_form.is_valid():			
			drug_prescription_model = prescription_form.save(commit=False)
			drug_prescription_model.patient = patient #Assign user(doctor) to prescriber field in DrugPrescription model
			#drug_prescription_model.prescriber = request.user #Assign user(doctor) to prescriber field in DrugPrescription model
			drug_prescription_model.registered_on = datetime.now()
			#drug_prescription_model.inpatient = 'false'
			medication_history = OutpatientMedication()
			medication_history.patient = patient
			medication_history.visit = PatientVisit.objects.filter(patient = patient).exclude(visit_status='Ended').last()
			medication_history.drug_prescription = drug_prescription_model 
			#medication_history.doctor = 
			medication_history.registered_on = datetime.now()
			
			drug_prescription_model.save()
			medication_history.save()
			messages.success(request,'Successfully Prescribed!')
			return redirect('outpatient_medical_note', patient.id)
		else:
			print('error: ', prescription_form.errors)
			messages.error(request,str(prescription_form.errors))

	context = {'prescription_form':prescription_form,
				'info_form':info_form,
				'patient':patient,
	}
	return render(request,'pharmacy_app/patient_prescription2.html', context)
	
def SavePrescription(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	if request.method == 'POST':
		info_form = PrescriptionInfoForm(request.POST)
		prescription_form = PrescriptionForm(request.POST)
		if info_form.is_valid():
			if prescription_form.is_valid():			
				info_model = info_form.save(commit=False)
				drug_prescription_model = prescription_form.save(commit=False)

				drug_prescription_model.patient = patient #Assign user(doctor) to prescriber field in DrugPrescription model
				drug_prescription_model.prescriber = Employee.objects.get(user_profile=request.user, designation__name='Doctor') #Assign user(doctor) to prescriber field in DrugPrescription model
				drug_prescription_model.registered_on = datetime.now()
				drug_prescription_model.info = info_model

				medication_history = OutpatientMedication()
				medication_history.patient = patient
				medication_history.visit = PatientVisit.objects.filter(patient = patient).exclude(visit_status='Ended').last()
				medication_history.drug_prescription = drug_prescription_model 
				#medication_history.doctor = 
				medication_history.registered_on = datetime.now()
				
				info_form.save()
				drug_prescription_model.save()
				medication_history.save()
				messages.success(request,'Successfully Prescribed2!')
				return redirect('outpatient_medical_note', patient.id)
			else:
				print('error: ', prescription_form.errors)
				messages.error(request,str(prescription_form.errors))
				return redirect('prescription_form', patient.id)
		else:
			print('error: ', info_form.errors)
			messages.error(request,str(info_form.errors))
			return redirect('prescription_form', patient.id)


	
def PrescriptionList(request):
	prescription_list = DrugPrescription.objects.filter(dispensed='false' )
#	prescription_list = DrugPrescription.objects.all()
	last_bill = Bill.objects.last()

	print(' last bill is:', last_bill,'\n')
	context = {'prescription_list':prescription_list, 'last_bill':last_bill}
	return render(request, 'pharmacy_app/prescription_list.html', context)

def InventoryStructure(request):
	"""
	this allows users to create stocks by entering how much 
	shelf it has and how much slot each shelf has
	"""
	inventory_structure_form = InventoryStructureForm()
	if request.method == 'POST':
		inventory_structure_form = InventoryStructureForm(request.POST)
		if inventory_structure_form.is_valid():
			print(inventory_structure_form.data['stock'])
			stock_name = inventory_structure_form.data['stock']
			shelf_amount =int( inventory_structure_form.data['shelf_amount'])
			slot_amount = int(inventory_structure_form.data['slot_amount'])
			in_stock_model = InStock()
			in_stock_model.stock_name = stock_name
			in_stock_model.save()				
			# below code generates amount of shelf as stated in form
			for i in range(1,shelf_amount + 1):
				in_stock_shelf_model = InStockShelf()
				in_stock_shelf_model.shelf_no = i
				in_stock_shelf_model.stock_name = in_stock_model
				in_stock_shelf_model.save()
				# below code generates amount of slot for each shelf as stated in form
				for j in range(1, slot_amount + 1):
					in_stock_slot_model = InStockSlot()
					in_stock_slot_model.slot_no = j
					in_stock_slot_model.shelf_no = in_stock_shelf_model
					in_stock_slot_model.save()
	context = {'inventory_structure_form': inventory_structure_form}
	return render(request,'pharmacy_app/inventory_structure.html',context)

def DispensaryStructure(request):
	dispensary_structure_form = DispensaryStructureForm()
	dispensary_stock_form = DispensaryStockForm()

	if request.method == 'POST':
		dispensary_structure_form = DispensaryStructureForm(request.POST)
		dispensary_stock_form = DispensaryStockForm(request.POST)

		if dispensary_structure_form.is_valid():
			dispensary_stock = dispensary_stock_form.save(commit=False)
			print(dispensary_structure_form.data['dispensary'])
			dispensary_name = dispensary_structure_form.data['dispensary']
			shelf_amount =int( dispensary_structure_form.data['shelf_amount'])
			slot_amount = int(dispensary_structure_form.data['slot_amount'])
			dispensary_model = Dispensary()
			dispensary_model.dispensary_name = dispensary_name
			dispensary_model.stock = dispensary_stock.stock
			dispensary_model.save()				
			for i in range(1,shelf_amount + 1):
				dispensary_shelf_model = DispensaryShelf()
				dispensary_shelf_model.shelf_no = i
				dispensary_shelf_model.dispensary = dispensary_model
				dispensary_shelf_model.save()
				for j in range(1, slot_amount + 1):
					dispensary_slot_model = DispensarySlot()
					dispensary_slot_model.slot_no = j
					dispensary_slot_model.shelf_no = dispensary_shelf_model
					dispensary_slot_model.save()
			messages.success(request,'Successful!')
	context = {'dispensary_structure_form':dispensary_structure_form,
				'dispensary_stock_form':dispensary_stock_form
	}
	return render(request,'pharmacy_app/dispensary_structure.html', context)

def DispensaryList(request):
	dispensary_list = Dispensary.objects.all()
	assigned_pharmacists = DispensaryPharmacist.objects.filter(active=True)
	all_pharmacists = Employee.objects.filter(designation__name='Pharmacy')
	unassigned_pharmacists = []
	for a in all_pharmacists:
		if DispensaryPharmacist.objects.filter(active=True, pharmacist__id =a.id).exists():
			print('Do Nothing')
		else:
			unassigned_pharmacists.append(a.id)
	assign_form = AssignPharmacistForm()
	assign_form.fields["pharmacist"].queryset = Employee.objects.filter(id__in=unassigned_pharmacists) 
	context = {'dispensary_list':dispensary_list,
				'assign_form':assign_form
	}
	return render(request,'pharmacy_app/dispensary_list.html', context)

def DispensaryShelfList(request, pk):
	dispensary_shelf_list = DispensaryShelf.objects.filter(dispensary_id=pk)
	print(dispensary_shelf_list)
	context = {'dispensary_shelf_list':dispensary_shelf_list,'dispensary_pk':pk}
	return render(request,'pharmacy_app/dispensary_shelf_list.html', context)

def EditDispensaryShelf(request, pk,dispensary_pk):
	dispensary_shelf = DispensaryShelf.objects.get(id=pk)
	print("gggg",dispensary_shelf.shelf_no)
	edit_dispensary_shelf_form = EditDispensaryShelfForm(initial={'shelf_no':dispensary_shelf.shelf_no})
	if request.method == 'POST':
		edit_dispensary_shelf_form = EditDispensaryShelfForm(request.POST, initial={'shelf_no':dispensary_shelf.shelf_no})
		if edit_dispensary_shelf_form.is_valid():
			dispensary_shelf.shelf_no = edit_dispensary_shelf_form.data['shelf_no']
			dispensary_shelf.save()
			return redirect('dispensary_shelf_list', dispensary_pk)
	context = {'edit_dispensary_shelf_form':edit_dispensary_shelf_form }
	return render(request,'pharmacy_app/edit_dispensary_shelf.html', context)

def EditStockShelf(request, pk,stock_pk):
	stock_shelf = InStockShelf.objects.get(id=pk)
	print("gggg",stock_shelf.shelf_no)
	edit_stock_shelf_form = EditStockShelfForm(initial={'shelf_no':stock_shelf.shelf_no})
	if request.method == 'POST':
		edit_stock_shelf_form = EditStockShelfForm(request.POST, initial={'shelf_no':stock_shelf.shelf_no})
		if edit_stock_shelf_form.is_valid():
			stock_shelf.shelf_no = edit_stock_shelf_form.data['shelf_no']
			
			stock_shelf.save()
			#return redirect('dispensary_shelf_list', dispensary_pk)
	context = {'edit_stock_shelf_form':edit_stock_shelf_form }
	return render(request,'pharmacy_app/edit_stock_shelf.html', context)

def StockList(request):
	in_stock_list = InStock.objects.all()
	in_stock_shelf_list = []
	in_stock_slot_list = []
	in_stock_slot_drug_list = []
	slot_quantity = 0
	shelf_quantity = 0
	stock_quantity = 0
	stock_quantity_array = []
	for in_stock in in_stock_list:
		in_stock_shelf_list = InStockShelf.objects.filter(stock_name=in_stock)
		for in_stock_shelf in in_stock_shelf_list:
			in_stock_slot_list = InStockSlot.objects.filter(shelf_no=in_stock_shelf)

			for in_stock_slot in in_stock_slot_list:
				in_stock_slot_drug_list = InStockSlotDrug.objects.filter(slot_no=in_stock_slot)				
				slot_quantity_dict = in_stock_slot_drug_list.aggregate(Sum('quantity'))				
				if slot_quantity_dict['quantity__sum'] is None:
					slot_quantity_dict['quantity__sum'] = 0
				slot_quantity = slot_quantity + slot_quantity_dict['quantity__sum']
#				print('quantity :', slot_quantity_dict['quantity__sum'], slot_quantity,'\n')
			shelf_quantity = shelf_quantity + slot_quantity
#			print('quantity :', shelf_quantity,'\n')
			slot_quantity = 0
		stock_quantity = stock_quantity + shelf_quantity
		stock_quantity_array.append(stock_quantity)
		print('quantity ', stock_quantity, '\n')
		shelf_quantity = 0
		stock_quantity = 0
	stock_zip = zip(in_stock_list, stock_quantity_array)	
	context = {'stock_zip': stock_zip}
	return render(request, 'pharmacy_app/stock_list.html', context)	

def StockShelfList(request, pk):
	in_stock_list = InStock.objects.all()
	in_stock_shelf_list = InStockShelf.objects.filter(stock_name_id=pk)
		
	in_stock_slot_list = []
	in_stock_slot_drug_list = []
	slot_quantity = 0
	shelf_quantity = 0
	stock_quantity = 0
	shelf_quantity_array = []
	print(in_stock_shelf_list)
	for in_stock_shelf in in_stock_shelf_list:
		print('pppp')
		in_stock_slot_list = InStockSlot.objects.filter(shelf_no=in_stock_shelf)

		for in_stock_slot in in_stock_slot_list:
			in_stock_slot_drug_list = InStockSlotDrug.objects.filter(slot_no=in_stock_slot)				
			slot_quantity_dict = in_stock_slot_drug_list.aggregate(Sum('quantity'))				
			if slot_quantity_dict['quantity__sum'] is None:
				slot_quantity_dict['quantity__sum'] = 0
			slot_quantity = slot_quantity + slot_quantity_dict['quantity__sum']
#			print('quantity :', slot_quantity_dict['quantity__sum'], slot_quantity,'\n')
	#	if slot_quantity
		shelf_quantity = shelf_quantity + slot_quantity
		shelf_quantity_array.append(shelf_quantity)
		print('quantity :', shelf_quantity,'\n')
		slot_quantity = 0
		shelf_quantity = 0
	stock_zip = zip(in_stock_shelf_list, shelf_quantity_array)	
	context = {'stock_zip': stock_zip, 'stock_pk':pk}
	return render(request, 'pharmacy_app/stock_shelf_list.html', context)	


def StockSlotList(request, pk):
	in_stock_list = InStock.objects.all()
#	in_stock_shelf_list = InStockShelf.objects.filter(stock_no_id=pk)
	
	in_stock_slot_list = InStockSlot.objects.filter(shelf_no_id=pk)
	in_stock_slot_drug_list = []
	slot_quantity = 0
	shelf_quantity = 0
	stock_quantity = 0
	slot_quantity_array = []
#	print(in_stock_shelf_list)
	for in_stock_slot in in_stock_slot_list:
		in_stock_slot_drug_list = InStockSlotDrug.objects.filter(slot_no=in_stock_slot)				
		slot_quantity_dict = in_stock_slot_drug_list.aggregate(Sum('quantity'))				
		if slot_quantity_dict['quantity__sum'] is None:
			slot_quantity_dict['quantity__sum'] = 0
		slot_quantity = slot_quantity + slot_quantity_dict['quantity__sum']
		slot_quantity_array.append(slot_quantity)
		slot_quantity = 0
		print(in_stock_slot_drug_list)
#	print('quantity :', slot_quantity,'\n')
	
	stock_zip = zip(in_stock_slot_list, slot_quantity_array)	
	context = {'stock_zip': stock_zip}
	return render(request, 'pharmacy_app/stock_slot_list.html', context)	


def StockDrugList(request, pk):
	stock_drug_list = InStockSlotDrug.objects.filter(slot_no_id=pk)
	stock_drug_array = []
	stock_drug_quantity_array = []
	for stock_drug in stock_drug_list:
		stock_drug_array.append(stock_drug.drug)
		stock_drug_quantity_array.append(stock_drug.quantity)
		print('Drug: ', stock_drug.drug, ' Quantity: ', stock_drug.quantity,'pk:',pk)
	stock_drug_zip = zip(stock_drug_array, stock_drug_quantity_array)
	context = {'stock_drug_zip':stock_drug_zip,'pk':pk}
	return render(request, 'pharmacy_app/stock_drug_list.html', context)

def ProcurementPage(request):
	"""
	this view function allows user to create a procurement and drugs & quantities associated with that procurement
	"""
	status_array = []
	procurement_list = Procurement.objects.all()
	for procurement in procurement_list:
		if procurement.status == 'pending':
			status_array.append("pending")
		else: 
			status_array.append("")
	last_procurement = Procurement.objects.last()
	procurement_zip = zip(procurement_list, status_array)
	procurement_form = ProcurementForm(initial={'procurement_no':last_procurement.procurement_no + 1})
	procurement_dispensary_form = ProcurementDispensaryForm()	
	if request.method == 'POST':
		#procurement_form = ProcurementForm(request.POST)
		procurement_dispensary_form = ProcurementDispensaryForm(request.POST)
		if procurement_dispensary_form.is_valid():
			procurement_dispensary = procurement_dispensary_form.save(commit=False)

			procurement = Procurement()
			procurement.procurement_no = last_procurement.procurement_no + 1
			procurement.dispensary = procurement_dispensary.dispensary
			procurement.save()
			messages.success(request,'Successful!')
			return redirect('procurement')
		else:
			print('error :',procurement_form.errors)
	procurement_detail_form = ProcurementDetailForm()

	context = {'procurement_detail_form':procurement_detail_form,
				'procurement_zip':procurement_zip,
				'procurement_form':procurement_form,
				'procurement_dispensary_form':procurement_dispensary_form,
				}
	return render(request, 'pharmacy_app/procurement.html', context)

def StockManagerProcurementPage(request):
	"""
	this view function allows user to create a procurement and drugs & quantities associated with that procurement
	"""
	status_array = []
	procurement_list = Procurement.objects.all()
	for procurement in procurement_list:
		if procurement.status == 'pending':
			status_array.append("pending")
		else: 
			status_array.append("")
	last_procurement = Procurement.objects.last()
	procurement_zip = zip(procurement_list, status_array)
	procurement_form = ProcurementForm(initial={'procurement_no':last_procurement.procurement_no + 1})
	procurement_dispensary_form = ProcurementDispensaryForm()	
	procurement_detail_form = ProcurementDetailForm()

	context = {'procurement_detail_form':procurement_detail_form,
				'procurement_zip':procurement_zip,
				'procurement_form':procurement_form,
				'procurement_dispensary_form':procurement_dispensary_form,
				}
	return render(request, 'pharmacy_app/stock_manager_procurement.html', context)

def CreateProcurement(request):
	last_procurement = Procurement.objects.last()
	procurement = Procurement()
	procurement.procurement_no = last_procurement.procurement_no + 1
	#procurement.dispensary = procurement_dispensary.dispensary
	procurement.save()
	return redirect('procurement')
	
def SaveProcurementDetail(request, procurement_id):
	procurement = Procurement.objects.get(procurement_no=procurement_id)
	if request.method == 'POST':
		procurement_detail_form = ProcurementDetailForm(request.POST)
		if procurement_detail_form.is_valid():
			procurement_detail_model = procurement_detail_form.save(commit=False)
			procurement_detail_model.procurement_no = procurement
			procurement_detail_model.save()
			messages.success(request, 'Procurement Created!')
			return redirect('procurement')
		else:
			messages.error(request,str(procurement_detail_form.errors))
			return redirect('procurement')

def CancelProcurement(request, procurement_pk):
	procurement = Procurement.objects.get(procurement_no=procurement_pk)
	if request.method == 'POST':
		procurement.status = 'cancelled'
		procurement.save()
		return redirect('procurement')
	context = {'procurement_no':procurement_pk}	
	return render(request, 'pharmacy_app/cancel_procurement.html', context)
def ProcurementDetailPage(request,pk,row):

	if row==None:
		row=1
	request_form = ProcurementDetailForm()

	procurement = Procurement.objects.get(procurement_no=pk)

	procurement_details = ProcurementDetail.objects.filter(procurement_no=procurement)

	real_batch_array = []
	batch_list = Batch.objects.filter(procurement=procurement)
	batch_array = []
	quantity_array = []
	drug_array = []
	for batch in batch_list:
#		print(batch,'\n')
		if batch.batch_no in batch_array:
			print('')

		else:
			batch_array.append(batch.batch_no)
			real_batch_array.append(batch)
			"""
			for drug in batch_list.drug:
				drug_array.append(drug)
				batch_objects = Batch.objects.filter(procurement=procurement, batch_no=batch.batch_no, drug=drug)
				quantity = batch_objects.aggregate(Sum('quantity'))
				quantity_array.append(quantity)
				batch_zip = zip(drug_array, quantity_array)
	print('\n','drug_array','\n')
			"""
#	drug_supply = DrugSupply.objects.filter(batch__procurement=procurement)
	#print(procurement_details)
	remaining_quantity = 0
#	procurement_zip = zip(procurement_details, drug_supply)
	supplied_quantity_array = []
	remaining_quantity_array = []
	supplied_quantity = 0
	total_remaining_quantity = 0
	procurement_zip = None
	for procurement_detail in procurement_details:
		#below code retrieves supplied drugs for a particular request(procurement)

		drug_supply = DrugSupply.objects.filter(batch__procurement=procurement, drug=procurement_detail.drug)
		
		#then for each supplied drug get how much was supplied (quantity)
		for drug_supply in drug_supply:
			supplied_quantity = supplied_quantity + drug_supply.supplied_quantity
		supplied_quantity_array.append(supplied_quantity)	 
		#remaining quantity holds how much of the requested amount of drug hasnot been supplied
		remaining_quantity = procurement_detail.quantity - supplied_quantity
		remaining_quantity_array.append(remaining_quantity)

		procurement_zip = zip(procurement_details, supplied_quantity_array, remaining_quantity_array)
		#print(supplied_quantity_array, remaining_quantity_array)
		supplied_quantity = 0		
		total_remaining_quantity = total_remaining_quantity + remaining_quantity
#		print(total_remaining_quantity,'\n')
	if request.htmx:
		row=row
		request_form = ProcurementDetailForm()
		request_form2 = ProcurementDetailForm(request.POST) 
		if request_form2.is_valid():
			print('Hes Sir25465464')
			request_model = request_form2.save(commit=False)
			request_model.procurement_no = procurement
			request_model.save()
			print(request)
			print('yeyy yjkkjk')
		print('Has come!!!')
		request_form = ProcurementDetailForm()
		context = {'request_form':request_form, 'row':row, 'procurement_pk':pk}
		return render(request,'pharmacy_app/partials/procurement_drug_form.html', context)

	context = {'procurement_zip':procurement_zip, 'batch_array':real_batch_array, 'procurement_pk':pk
				, 'request_form':request_form, 'row':row
	}
	return render(request,'pharmacy_app/procurement_detail.html', context)

def ProcurementBatch(request, procurement_pk, batch_no):
	print('procurement_pk is', procurement_pk, '\n', 'batch_no is ', batch_no)

	batch_list = Batch.objects.filter(procurement__procurement_no = procurement_pk, batch_no=batch_no)
	print('ddd', batch_list)
	batch_drug_array = []
	batch_quantity_array = []
	for batch in batch_list:
		if batch.drug not in batch_drug_array:
			batch_drug_array.append(batch.drug)
	print('\n', batch_drug_array)
	for drug in batch_drug_array:
		batch_objects = Batch.objects.filter(procurement__procurement_no=procurement_pk, batch_no=batch_no, drug=drug)
		quantity = batch_objects.aggregate(Sum('quantity'))
		quantity = quantity['quantity__sum']
		batch_quantity_array.append(quantity)
		batch_zip = zip(batch_drug_array, batch_quantity_array)
		context = {'batch_zip':batch_zip, 'batch_no':batch_no}
	return render(request,'pharmacy_app/procurement_batch.html', context)

"""
def ProcurementDetail(request,pk):
	procurement_object = Procurement.objects.get(id=pk)
	procurement_detail_form = ProcurementDetailForm()
	if request.method == 'POST':
		procurement_detail_form = ProcurementDetailForm(request.POST)
		if procurement_detail_form.is_valid():
			procurement_detail_form.save()
		else:
			print('error')
	context = {'procurement_detail_form':procurement_detail_form, 'procurement_object':procurement_object}
	return render(request, 'pharmacy_app/procurement_detail_form.html', context)
"""

def DrugPriceFormPage(request):
	"""
	This function allows user to setup prices for drugs
	"""
	drug_price_form = DrugPriceForm()
	drug_price_list = DrugPrice.objects.all()
	drug_price_array = []
#	for drug_price in drug_price_list:
#		if drug_price.drug == 

	if request.method == 'POST':
		drug_price_form = DrugPriceForm(request.POST)
		if drug_price_form.is_valid():
			drug_price_model = drug_price_form.save(commit=False)
			try:
				same_drug = DrugPrice.objects.get(drug=drug_price_model.drug, active = 'active')
				same_drug.active = 'not_active'
				same_drug.save()
			except DrugPrice.DoesNotExist:
				print('l')
			drug_price_model.active = 'active'
			#'effective_date' field is nedded to show since when a paricular price was set for a drug
			drug_price_model.effective_date = datetime.now()
			drug_price_model.save()
		else:
			print('drug price form errors: ', drug_price_form.errors)
#	drug_price = DrugPrice.objects.get(drug=bill_detail_model.drug, active='active')

	context = {'drug_price_form':drug_price_form, 'drug_price_list':drug_price_list}
	return render(request, 'pharmacy_app/drug_price_form.html', context)



def ThresholdFormPage(request):
	inventory_threshold = InventoryThreshold.objects.all()
#	threshold_array = []
	threshold_id_array = []
	for threshold in inventory_threshold:
		threshold_id_array.append(threshold.id)
	#print(threshold_id_array)
	#low_stock_level_alert(threshold_id_array)

	threshold_form = ThresholdForm()
	if request.method == 'POST':
		threshold_form = ThresholdForm(request.POST)
		if threshold_form.is_valid():
			threshold_model = threshold_form.save(commit=False)
			print('yooo','\n')
			try:
	 			threshold_drug = InventoryThreshold.objects.get(drug=threshold_model.drug)
	 			threshold_drug.delete()
	 			threshold_model.save()
			except:
				threshold_model.save()

		else:
			print(threshold_form.errors)


	context = {'threshold_form':threshold_form, 'inventory_threshold':inventory_threshold}
	return render(request, 'pharmacy_app/threshold.html', context)


def LowStockDrugs(request):
	inventory_threshold = InventoryThreshold.objects.all()

	all_drugs = Dosage.objects.all()
	drug_array = []
	stock_quantity_array = []
	needed_amount_array = []

	for drug in all_drugs:
		drug_in_stock = InStockSlotDrug.objects.filter(drug=drug)
		drug_in_dispesary = DispensaryDrug.objects.filter(drug=drug)

		stock_quantity_dict = drug_in_stock.aggregate(Sum('quantity'))
		stock_quantity = stock_quantity_dict['quantity__sum']		
		if stock_quantity == None:
			stock_quantity = 0
		dispensary_dict = drug_in_dispesary.aggregate(Sum('quantity'))
		dispensary_quantity = dispensary_dict['quantity__sum']		
		if dispensary_quantity == None:
			dispensary_quantity = 0
		total_quantity = stock_quantity + dispensary_quantity
		threshold = InventoryThreshold.objects.get(drug = drug)
		if total_quantity < threshold.threshold:
			print(drug, 'stock quantity: ', stock_quantity,'\n')
			stock_quantity_array.append(total_quantity)
			needed_amount_array.append(threshold.threshold - total_quantity) 
			drug_array.append(drug)
			threshold_zip = zip(drug_array, stock_quantity_array, needed_amount_array)
			stock_quantity = 0		
			context = {'threshold_zip':threshold_zip}
			return render(request, 'pharmacy_app/low_stock_drugs.html',context)
		else:
			return render(request, 'pharmacy_app/low_stock_drugs.html')


def DrugProfilePage(request, pk):

	drugs = Dosage.objects.all()
	stock_quantity_array = []
	drug_names = []
	for drug in drugs:
		drug_names.append(drug.drug.drug.commercial_name)
		drug_in_stock = InStockSlotDrug.objects.filter(drug=drug)
		stock_quantity_dict = drug_in_stock.aggregate(Sum('quantity'))
		stock_quantity = stock_quantity_dict['quantity__sum']
		stock_quantity_array.append(stock_quantity)
	print(stock_quantity_array)

	
	drug = Dosage.objects.get(id=pk)
	drug_corelation = DrugCorelation.objects.filter(drug=drug)
	try:
		intake_mode = IntakeMode.objects.get(drug=drug)
	except:
		intake_mode = None
	try:
		image = DrugImage.objects.get(drug=drug, active='active')
		all_images = DrugImage.objects.filter(drug=drug)
		image_count = 0
		for i in all_images:
			image_count = image_count + 1
		context = {'image':image, 'drug':drug, 'image_count':image_count,
		'drug_corelation':drug_corelation, 'intake_mode':intake_mode}
			
	except:
		print("")
		context = { 'drug':drug,'drug_corelation':drug_corelation, 'intake_mode':intake_mode}
			
#	for d in drug_corelation:
#	print(d.drug, d.pathological_findings, d.food, d.alcohol, d.relation,'\n')

	return render(request, 'pharmacy_app/drug_profile.html', context)


def DrugImageFormPage(request,pk):
	images = DrugImage.objects.filter(drug_id=pk)
	image_form = DrugImageForm()
	if request.method == 'POST':
		image_form = DrugImageForm(request.POST)
#		image_file = request.FILES.get('file')
		images = request.FILES.getlist('images')
		print(image_form)
		if image_form.is_valid():
			image_model = image_form.save(commit=False)
			for image in images:
				print(image)
				image_object= DrugImage()
				image_object.drug = image_model.drug
				image_object.image = image
				drug_images = DrugImage.objects.filter(drug=image_object.drug)
				if not drug_images:
					image_object.active='active'
				image_object.save()
		else:
			print(image_form.errors)
		active_image_form = ActiveImageForm(request.POST)
		
		if active_image_form.is_valid():
			print('wors')
		else:
			print('no')
		
	context = {'image_form':image_form,'images':images}
	return render(request, 'pharmacy_app/drug_image_form.html', context)

def BillPage(request, pk):
	bill = Bill.objects.get(bill_no=pk)
	bill_details = BillDetail.objects.filter(bill=bill)
	bill_details_array = []
	total_price = 0
	pri_times_quantity = 1
	single_drug_charge = []
	patient = None
	time = None
	for b in bill_details:
#		if b.discount == 'Yes':
#			pri_times_quantity = b.quantity * b.selling_price.discounted_price 
		
		pri_times_quantity = b.quantity * b.selling_price.selling_price
		total_price =  total_price + pri_times_quantity
		print(b.selling_price.selling_price,'\n')
		patient = b.patient
		time = b.registered_on
		single_drug_charge.append(pri_times_quantity)
		bill_details_array.append(b)
		bill_zip = zip(bill_details, single_drug_charge)
	print(total_price)
	context = {'bill_zip': bill_zip,'bill_details':bill_details, 'bill':bill, 'total_price':total_price,
				'patient':patient, 'time':time, 'single_drug_charge':single_drug_charge, 'pk':pk}

	return render(request, 'pharmacy_app/bill_detail.html', context)


	"""
	all_drugs = Dosage.objects.all()
	stock_quantity_array = []
	drug_array = []
	drug_chart_zip = None
	for drug in all_drugs:
		drug_in_stock = InStockSlotDrug.objects.filter(drug=drug)
		stock_quantity_dict = drug_in_stock.aggregate(Sum('quantity'))
		stock_quantity = stock_quantity_dict['quantity__sum']
		stock_quantity_array.append(stock_quantity)
		drug_array.append(drug.drug.drug.commercial_name)
		drug_chart_zip = zip(drug_array, stock_quantity_array)
#		print('drug :', drug, 'Stock Quantity ', stock_quantity,'\n')
	"""
def PrintedInvoice(request,pk):
	bill = Bill.objects.get(bill_no=pk)
	bill_details = BillDetail.objects.filter(bill=bill)
	bill_details_array = []
	total_price = 0
	pri_times_quantity = 1
	single_drug_charge = []
	patient = None
	time = None
	for b in bill_details:
		pri_times_quantity = b.quantity * b.selling_price.selling_price 
		total_price =  total_price + pri_times_quantity
		print(b.selling_price.selling_price,'\n')
		patient = b.patient
		time = b.registered_on
		single_drug_charge.append(pri_times_quantity)
		bill_details_array.append(b)
		bill_zip = zip(bill_details, single_drug_charge)
	print(total_price)
	context = {'bill_zip': bill_zip, 'bill_details':bill_details, 'bill':bill, 'total_price':total_price,
				'patient':patient, 'time':time, 'single_drug_charge':single_drug_charge}

	return render(request, 'pharmacy_app/printed_invoice.html', context)



def NewBillForm(request, pk,pk2):
	last_bill_no = pk2
	new_pk = pk2 + 1
	bill = Bill()
	bill.bill_no = new_pk
	print('\n','new bill number: ', bill.bill_no, 'last bill number :', pk2,'\n')
	if ( bill.bill_no - pk2 == 1):
		bill.save()

	prescription = DrugPrescription.objects.get(id=pk) 
	dispension_form = DispensionForm()

	stock_slot_id_array = []	
	stock_slots = InStockSlot.objects.all()		
	for stock_slot in stock_slots:	
		slot_drug = stock_slot.instockslotdrug_set.filter(drug_id=prescription.drug.id).first()
		if slot_drug:
			stock_slot_id_array.append(stock_slot.id)			
	
	
	stock_slots = InStockSlot.objects.filter(id__in=stock_slot_id_array)
	dispension_form.fields["slot_no"].queryset = stock_slots
	bill_form = BillForm(initial={'bill':bill,'drug':prescription.drug})
	
#	small_bill_form = SmallBillForm()
	qs = BillDetail.objects.none()
	SmallBillFormset = modelformset_factory(BillDetail, form=SmallBillForm, extra=0)
	small_bill_formset = SmallBillFormset(request.POST or None, queryset=qs)
	
	if request.method == 'POST':
		bill_form = BillForm(request.POST, initial={'bill':bill, 'drugs':prescription.drug})
		if bill_form.is_valid():
			small_bill_formset = SmallBillFormset(request.POST)
			if small_bill_formset.is_valid():
				bill_detail_model = bill_form.save(commit=False)
				drug_price = DrugPrice.objects.get(drug=bill_detail_model.drug, active='active')
				bill_detail_model.selling_price = drug_price
				bill_detail_model.patient = prescription.patient
				bill_detail_model.registered_on = datetime.now()
				for form in small_bill_formset:
					small_bill_detail_model = form.save(commit=False)
					small_bill_detail_model.bill = bill 
					small_bill_detail_model.selling_price = drug_price
					small_bill_detail_model.patient = prescription.patient
					small_bill_detail_model.registered_on = datetime.now()
					small_bill_detail_model.save()
				bill_detail_model.save() 
		else:
			print('bill form errors: ', bill_form.errors, '\n', 'small bill formset errors: ', small_bill_formset.errors)
	context = {'bill_form':bill_form, 'small_bill_formset':small_bill_formset}
	return  render(request, 'pharmacy_app/new_bill_form.html', context)

def DrugChart(request):
	all_drugs = Dosage.objects.all()
	stock_quantity_array = []
	drug_array = []
	drug_chart_zip = None

	slot_quantity_array = []
	stock_slot_array = []
	stock_quantity = 0
	stock_slot_quantity = 0


	for drug in all_drugs:
		drug_in_stock = InStockSlotDrug.objects.filter(drug=drug)
		stock_quantity_dict = drug_in_stock.aggregate(Sum('quantity'))
		stock_quantity = stock_quantity_dict['quantity__sum']
		stock_quantity_array.append(stock_quantity)
		drug_array.append(drug.drug.drug.commercial_name)
		drug_chart_zip = zip(drug_array, stock_quantity_array)
#		print('drug :', drug, 'Stock Quantity ', stock_quantity,'\n')
		stock_slots = InStockSlot.objects.all()		
		for stock_slot in stock_slots:	
			slot_drugs = stock_slot.instockslotdrug_set.filter(drug=drug)
#			print('slot drugs:',slot_drugs)
			if slot_drugs:
				if stock_slot not in stock_slot_array:
					stock_slot_array.append(stock_slot)
					for slot_drug in slot_drugs:
						stock_slot_quantity = stock_slot_quantity + slot_drug.quantity
						print('Drug : ',slot_drug, 'Quantity :',stock_slot_quantity, ' Found in',stock_slot,'\n')
				else:
					for slot_drug in slot_drugs:
						stock_slot_quantity = stock_slot_quantity + slot_drug.quantity
						print('Drug : ',slot_drug, 'Quantity :',stock_slot_quantity, ' Found in',stock_slot,'\n')
			if stock_slot_quantity > 0 :
				slot_quantity_array.append(stock_slot_quantity)
			stock_slot_quantity = 0


		context = {'drug_chart_zip':drug_chart_zip, 'drug_array':drug_array, 'stock_quantity_array':stock_quantity_array}
	return render(request, 'pharmacy_app/drug_chart.html', context)


def get_data(request,*args, **kwargs):
	data = {'jack': 12, 'john':10 }
	return JsonResponse(data)

def chart(request):
	return render(request, 'pharmacy_app/chart.html')

class ChartData(APIView):
	authentication_classes = []
	permission_classes = []

	def get(self, request, format=None, *args, **kwargs):
		
		drugs = Dosage.objects.all()
		"""
		for drug in drugs:
			drug_name = drugs.drug.drug.commercial_name
		"""
		stock_quantity_array =[]
		shelf_quantity_array = []
		total_quantity_array = []
		drug_names = []
		drug_names_array = []
		for drug in drugs:
			drug_names.append(drug.drug.drug.commercial_name)
			drug_in_stock = InStockSlotDrug.objects.filter(drug=drug)
			for drugl in drug_in_stock:
				drug_names_array.append(str(drugl.drug))
			try:
				stock_quantity_dict = drug_in_stock.aggregate(Sum('quantity'))
				stock_quantity = stock_quantity_dict['quantity__sum']
				stock_quantity_array.append(stock_quantity)

				drug_on_slot = DispensaryDrug.objects.filter(drug=drug)
				shelf_quantity_dict = drug_on_slot.aggregate(Sum('quantity'))
				shelf_quantity = shelf_quantity_dict['quantity__sum']
				shelf_quantity_array.append(shelf_quantity)

				total_quantity = shelf_quantity + stock_quantity
				print(total_quantity)
				total_quantity_array.append(total_quantity)
			except:
				total_quantity_array.append(0)
				

		labels = ['one','two','three']
		number = [10]
		data = {'labels':drug_names_array,
				'numbers':total_quantity_array }
		return Response(data)

def ShelfChart(request):
	return render(request, 'pharmacy_app/shelf_chart.html')

class ShelfChartData(APIView):
	authentication_classes = []
	permission_classes = []
#	renderer_classes = [TemplateHTMLRenderer]
#	template_name = 'pharmacy_app/shelf_chart.html'
	def get(self, request, format=None, *args, **kwargs):

		pk = kwargs.get('pk','Default Value if not there')
		print('ppppkkkkkk',pk)
		in_stock_list = InStock.objects.all()
		in_stock_shelf_list = InStockShelf.objects.filter(stock_name_id=2)
		
		drugs = Dosage.objects.all()
		drug_names = []	
		in_stock_slot_list = []
		in_stock_slot_drug_list = []
		slot_quantity = 0
		shelf_quantity = 0
		stock_quantity = 0
		shelf_quantity_array = []
		print(in_stock_shelf_list)
		for in_stock_shelf in in_stock_shelf_list:
			print('pppp')
			in_stock_slot_list = InStockSlot.objects.filter(shelf_no=in_stock_shelf)

			for in_stock_slot in in_stock_slot_list:
				in_stock_slot_drug_list = InStockSlotDrug.objects.filter(slot_no=in_stock_slot)				
				for slot_drug  in in_stock_slot_drug_list:
					drug_names.append(slot_drug.drug.drug.drug.commercial_name) 
				slot_quantity_dict = in_stock_slot_drug_list.aggregate(Sum('quantity'))				
				if slot_quantity_dict['quantity__sum'] is None:
					slot_quantity_dict['quantity__sum'] = 0
				slot_quantity = slot_quantity + slot_quantity_dict['quantity__sum']
			shelf_quantity = shelf_quantity + slot_quantity
			shelf_quantity_array.append(shelf_quantity)
			print('quantity :', shelf_quantity,'\n')
			slot_quantity = 0
			shelf_quantity = 0
		data = {'labels':drug_names,
			'numbers':shelf_quantity_array }
		
		return Response(data)
def ChartTrial(request):
	credit_bills = DrugDispensed.objects.filter(payment_type='credit')
	print(credit_bills)
	for credit in credit_bills:
		print('\n', credit.bill_no,'\n')

	return render(request,'pharmacy_app/chart_trial.html')

def DrugSaleReport(request):

	return render(request,'pharmacy_app/drug_sale_chart.html')

def DrugSaleDetail(request, month_no):
#	bills = BillDetail.objects.filter(registered_on__month=month_no)
	quantity_sold = []
	drug_array = []
	all_drugs = Dosage.objects.all()
	for drug in all_drugs:
		drug_array.append(str(drug))		
		dt = datetime.date(datetime.now())
		bills = BillDetail.objects.filter( registered_on__month=month_no, drug=drug)
		print(dt.day)
		quantity_sold_dict = bills.aggregate(Sum('quantity'))
		if quantity_sold_dict['quantity__sum']:
			quantity_sold.append(quantity_sold_dict['quantity__sum'])
		else:	
			quantity_sold_dict = 0
			quantity_sold.append(quantity_sold_dict)
#			print('drug : ', drug, 'sold quantity : ', quantity_sold_dict,'\n')
		bill_zip = zip(drug_array,quantity_sold)
	context = {'bill_zip':bill_zip}
	return render(request,'pharmacy_app/drug_sale_detail.html',context)

class DrugSaleData(APIView):
	authentication_classes = []
	permission_classes = []

	def get(self, request, format=None, *args, **kwargs):
		quantity_sold = []
		months = ['January','February','March','April','May','June','July','August','September','October','November','December']
		for i in range(1,13):
			sold_drugs = BillDetail.objects.filter(registered_on__month=i)
			quantity_sold_dict = sold_drugs.aggregate(Sum('quantity'))
			if quantity_sold_dict['quantity__sum']:
				quantity_sold.append(quantity_sold_dict['quantity__sum'])
			else:			
				quantity_sold_dict = 0
				quantity_sold.append(quantity_sold_dict)
		data = {'labels':months,
			'numbers':quantity_sold }
		
		return Response(data)


def MonthlySaleReport(request):
	quantity_sold = []
	credit_quantity_sold = []
	drug_array = []
	all_drugs = Dosage.objects.all()
	for drug in all_drugs:
		drug_array.append(drug.drug.drug.commercial_name)		
		bills = BillDetail.objects.filter(registered_on__month=1, drug=drug)

		quantity_sold_dict = bills.aggregate(Sum('quantity'))
		if quantity_sold_dict['quantity__sum']:
			 
			quantity_sold.append(quantity_sold_dict['quantity__sum'])

		else:	
			quantity_sold_dict = 0
			quantity_sold.append(quantity_sold_dict)

		print('drug : ', drug, 'sold quantity : ', quantity_sold_dict,'\n')
		
	context = {'labels':drug_array, 'numbers':quantity_sold }

	return render(request,'pharmacy_app/monthly_sale_chart.html',context)

class MonthlySaleData(APIView):
	authentication_classes = []
	permission_classes = []

	def get(self, request, format=None, *args, **kwargs):
		quantity_sold = []
		drug_array = []
		all_drugs = Dosage.objects.all()
		for drug in all_drugs:
			drug_array.append(str(drug))		
			dt = datetime.date(datetime.now())
			bills = BillDetail.objects.filter( registered_on__month=1, drug=drug)
			print(dt.day)
			quantity_sold_dict = bills.aggregate(Sum('quantity'))
			if quantity_sold_dict['quantity__sum']:
				quantity_sold.append(quantity_sold_dict['quantity__sum'])
			else:	
				quantity_sold_dict = 0
				quantity_sold.append(quantity_sold_dict)
#			print('drug : ', drug, 'sold quantity : ', quantity_sold_dict,'\n')
			
		data = {'labels':drug_array,
			'numbers':quantity_sold }
		return Response(data)			

def DailySaleReport(request):
	return render(request, 'pharmacy_app/daily_sale_chart.html')
class DailySaleData(APIView):
	authentication_classes = []
	permission_classes = []

	def get(self, request, format=None, *args, **kwargs):
		quantity_sold = []
		drug_array = []
		all_drugs = Dosage.objects.all()
		for drug in all_drugs:
			drug_array.append(str(drug))		
			dt = datetime.date(datetime.now())
			bills = BillDetail.objects.filter(registered_on__day=dt.day, registered_on__month=dt.month, drug=drug)
			print(dt.day)
			quantity_sold_dict = bills.aggregate(Sum('quantity'))
			if quantity_sold_dict['quantity__sum']:
				quantity_sold.append(quantity_sold_dict['quantity__sum'])
			else:	
				quantity_sold_dict = 0
				quantity_sold.append(quantity_sold_dict)
			print('drug : ', drug, 'sold quantity : ', quantity_sold_dict,'\n')
			
		data = {'labels':drug_array,
			'numbers':quantity_sold }
		return Response(data)			

def MedicalAdministrationRecord(request):
	patients = Patient.objects.all()

	context = {'patients':patients}
	return render(request,'pharmacy_app/medical_administration_record.html', context)

#we use below function to relocate drugs from stock
def DrugRelocationFromStock(request):

	#we use dispension form to retrieve the slot from which drug will be relocated
	dispension_form = DispensionForm()
	qr = InStockSlotDrug.objects.none()
	DispensionFormset = modelformset_factory(InStockSlotDrug, form=DispensionForm, extra=1)
	dispension_formset = DispensionFormset(request.POST or None, queryset=qr)


	drug_relocation_form = DrugRelocationForm()
	qs = DrugRelocationTemp.objects.none()
	DrugRelocationFormset = modelformset_factory(DrugRelocationTemp, form=DrugRelocationForm, extra=1)
	drug_relocation_formset = DrugRelocationFormset(request.POST or None, queryset=qs)

	if request.method == 'POST':
		drug_relocation_formset = DrugRelocationFormset(request.POST)
		dispension_formset = DispensionFormset(request.POST)
		if all([drug_relocation_formset.is_valid(), dispension_formset.is_valid()]):
			relocation_zip = zip(drug_relocation_formset,dispension_formset)
			for a,b in relocation_zip:
				drug_relocation_model = a.save(commit=False)
				in_stock_slot_model_temp = b.save(commit=False)
				#below code subtracts relocated drug amount from stock				
				in_stock_slot_model = InStockSlotDrug.objects.get(drug=drug_relocation_model.drug, slot_no= in_stock_slot_model_temp.slot_no)
				if (in_stock_slot_model.quantity - drug_relocation_model.quantity > (-1)):
					in_stock_slot_model.quantity =  in_stock_slot_model.quantity - drug_relocation_model.quantity
					in_stock_slot_model.save()
					print(in_stock_slot_model.quantity)
					#below code adds relocated drug amount to a temporary storage model 'DrugRelocationTemp'
					try:
						drug_relocation_object = DrugRelocationTemp.objects.get(drug=drug_relocation_model.drug)
						drug_relocation_object.quantity = drug_relocation_object.quantity + drug_relocation_model.quantity
						drug_relocation_object.save()
					except DrugRelocationTemp.DoesNotExist:
						drug_relocation_model.save()
					messages.success(request, str(drug_relocation_model.quantity) + " " + str(drug_relocation_model.drug) + " has been relocated from " + str(in_stock_slot_model.slot_no))
#					return redirect('drug_allocation_to_dispensary', pk = drug_relocation_model.id)
				else:
					print('error')
				#print(in_stock_slot_model.quantity)
			print('hell yeah','\n')

	context = {'dispension_formset':dispension_formset,'drug_relocation_formset':drug_relocation_formset}
	return render(request, 'pharmacy_app/drug_relocation_from_stock.html', context)

#function below 
def DrugAllocationToDispensary(request, row):
	if row==None:
		row=1
	#we use DispensaryDrugForm to allocate drugs that were previously relocated
	#from stock into dispensary
	dispensary_drug_form = DispensaryDrugForm()
	unallocated_drugs = DrugRelocationTemp.objects.all()

#	unallocated_quantity = drug_relocation_model.aggregate(Sum('quantity'))
#	print(unallocated_quantity)
	qr = DispensaryDrug.objects.none()
	DispensaryDrugFormset = modelformset_factory(DispensaryDrug, form=DispensaryDrugForm, extra=1)
	dispensary_drug_formset = DispensaryDrugFormset(request.POST or None, queryset=qr)

	if request.htmx:

		row=row
		dispensary_drug_form = DispensaryDrugForm(request.POST) 
		if dispensary_drug_form.is_valid():

			dispensary_drug_form = dispensary_drug_form.save(commit=False)
			dispensary_slot = dispensary_drug_form.slot_no
			try:
				dispensary_drug_qs = DispensaryDrug.objects.get(slot_no=dispensary_drug_form.slot_no, drug=dispensary_drug_form.drug)
			except DispensaryDrug.DoesNotExist:
				dispensary_drug_qs = None
			#if that drug does not exist in the exact slot submitted in the form, 'DispensaryDrug' model is created
			#else quantity is added to the existing object in the 'DispensaryDrug' Model 
			if not dispensary_drug_qs:
				new_dispensary_drug_model =  DispensaryDrug()
				new_dispensary_drug_model.drug = dispensary_drug_form.drug
				new_dispensary_drug_model.quantity = dispensary_drug_form.quantity
				new_dispensary_drug_model.slot_no = dispensary_drug_form.slot_no
				drug_relocation_object = DrugRelocationTemp.objects.get(drug=dispensary_drug_form.drug)
				drug_relocation_object.quantity = drug_relocation_object.quantity - dispensary_drug_form.quantity
				if drug_relocation_object.quantity > -1:
					drug_relocation_object.save()
				new_dispensary_drug_model.save()
				print(new_dispensary_drug_model.quantity) 
			else :			
				dispensary_drug_model = DispensaryDrug.objects.get(slot_no=dispensary_drug_form.slot_no, drug=dispensary_drug_form.drug)
				dispensary_drug_model.quantity = dispensary_drug_model.quantity + dispensary_drug_form.quantity
				drug_relocation_object = DrugRelocationTemp.objects.get(drug=dispensary_drug_form.drug)
				drug_relocation_object.quantity = drug_relocation_object.quantity - dispensary_drug_form.quantity
				if drug_relocation_object.quantity > -1:
					drug_relocation_object.save()
					dispensary_drug_model.save()
				print(dispensary_drug_model.quantity)
		dispensary_drug_form = DispensaryDrugForm()
		context = {'dispensary_drug_form':dispensary_drug_form, 'unallocated_drugs':unallocated_drugs, 'row':row}
		return render(request, 'pharmacy_app/partials/allocate_drug_to_dispensary_form.html', context)


	"""
	if request.method == 'POST':
		dispensary_drug_formset = DispensaryDrugFormset(request.POST)
		if dispensary_drug_formset.is_valid():
			for form in dispensary_drug_formset:
				dispensary_drug_form = form.save(commit=False)
				dispensary_slot = dispensary_drug_form.slot_no
				try:
					dispensary_drug_qs = DispensaryDrug.objects.get(slot_no=dispensary_drug_form.slot_no, drug=dispensary_drug_form.drug)
				except DispensaryDrug.DoesNotExist:
					dispensary_drug_qs = None
				#if that drug does not exist in the exact slot submitted in the form, 'DispensaryDrug' model is created
				#else quantity is added to the existing object in the 'DispensaryDrug' Model 
				if not dispensary_drug_qs:
					new_dispensary_drug_model =  DispensaryDrug()
					new_dispensary_drug_model.drug = dispensary_drug_form.drug
					new_dispensary_drug_model.quantity = dispensary_drug_form.quantity
					new_dispensary_drug_model.slot_no = dispensary_drug_form.slot_no
					drug_relocation_object = DrugRelocationTemp.objects.get(drug=dispensary_drug_form.drug)
					drug_relocation_object.quantity = drug_relocation_object.quantity - dispensary_drug_form.quantity
					if drug_relocation_object.quantity > -1:
						drug_relocation_object.save()
					new_dispensary_drug_model.save()
					print(new_dispensary_drug_model.quantity) 
				else :			
					dispensary_drug_model = DispensaryDrug.objects.get(slot_no=dispensary_drug_form.slot_no, drug=dispensary_drug_form.drug)
					dispensary_drug_model.quantity = dispensary_drug_model.quantity + dispensary_drug_form.quantity
					drug_relocation_object = DrugRelocationTemp.objects.get(drug=dispensary_drug_form.drug)
					drug_relocation_object.quantity = drug_relocation_object.quantity - dispensary_drug_form.quantity
					if drug_relocation_object.quantity > -1:
						drug_relocation_object.save()
						dispensary_drug_model.save()
					print(dispensary_drug_model.quantity)

				#dispensary_drug_model.save()
				#if 
	"""
	context = {'dispensary_drug_formset':dispensary_drug_formset, 'unallocated_drugs':unallocated_drugs,
				'dispensary_drug_form':dispensary_drug_form, 'row':row
	}
	return render(request, 'pharmacy_app/drug_allocation_to_dispensary.html', context)

def NonPrescriptionBillForm(request):
	
	#This page generates bill model object as clerk dispenses drug from prescriptions
	#pk: primary key of DrugPrescription 
	
	last_bill = Bill.objects.last()
	bill = Bill()
	bill.bill_no = last_bill.bill_no + 1
	print(bill.bill_no)

	dispension_form = DispensionForm()
	
	
#	bill_formset = BillFormSet(request.POST or None)
	qr = DispensaryDrug.objects.none()
	DispensionFormset = modelformset_factory(DispensaryDrug, form=DispensionForm, extra=1)
	dispension_formset = DispensionFormset(request.POST or None, queryset=qr)
	
	
#	small bill formset is used in case clerk has to dispense drugs outside
#	the ones that were prescribed.
	
	qs = BillDetail.objects.none()
	SmallBillFormset = modelformset_factory(BillDetail, form=SmallBillForm, extra=1)
	small_bill_formset = SmallBillFormset(request.POST or None, queryset=qs)
	
	discount_form = DiscountForm(initial={'discount':'No'})
	patient_form = PatientForm()	
	payment_type_form = PaymentTypeForm(initial={'payment_type':'cash'})
	if request.method == 'POST':
		small_bill_formset = SmallBillFormset(request.POST)
		payment_type_form = PaymentTypeForm(request.POST)
		patient_form = PatientForm(request.POST)
		discount_form = DiscountForm(request.POST)
		if all([dispension_formset.is_valid(), small_bill_formset.is_valid()]):
			formset_zip = zip(dispension_formset, small_bill_formset)
			for dispension_form, small_bill_form in formset_zip:
				patient_object = patient_form.save(commit=False)
				discount_object = discount_form.save(commit=False)
				small_bill_detail_model = small_bill_form.save(commit=False)
				print('\n', small_bill_detail_model.drug,'\n')
				small_bill_detail_model.bill = bill 
				drug_price = DrugPrice.objects.get(drug=small_bill_detail_model.drug, active='active')
				small_bill_detail_model.selling_price = drug_price
				if discount_object == 'Yes':
					small_bill_detail_model.discount = 'Yes'
				else:
					small_bill_detail_model.discount == 'No'
#				small_bill_detail_model.patient = prescription.patient
				small_bill_detail_model.registered_on = datetime.now()
				stock_slot_model = dispension_form.save(commit=False)
				try:
					slot_drug = DispensaryDrug.objects.get(slot_no=stock_slot_model.slot_no, drug = small_bill_detail_model.drug)
					if slot_drug.quantity - small_bill_detail_model.quantity > (-1):
						slot_drug.quantity = slot_drug.quantity - small_bill_detail_model.quantity
						bill.save()
						small_bill_detail_model.save()
						payment_type_form = payment_type_form.save(commit=False)
						print(patient_object.patient)
						if payment_type_form.payment_type == 'credit':
							try:
								patient_credit = PatientCredit.objects.get(patient=patient_object.patient)
								print(patient_credit)
								patient_credit.credit_amount = patient_credit.credit_amount + total_price
								print('\n', total_price,'llllss')
								
								patient_credit.save()
							except:
								new_patient_credit = PatientCredit()
								new_patient_credit.patient = patient_object.patient
								new_patient_credit.credit_amount =  total_price
								print('\n', total_price,'lllls4s')
								new_patient_credit.save()
						slot_drug.save()
						return redirect('bill_detail', pk = bill.bill_no)
				
						print('yeah yeah')
					else:
						print("yo you dont have")
				except:
					print('nothing')
		else:
			print('bill form error ', bill_form.errors)

#		dispension_form = Dispe
	context = { 'bill':bill,'small_bill_formset':small_bill_formset, 'patient_form':patient_form,
				'dispension_formset': dispension_formset, 'payment_type_form':payment_type_form
				,'discount_form':discount_form}
	return render(request, 'pharmacy_app/non_prescription_bill_form.html', context)

def PatientCreditPage(request):

	return render(request, 'pharmacy_app/patient_credit.html')

def AssignPharmacistToDispensary(request, dispensary_id):
	dispensary = Dispensary.objects.get(id=dispensary_id)
	if request.method == 'POST':
		assign_form = AssignPharmacistForm(request.POST)
		if assign_form.is_valid():
			dispensary_pharmacist = assign_form.save(commit=False)
			dispensary_pharmacist.dispensary = dispensary
			dispensary_pharmacist.active = True
			dispensary_pharmacist.save()

			messages.success(request,'Successful!')
			return redirect('dispensary_list')
		else:
			messages.error(request,str(assign_form.errors))
			return redirect('dispensary_list')
            #elif user.employee.designation.name == 'Laboratory Head':

def PharmacistDrugRequest(request, row):
	if row==None:
		row=1
	else:
		print('l',row)
	qr = DispensaryDrug.objects.none()
	RequestFormset = modelformset_factory(DispensaryProcurementRequest, form=DrugRequestForm, extra=0)
	request_formset = RequestFormset(request.POST or None, queryset=qr)
	
	request_form = DrugRequestForm()
	#request_url = reverse("pharmacist_drug_request")
	context = {'request_form':request_form}
	if request.method == 'POST':
		print('Here As Well!!!!!!!!!!!11111111')

		"""
		#request_formst = RequestFormset(request.POST)
		#if request_formset.is_valid():
			for request_form in request_formset:
				#small_bill_detail_model = form.save(commit=False)
				request_model = request_form.save(commit=False)
				request_model.dispensary = DispensaryPharmacist.objects.get(pharmacist__user_profile=request.user, active=True)
				request_model.active = True
				request_model.save()
			
		request_form2 = DrugRequestForm(request.POST) 
		if request_form2.is_valid():
			print('Hes Sir22')
			request_form2.save()
			messages.success(request,'Successful!')
			#return redirect('dispensary_list')
		else:
			messages.error(request,str(request_formset.errors))
			#return redirect('dispensary_list')
		request_form = DrugRequestForm()
		context = {'request_form':request_form}
		"""	
	if request.htmx:

		row=row
		request_form2 = DrugRequestForm(request.POST) 
		if request_form2.is_valid():
			print('Hes Sir')
			request_model = request_form2.save(commit=False)
			request_model.dispensary = DispensaryPharmacist.objects.get(pharmacist__user_profile=request.user, active=True)
			request_model.active = True
			request_model.save()
			print('yeyy yeyyyyyi')
		print('Has come!!!')
		request_form = DrugRequestForm()
		context = {'request_form':request_form, 'row':row}
		return render(request,'pharmacy_app/partials/drug_request_form.html', context)
	context = {'row':row,'request_form':request_form, 'request_formset':request_formset}
	return render(request, 'pharmacy_app/pharmacist_drug_request.html', context)
		
def DrugRequestFirstApproval(request):
	request_list = DispensaryProcurementRequest.objects.filter(active=True, first_approval=False)
	
	dispensary_array = []
	count=None
	dis_array = []
	for request1 in request_list:
		dispensary_request = DispensaryProcurementRequest.objects.filter(active=True, first_approval=False, dispensary__dispensary=request1.dispensary.dispensary).last()
		if dispensary_request.dispensary.dispensary not in dis_array:
			dispensary_array.append(dispensary_request)
		for request3 in dispensary_array:
			dis_array.append(request3.dispensary.dispensary)
		"""
		count1=0
		if count1==0:
			for request2 in dispensary_request:
				count = 0
				if count==0:					
					dispensary_array.append(request2)
				count = 1
			count1=1
		"""
	for request1 in dispensary_array:
		print('\n',request1.id,'\n')
	dis_array2 = []
	dispensary_array2 = []
	request_list2 = DispensaryProcurementRequest.objects.filter(active=True, first_approval=True, second_approval=True)
	for request1 in request_list2:
		dispensary_request = DispensaryProcurementRequest.objects.filter(active=True, first_approval=True,second_approval=True, dispensary__dispensary=request1.dispensary.dispensary).last()
		if dispensary_request.dispensary.dispensary not in dis_array2:
			dispensary_array2.append(dispensary_request)
		for request3 in dispensary_array2:
			dis_array2.append(request3.dispensary.dispensary)

	context = {'request_list':dispensary_array, 'request_list2':dispensary_array2}
	return render(request, 'pharmacy_app/drug_request_first_approval.html', context)

def RequestListFromStock(request):
	dis_array2 = []
	dispensary_array2 = []
	request_list2 = DispensaryProcurementRequest.objects.filter(active=True, first_approval=True, second_approval=True)
	for request1 in request_list2:
		dispensary_request = DispensaryProcurementRequest.objects.filter(active=True, first_approval=True,second_approval=True, dispensary__dispensary=request1.dispensary.dispensary).last()
		if dispensary_request.dispensary.dispensary not in dis_array2:
			dispensary_array2.append(dispensary_request)
		for request3 in dispensary_array2:
			dis_array2.append(request3.dispensary.dispensary)
	
	context = {'request_list2':dispensary_array2}
	return render(request, 'pharmacy_app/request_list_from_stock.html', context)

def ViewDrugRequest(request, dispensary_id):
	dispensary = Dispensary.objects.get(id=dispensary_id)
	request_list = DispensaryProcurementRequest.objects.filter(active=True, dispensary__dispensary__id=dispensary_id)
	request1 = DispensaryProcurementRequest.objects.filter(active=True, dispensary__dispensary__id=dispensary_id).first()
	
	context = {'request_list':request_list, 'request':request1}
	return render(request, 'pharmacy_app/view_drug_request.html', context)

def ConfirmApproval(request, dispensary_id):

	return render(request, 'pharmacy_app/confirm_approval.html')

def ViewApprovedRequest(request, dispensary_id, row):
	if row==None:
		row = 1
	dispensary = Dispensary.objects.get(id=dispensary_id)
	request_list = DispensaryProcurementRequest.objects.filter(active=True, dispensary__dispensary__id=dispensary_id)
	request1 = DispensaryProcurementRequest.objects.filter(active=True, dispensary__dispensary__id=dispensary_id).first()

	qr = DispensaryDrug.objects.none()
	RequestFormset = modelformset_factory(DispensaryProcurementRequest, form=DrugRequestForm, extra=0)
	request_formset = RequestFormset(request.POST or None, queryset=qr)

	qr = DispensaryDrug.objects.none()
	RequestFormset = modelformset_factory(DispensaryProcurementRequest, form=DrugRequestForm, extra=0)
	request_formset = RequestFormset(request.POST or None, queryset=qr)
	
	request_form = DrugRelocationForm()
	slot_form = StockSlotForm()	
	if request.htmx:				
		request_form = DrugRelocationForm(request.POST)
		slot_form = StockSlotForm(request.POST)	
		if all([request_form.is_valid(), slot_form.is_valid()]):
			print('ddddssss')
			drug_relocation_model = request_form.save(commit=False)
			in_stock_slot_model_temp = slot_form.save(commit=False)
			print(drug_relocation_model.drug, in_stock_slot_model_temp.stock_slot_no)
			#below code subtracts relocated drug amount from stock				
			in_stock_slot_model = InStockSlotDrug.objects.get(drug=drug_relocation_model.drug, slot_no= in_stock_slot_model_temp.stock_slot_no)
			print('fsjlakjlaj')
			if (in_stock_slot_model.quantity - drug_relocation_model.quantity > (-1)):
				in_stock_slot_model.quantity =  in_stock_slot_model.quantity - drug_relocation_model.quantity
				in_stock_slot_model.save()
				print(in_stock_slot_model.quantity)
				#below code adds relocated drug amount to a temporary storage model 'DrugRelocationTemp'
				#try:
				drug_relocation_object = DrugRelocationTemp.objects.get(drug=drug_relocation_model.drug)
				drug_relocation_object.quantity = drug_relocation_object.quantity + drug_relocation_model.quantity
				drug_relocation_object.save()

				if row==3345:
					context = {'request_list':request_list, 'request':request1,
								'dispensary_id':dispensary_id
					}
				
					return render(request, 'pharmacy_app/view_approved_request.html', context)

				#except DrugRelocationTemp.DoesNotExist:
				#	drug_relocation_model.save()
				messages.success(request, str(drug_relocation_model.quantity) + " " + str(drug_relocation_model.drug) + " has been relocated from " + str(in_stock_slot_model.slot_no))
			else:
				print('NOT WORKED HERE @@@@!!!')
		request_form = DrugRelocationForm()
		slot_form = StockSlotForm()	

		context = {'request_list':request_list, 'request':request1,
					'slot_form':slot_form, 'request_form':request_form,
					'dispensary_id':dispensary_id, 'row':row,
				}
		return render(request, 'pharmacy_app/partials/approved_drug_request_form.html', context)

	context = {'request_list':request_list, 'request':request1,
				'slot_form':slot_form, 'request_form':request_form,
				'dispensary_id':dispensary_id,'row':row
	}
	return render(request, 'pharmacy_app/view_approved_request.html', context)


def TempRequestSave(request, dispensary_id):
	dispensary = Dispensary.objects.get(id=dispensary_id)
	request_list = DispensaryProcurementRequest.objects.filter(active=True, dispensary__dispensary__id=dispensary_id)
	for request1 in request_list:
		request1.active=False
		request1.save()
	messages.success(request, 'Successful!')
	return redirect('drug_request_first_approval')


def ApproveRequest(request, dispensary_id):
	dispensary = Dispensary.objects.get(id=dispensary_id)
	request_list = DispensaryProcurementRequest.objects.filter(active=True, dispensary__dispensary__id=dispensary_id)
	for request1 in request_list:
		if request1.first_approval == True:
			request1.second_approval = True 
			request1.save()
		else:
			request1.first_approval = True 
			request1.save()
	messages.success(request, 'Successful!')
	return redirect('drug_request_first_approval')

def DrugRequestSecondApproval(request):
	request_list = DispensaryProcurementRequest.objects.filter(active=True, first_approval=True,second_approval=False)
	
	dispensary_array = []
	count=None
	dis_array = []
	for request1 in request_list:
		dispensary_request = DispensaryProcurementRequest.objects.filter(active=True, first_approval=True, second_approval=False, dispensary__dispensary=request1.dispensary.dispensary).last()
		if dispensary_request.dispensary.dispensary not in dis_array:
			dispensary_array.append(dispensary_request)
		for request3 in dispensary_array:
			dis_array.append(request3.dispensary.dispensary)

	request_list = DispensaryProcurementRequest.objects.filter(active=True, first_approval=True, second_approval=False)
	context = {'request_list':dispensary_array}
	return render(request, 'pharmacy_app/drug_request_second_approval.html', context)

def PharmacyReport1(request):
# Chart data is passed to the `dataSource` parameter, like a dictionary in the form of key-value pairs.
	dataSource = OrderedDict()
	supply_chart = OrderedDict()
	dispensary_supply_chart = OrderedDict()

# The `chartConfig` dict contains key-value pairs of data for chart attribute
	chartConfig = OrderedDict()
	chartConfig["caption"] = "Drugs Sold Today"
	chartConfig["subCaption"] = "In Birr"
	chartConfig["xAxisName"] = "Country"
	chartConfig["yAxisName"] = "Reserves (MMbbl)"
	chartConfig["numberSuffix"] = " Birr"
	chartConfig["theme"] = "fusion"
	chartConfig["numVisiblePlot"] = "8",
	chartConfig["flatScrollBars"] = "1",
	chartConfig["scrollheight"] = "1",
	chartConfig["type"] = "pie2d",

	dataSource["chart"] = chartConfig
	dataSource["data"] = []

	supply_chart["chart"] = chartConfig
	supply_chart["chart"] = {
		"caption":'Total Drugs Supplied',
		"subCaption":'In Unit',
		"numberSuffix":'Units',
		'theme':'fusion',
	}
	dispensary_supply_chart["chart"] = {
		"caption":'Total Drugs Supplied',
		"subCaption":'In Unit',
		"numberSuffix":'Units',
		'theme':'fusion',
	}

	supply_chart["data"] = []
	dispensary_supply_chart["data"] = []

	filtered_dispensary_id = int(request.GET.get('dispensary_id','0')) or None
	filtered_procurement_id = int(request.GET.get('procurement_id','0')) or None
	filtered_drug_id = int(request.GET.get('drug_id','0')) or None

	if filtered_dispensary_id:
		filtered_dispensary = Dispensary.objects.get(id=filtered_dispensary_id)
		print(filtered_dispensary,'dsdsdsds')
	else:
		filtered_dispensary = None
	if filtered_procurement_id:
		filtered_procurement = Procurement.objects.get(procurement_no=filtered_procurement_id)
		print('pprprprprp: ',filtered_procurement)
	else:
		filtered_procurement = None

	if filtered_drug_id:
		filtered_drug = Dosage.objects.get(id=filtered_drug_id)
		print('pprprprpr111111111111p: ',filtered_drug)
	else:
		filtered_drug = None

	all_drugs = Dosage.objects.all()
	slot_drugs = DispensarySlot.objects.all()
	drug_array = []
	shelf_quantity_array = []
	stock_quantity_array = []
	total_quantity_array = []
	stock_array = []
	alert_array = []
	alert_drug_array = []
	drug_price_array = []
	alert_zip = None

	if filtered_dispensary:
		for drug in all_drugs:
			total_quantity = 0
			shelf_quantity = 0 
			drug_on_slot = DispensaryDrug.objects.filter(drug=drug,slot_no__shelf_no__dispensary=filtered_dispensary)
			shelf_quantity_dict = drug_on_slot.aggregate(Sum('quantity'))
			shelf_quantity = shelf_quantity_dict['quantity__sum']
			if shelf_quantity==None:
				shelf_quantity=0
			shelf_quantity_array.append(shelf_quantity)
			#print(drug, 'shelf quantity:',shelf_quantity,'\n')
			#total_quantity = shelf_quantity 
			#total_quantity_array.append(total_quantity)
			drug_array.append(drug)
			drug_price_array.append(DrugPrice.objects.get(drug=drug))
			inventory_zip = zip(drug_array, shelf_quantity_array,drug_price_array)

	else:
		for drug in all_drugs:
			total_quantity = 0
			shelf_quantity = 0 
			stock_quantity = 0

			#drug on slot is drugs that are in dispensaries
			#drug in stock are drugs in stocks
			drug_on_slot = DispensaryDrug.objects.filter(drug=drug)
			drug_in_stock = InStockSlotDrug.objects.filter(drug=drug)

			#shelf quantity is quantity of drug in dispensaries

			shelf_quantity_dict = drug_on_slot.aggregate(Sum('quantity'))
			shelf_quantity = shelf_quantity_dict['quantity__sum']
			shelf_quantity_array.append(shelf_quantity)
			#print(drug, 'shelf quantity:',shelf_quantity,'\n')

			#stock quantity is quantity of drug in stocks
			stock_quantity_dict = drug_in_stock.aggregate(Sum('quantity'))
			stock_quantity = stock_quantity_dict['quantity__sum']
			stock_quantity_array.append(stock_quantity)

			#print(drug, 'stock quantity: ', stock_quantity,'\n')

			total_quantity = shelf_quantity + stock_quantity
			total_quantity_array.append(total_quantity)
			#print('total_quantity :', total_quantity,'\n')

			drug_array.append(drug)
			drug_price_array.append(DrugPrice.objects.get(drug=drug))
			inventory_zip = zip(drug_array, total_quantity_array,drug_price_array)
			dataSource["data"].append({"label": str(drug), "value": total_quantity})
			print('drug: ',drug,'qua: ',total_quantity,'\n')
			if InventoryThreshold.objects.get(drug=drug):
				threshold = InventoryThreshold.objects.get(drug = drug)
			#print('ddddddddddd',total_quantity, 'ccccccccccccc',threshold.threshold)
			#if drug quantity in shelf and dispensary is less than its threshold it is in low stock level
			if total_quantity < threshold.threshold:
				alert_array.append(threshold.threshold - total_quantity)
				alert_drug_array.append(drug)
				alert_zip = zip(alert_drug_array, alert_array)

	#for a,b in inventory_zip:
	#	print('aaaaa',a)
	if filtered_procurement:
		drug_supply = DrugSupply.objects.filter(drug__isnull=False, batch__procurement=filtered_procurement)
	else:
		drug_supply = DrugSupply.objects.filter(drug__isnull=False)
	supplied_drug = []
	supplied_amount = []
	for supply in drug_supply:
		if supply.drug in supplied_drug:
			print('')
		else:	
			if filtered_procurement:
				drug_supplied = DrugSupply.objects.filter(drug=supply.drug, batch__procurement=filtered_procurement)
			else:
				drug_supplied = DrugSupply.objects.filter(drug=supply.drug, batch__procurement=filtered_procurement)

			supplied_drug.append(supply.drug)
			temp_dict = drug_supplied.aggregate(Sum('supplied_quantity'))
			temp_quantity = temp_dict['supplied_quantity__sum']
			supplied_amount.append(temp_quantity)
			supply_chart["data"].append({"label": str(supply.drug), "value": temp_quantity})
	
	dispensed_drug = []
	dispensed_amount = []
	dispensary_supplied = []
	for drug in Dosage.objects.all():
		if filtered_procurement:

			a = 1
			dispensed_drug.append(drug)
			dispensed_amount.append(2 + a)
			a= a +2
			drug_supply = DrugSupplyToDispensary.objects.filter(drug=drug)
			temp_dict = drug_supply.aggregate(Sum('quantity'))
			temp_quantity = temp_dict['quantity__sum']
			dispensary_supplied.append(temp_quantity)
			dispensary_supply_chart["data"].append({"label": str(drug), "value": temp_quantity})

		else:
				
			a = 3
			dispensed_drug.append(drug)
			dispensed_amount.append(5 + a)
			a= a +4
			drug_supply = DrugSupplyToDispensary.objects.filter(drug=drug)
			temp_dict = drug_supply.aggregate(Sum('quantity'))
			temp_quantity = temp_dict['quantity__sum']
			dispensary_supplied.append(temp_quantity)
			dispensary_supply_chart["data"].append({"label": str(drug), "value": temp_quantity})

	dispense_zip = zip(dispensed_drug, dispensed_amount)
	supply_zip = zip(supplied_drug,supplied_amount)
	dispensary_supply_zip =zip(dispensed_drug,dispensary_supplied)

	dispensary_list =  Dispensary.objects.all()
	procurement_list =  Procurement.objects.all()

	all_prescriptions = DrugPrescription.objects.all()

	if filtered_drug:			
		prescription_list = DrugPrescription.objects.filter(drug=filtered_drug)
		ward_prescription = DrugPrescription.objects.filter(inpatient='true', drug=filtered_drug)
		emgc_prescription = 1
	else:
		prescription_list = DrugPrescription.objects.all()
		ward_prescription = DrugPrescription.objects.filter(inpatient='true')
		emgc_prescription = 3
	#opd_prescription = 

	prescriptions_today = DrugPrescription.objects.filter()[:5][::-1]
	patients = []
	active_drugs = []

	drugs_taken = []
	patient2 = []
	cost = []
	cost_sum = 0
	for patient in Patient.objects.all():
		patient_prescriptions = DrugPrescription.objects.filter(patient=patient)
		if patient_prescriptions:
			#print('hehehheheheh:   ss', patient_prescriptions.count(), patient)
			if patient_prescriptions.count()>1:
				patients.append(patient)
				active_drugs.append(patient_prescriptions.count())
				#print(patient_prescriptions.count())
		
			drugs_taken.append(patient_prescriptions.count())
			patient2.append(patient)
			for p in patient_prescriptions:
				drug_price = DrugPrice.objects.get(drug=drug,active='active')
				cost_sum = cost_sum + drug_price.selling_price
			cost.append(cost_sum)
	poly_pharmacy_zip = zip(patients,active_drugs)
	top_customers_zip = zip(patient2,drugs_taken,cost)

	dispensed_drug_array = []

	pharmacist_array = []
	dispensary_array = []
	cashier_array = []
	revenue_array = []
	for dispensary in dispensary_list:
		pharmacist_list = DispensaryPharmacist.objects.filter(dispensary=dispensary)
		cashier_list = DispensaryCashier.objects.filter(dispensary=dispensary)
		dispensary_array.append(dispensary)
		if pharmacist_list:
			pharmacist_array.append(pharmacist_list.count())
		else:
			pharmacist_array.append(0)
		if cashier_list:
			cashier_array.append(cashier_list.count())
		else:
			cashier_array.append(0)
	
		dispensed_drugs = DrugDispensed.objects.filter(dispensary=dispensary)
		if dispensed_drugs:
			dispensed_sum = 0
			revenue = 0
			for d in dispensed_drugs:
				dispensed_sum = dispensed_sum + (d.bill_no.quantity) 
				revenue = revenue + (d.bill_no.quantity * d.bill_no.selling_price.selling_price)
			dispensed_drug_array.append(dispensed_sum)
			revenue_array.append(revenue)
		else:
			dispensed_drug_array.append(0)
			revenue_array.append(0)
	dispensary_zip = zip(dispensary_array,pharmacist_array,cashier_array)
	dispensaries_by_sale = zip(dispensary_array,dispensed_drug_array)
	dispensaries_by_revenue = zip(dispensary_array,revenue_array)
	
	sale_amount = 0
	sale_sum = 0
	today = datetime.now()
	today_sale = DrugDispensed.objects.filter(registered_on__day=today.day, bill_no__isnull=False,bill_no__selling_price__isnull=False)
	for sale in today_sale:
		sale_amount = sale_amount + sale.bill_no.quantity
		sale_sum = sale_sum +(sale.bill_no.selling_price.selling_price * sale.bill_no.quantity)

	print('Drugs Sold: ',sale_amount,'\n','Sale Amount:',sale_sum)
	if request.htmx:
		dispensary_id = request.GET.get('id')
		#print('HOHOHOHOHOOHOHOHO','\n','jsksksks',item_id)
		dispensed_drugs2 = DrugDispensed.objects.filter(dispensary_id=dispensary_id)

		context2 = {'dispensed_drugs2':dispensed_drugs2}
		return render(request,'pharmacy_app/partials/pharmacy_report1_partial.html', context2)

	
	inventory_pie_chart = FusionCharts("pie2d", "myFirstChart", "500", "300", "myFirstchart-container", "json", dataSource)
	inventory_bar_chart = FusionCharts("column2d", "myFirstChart2", "500", "300", "inventory-bar-chart-container", "json", dataSource)

	supply_pie_chart = FusionCharts("pie2d", "myFirstChart3", "500", "300", "supplied_drug_pie_chart_container", "json", supply_chart)
	supply_bar_chart = FusionCharts("column2d", "myFirstChart4", "500", "300", "supplied_drug_bar_chart_container", "json", supply_chart)

	dispensary_supply_pie_chart = FusionCharts("pie2d", "myFirstChart5", "500", "300", "dispensary_supplied_drug_pie_chart_container", "json", dispensary_supply_chart)
	dispensary_supply_bar_chart = FusionCharts("column2d", "myFirstChart6", "500", "300", "dispensary_supplied_drug_bar_chart_container", "json", dispensary_supply_chart)

	context = {'inventory_zip': inventory_zip,
				'inventory_pie_chart':inventory_pie_chart.render(),
				'inventory_bar_chart':inventory_bar_chart.render(),

				'supply_pie_chart':supply_pie_chart.render(),
				'supply_bar_chart':supply_bar_chart.render(),				
				'supply_zip':supply_zip,

				'dispensary_supply_pie_chart':dispensary_supply_pie_chart.render(),
				'dispensary_supply_bar_chart':dispensary_supply_bar_chart.render(),
				'dispense_zip':dispense_zip,

				'dispensary_list':dispensary_list,
				'procurement_list':procurement_list,
				'alert_zip':alert_zip,
				'dispensary_supply_zip':dispensary_supply_zip,
				'ward_prescription':ward_prescription.count(),
				'opd_prescription':prescription_list.count() - ward_prescription.count(),
				'emgc_prescription':emgc_prescription,
				'total_prescription':prescription_list.count(),
				'prescription_list':all_prescriptions,

				'drugs':all_drugs,
				'prescriptions_today':prescriptions_today,
				'poly_pharmacy_zip':poly_pharmacy_zip,
				'top_customers_zip':top_customers_zip,

				'dispensary_zip':dispensary_zip,
				'dispensaries_by_sale':dispensaries_by_sale,
				'dispensaries_by_revenue':dispensaries_by_revenue,

				'sale_sum':sale_sum,
				'sale_amount':sale_amount,

	}

	return render(request, 'pharmacy_app/pharmacy_report1.html', context)


def PrescriptionListReport(request):
	filtered_sex = str(request.GET.get('sex')) or None
	filtered_department = str(request.GET.get('department')) or None

	if filtered_sex =='MALE' or filtered_sex =='FEMALE':
		all_prescriptions = DrugPrescription.objects.filter(patient__sex=filtered_sex)
		print('dddd',filtered_sex)
	else:
		all_prescriptions = DrugPrescription.objects.all()

	if filtered_department:
		if filtered_department == 'Inpatient':
			all_prescriptions = all_prescriptions.filter(inpatient='true')
			print('dddd22')
			for p in all_prescriptions:
				print(p,'\n')

		else:
			all_prescriptions = all_prescriptions.exclude(inpatient='true')
			print('dddd33')
	else:
		all_prescriptions = DrugPrescription.objects.all()
	
	drugs = Dosage.objects.all()

	age = []
	for i in range(1,120):
		age.append(i)
	sex = ['MALE','FEMALE']
	prescription_department = ['Inpatient','Outpatient']

	payment_statuses = ['Insurance','Free','Credit','Default']
	dosage_forms = ['Tablet','Capsule','Oral_solution','Injection','Injection with Dilutent']

	context = {'prescription_list':all_prescriptions,
				'age_array':age,
				'drugs':drugs,
				'sex':sex,
				'payment_statuses':payment_statuses,
				'dosage_forms':dosage_forms,
				'prescription_department':prescription_department,

	}

	return render(request, 'pharmacy_app/prescription_list_report.html',context)

def SuppliedDrugReport(request):
	filtered_sex = str(request.GET.get('sex')) or 'None'
	filtered_drug = request.GET.get('drug') or 'None2'

	if filtered_sex =='MALE' or filtered_sex =='FEMALE':
		all_prescriptions = DrugPrescription.objects.filter(patient__sex=filtered_sex)
		print('dddd',filtered_sex)
	else:
		all_prescriptions = DrugPrescription.objects.all()

	if filtered_drug == 'None2':
		supplied_list = DrugSupply.objects.all()
	else:
		drug = Dosage.objects.get(id=filtered_drug)
		supplied_list = DrugSupply.objects.filter(drug=drug)
	
	drugs = Dosage.objects.all()
	stock_list = InStock.objects.all()

	context = {'supplied_list':supplied_list,
				'drugs':drugs,
				'stock_list':stock_list,
	}

	return render(request, 'pharmacy_app/supplied_drug_report.html',context)

def DispensarySupplyReport(request):
	filtered_drug = request.GET.get('drug') or 'None2'
	filtered_dispensary = request.GET.get('dispensary') or 'None2'
	print(filtered_drug)

	supplied_list = DrugSupplyToDispensary.objects.all()
	if filtered_drug == 'None2' or filtered_drug == '0':
		supplied_list = DrugSupplyToDispensary.objects.all()
	else:
		drug = Dosage.objects.get(id=filtered_drug)
		supplied_list = supplied_list.filter(drug=drug)
	if filtered_dispensary == 'None2' or filtered_dispensary == '0':
		print('Do Nothing')
	else:
		dispensary = Dispensary.objects.get(id=filtered_dispensary)
		supplied_list = supplied_list.filter(dispensary=dispensary)	

	drugs = Dosage.objects.all()
	dispensary_list = Dispensary.objects.all()

	context = {'supplied_list':supplied_list,
				'drugs':drugs,
				'dispensary_list':dispensary_list,
	}

	return render(request, 'pharmacy_app/dispensary_supplied_report.html',context)

def DrugBillReport(request):
	start_date = datetime.strptime(request.GET.get('start_date') or '1970-01-01', '%Y-%m-%d')
	end_date = datetime.strptime(request.GET.get('end_date') or str(datetime.now().date()),  '%Y-%m-%d')

	filtered_drug = request.GET.get('drug') or 'None2'
	filtered_dispensary = request.GET.get('dispensary') or 'None2'

	bill_list = DrugDispensed.objects.filter(registered_on__range=[start_date,end_date])
	if filtered_drug == 'None2' or filtered_drug == '0':
		print('Do Nothing')
	else:
		bill_list = bill_list.filter(bill_no__drug = Dosage.objects.get(id=filtered_drug))
	if filtered_dispensary == 'None2' or filtered_dispensary == '0':
		print('Do Nothing')
	else:
		dispensary = Dispensary.objects.get(id=filtered_dispensary)
		bill_list = bill_list.filter(dispensary = dispensary)
	drugs = Dosage.objects.all()
	dispensary_list = Dispensary.objects.all()
	age = []
	for i in range(1,120):
		age.append(i)
	sex = ['MALE','FEMALE']
	department = ['Inpatient','Outpatient']

	payment_statuses = ['Insurance','Free','Credit','Default']
	dosage_forms = ['Tablet','Capsule','Oral_solution','Injection','Injection with Dilutent']

	context = {'bill_list':bill_list,
				'drugs':drugs,
				'dispensary_list':dispensary_list,
				'age_array':age,
				'payment_statuses':payment_statuses,
				'department':department
	}

	return render(request, 'pharmacy_app/drug_bill_report.html',context)

def TodaySaleReport(request):
	sale_amount = 0
	sale_sum = 0
	today = datetime.now()
	dispensed_drugs = DrugDispensed.objects.filter( bill_no__isnull=False,bill_no__selling_price__isnull=False)
	
	drugs = Dosage.objects.all()

	age = []
	for i in range(1,120):
		age.append(i)
	sex = ['MALE','FEMALE']
	prescription_department = ['Inpatient','Outpatient']

	payment_statuses = ['Insurance','Free','Credit','Default']
	dosage_forms = ['Tablet','Capsule','Oral_solution','Injection','Injection with Dilutent']

	context = {'sale_sum':sale_sum,
				'sale_amount':sale_amount,
				'dispensed_drugs':dispensed_drugs,
	
	}
	return render(request, 'pharmacy_app/today_sale_report.html',context)

def PharmacyReportChart(request):
	return render(request, 'pharmacy_app/pharmacy_report_chart.html')

def PharmacyReportChart1(request):
	return render(request, 'pharmacy_app/pharmacy_report_chart1.html')

class PharmacyReportChartData(APIView):
	authentication_classes = []
	permission_classes = []

	def get(self, request, format=None, *args, **kwargs):
		print('klslssssssssssssssssssssssssssjdd')
		drug_supply = DrugSupply.objects.filter(drug__isnull=False)
		supplied_drug = []
		supplied_drug1 = []
		supplied_amount = []
		for supply in drug_supply:
			if supply.drug in supplied_drug1:
				print('ss')
			else:	
				drug_supplied = DrugSupply.objects.filter(drug=supply.drug)

				supplied_drug.append(str(supply.drug))
				supplied_drug1.append(supply.drug)
				temp_dict = drug_supplied.aggregate(Sum('supplied_quantity'))
				temp_quantity = temp_dict['supplied_quantity__sum']
				supplied_amount.append(temp_quantity)
		for a in supplied_amount:
			print(a)
		for a in supplied_drug:
			print(a)

		shelf_quantity_array = []
		stock_quantity_array = []
		total_quantity_array = []
		drug_array = []
		for drug in Dosage.objects.all():
			total_quantity = 0
			shelf_quantity = 0 
			stock_quantity = 0

			#drug on slot is drugs that are in dispensaries
			#drug in stock are drugs in stocks
			drug_on_slot = DispensaryDrug.objects.filter(drug=drug)
			drug_in_stock = InStockSlotDrug.objects.filter(drug=drug)

			#shelf quantity is quantity of drug in dispensaries

			shelf_quantity_dict = drug_on_slot.aggregate(Sum('quantity'))
			shelf_quantity = shelf_quantity_dict['quantity__sum']
			shelf_quantity_array.append(shelf_quantity)
			#print(drug, 'shelf quantity:',shelf_quantity,'\n')

			#stock quantity is quantity of drug in stocks
			stock_quantity_dict = drug_in_stock.aggregate(Sum('quantity'))
			stock_quantity = stock_quantity_dict['quantity__sum']
			stock_quantity_array.append(stock_quantity)

			#print(drug, 'stock quantity: ', stock_quantity,'\n')

			total_quantity = shelf_quantity + stock_quantity
			total_quantity_array.append(total_quantity)
			#print('total_quantity :', total_quantity,'\n')

			drug_array.append(str(drug))

		labels = ['one','two','three']
		number = [10]
		data = {'supplied_labels':supplied_drug,
				'supplied_numbers':supplied_amount,
				'drug_array':drug_array,
				'total_quantity_array':total_quantity_array,
				}
		return Response(data)

class PharmacyReportChartData1(APIView):
	authentication_classes = []
	permission_classes = []

	def get(self, request, format=None, *args, **kwargs):
		print('klslssssssssssssssssssssssssssjdd')
		drug_supply = DrugSupply.objects.filter(drug__isnull=False)
		supplied_drug = []
		supplied_drug1 = []
		supplied_amount = []
		for supply in drug_supply:
			if supply.drug in supplied_drug1:
				print('ss')
			else:	
				drug_supplied = DrugSupply.objects.filter(drug=supply.drug)

				supplied_drug.append(str(supply.drug))
				supplied_drug1.append(supply.drug)
				temp_dict = drug_supplied.aggregate(Sum('supplied_quantity'))
				temp_quantity = temp_dict['supplied_quantity__sum']
				supplied_amount.append(temp_quantity)
		for a in supplied_amount:
			print(a)
		for a in supplied_drug:
			print(a)

		shelf_quantity_array = []
		stock_quantity_array = []
		total_quantity_array = []
		drug_array = []
		for drug in Dosage.objects.all():
			total_quantity = 0
			shelf_quantity = 0 
			stock_quantity = 0

			#drug on slot is drugs that are in dispensaries
			#drug in stock are drugs in stocks
			drug_on_slot = DispensaryDrug.objects.filter(drug=drug)
			drug_in_stock = InStockSlotDrug.objects.filter(drug=drug)

			#shelf quantity is quantity of drug in dispensaries

			shelf_quantity_dict = drug_on_slot.aggregate(Sum('quantity'))
			shelf_quantity = shelf_quantity_dict['quantity__sum']
			shelf_quantity_array.append(shelf_quantity)
			#print(drug, 'shelf quantity:',shelf_quantity,'\n')

			#stock quantity is quantity of drug in stocks
			stock_quantity_dict = drug_in_stock.aggregate(Sum('quantity'))
			stock_quantity = stock_quantity_dict['quantity__sum']
			stock_quantity_array.append(stock_quantity)

			#print(drug, 'stock quantity: ', stock_quantity,'\n')

			total_quantity = shelf_quantity + stock_quantity
			total_quantity_array.append(total_quantity)
			#print('total_quantity :', total_quantity,'\n')

			drug_array.append(str(drug))

		labels = ['one','two','three']
		number = [10]
		data = {'supplied_labels':supplied_drug,
				'supplied_numbers':supplied_amount,
				'drug_array':drug_array,
				'total_quantity_array':total_quantity_array,
				}
		return Response(data)
