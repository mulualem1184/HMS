from django.shortcuts import render
from .models import *
from core.models import *
from pharmacy_app.models import *
from django.contrib import messages
from .forms import *
from django.shortcuts import redirect
from django.contrib import messages
from datetime import datetime

from django.forms.models import modelformset_factory

# Create your views here.
def ServiceFormPage(request):
	service_form = CreateServiceForm()
	if request.method == 'POST':
		service_form = CreateServiceForm(request.POST)
		if service_form.is_valid():
			service_model = service_form.save()
			messages.success(request,'Service Successfully Created')
	context = {'service_form':service_form}
	return render(request,'billing_app/service_form.html',context)

def VisitingCardPriceFormPage(request):
	visiting_price_form = VisitingBillForm()
	if request.method == 'POST':
		visiting_price_form = VisitingBillForm(request.POST)
		if visiting_price_form.is_valid():
			visiting_price_model = visiting_price_form.save()
			messages.success(request,'Service Successfully Created')
	context = {'visiting_price_form':visiting_price_form}
	return render(request,'billing_app/visiting_bill_card_price.html',context)

def AssignVisitingCardFormPage(request):
	bill = VisitBill()
	assign_form = AssignVisitingCardForm()
	if request.method == 'POST':
		assign_form = AssignVisitingCardForm(request.POST)
		if assign_form.is_valid():
			bill_detail_model = assign_form.save(commit=False)
			bill_detail_model.bill = bill
#			visit = PatientVisit.objects.get(payment_status='not_paid', patient=bill_detail_model.patient)
			bill.save()
			bill_detail_model.save()
			messages.success(request,'Patient Assigned To Visiting Card')
	context = {'assign_form':assign_form}
	return render(request,'billing_app/assign_visiting_card_form.html',context)

def VisitingCardList(request):
	card_list = VisitBillDetail.objects.filter(selling_price=None)
	context = {'card_list':card_list}
	return render(request,'billing_app/visiting_card_list.html',context)

def GenerateVisitBill(request, bill_id):

	bill = VisitBill()
	visit_bill = VisitBillDetail.objects.get(id=bill_id)
	discount_form = VisitBillDiscountForm(initial={'discount':'No'})
	insurance_form = VisitBillInsuranceForm(initial={'insurance':'No'})

	if request.method == 'POST':
		discount_form = VisitBillDiscountForm(request.POST)
		insurance_form = VisitBillInsuranceForm(request.POST)
		if all([discount_form.is_valid(), insurance_form.is_valid()]):
			bill_detail_model = discount_form.save(commit=False)
			insurance_form = insurance_form.save(commit=False)
			if bill_detail_model.discount == 'Yes':
				visit_bill.selling_price = visit_bill.visiting_card.discounted_price
			else:
				visit_bill.selling_price = visit_bill.visiting_card.visiting_price
			if insurance_form.insurance == 'Yes':
				try:
					patient_insurance = PatientInsurance.objects.get(patient=visit_bill.patient)
					#try:
					excluded_services = InsuranceExcludedService.objects.get(insurance=patient_insurance)
					for service in excluded_services.excluded_service.all():
						print(service,'\n', 'dddd',visit_bill.visiting_card.service)
						if visit_bill.visiting_card.service == excluded_services.excluded_service:
							messages.error(request, 'The Requested Service Is Not Covered By Insurance!')
					#except:
					#	print('No excluded_services!!')
				except:
					messages.error(request, 'Pateint Has No Insurance')
					return redirect('generate_visit_bill', bill_id)
				visit_bill.insurance = 'Yes'
			else:
				visit_bill.insurance = 'No'
			visit_bill.bill = bill			
			visit_bill.registered_on = datetime.now()
			
			bill.save()
			visit_bill.save()
			patient_visit = PatientVisit()
			patient_visit.patient = visit_bill.patient
			patient_visit.visit_status = 'Pending'
			patient_visit.payment_status = 'paid'
			patient_visit.save()
			return redirect('visit_bill_detail', bill_id)
			messages.success(request,'Bill Successfully Generated')

	context = {'discount_form': discount_form, 'insurance_form':insurance_form}
	return render(request,'billing_app/generate_visit_bill.html',context)

def VisitBillDetailPage(request, bill_id):
	visit_bill = VisitBillDetail.objects.get(id=bill_id)
	try:
		patient_insurance = PatientInsurance.objects.get(patient=visit_bill.patient)
						
		excluded_services = InsuranceExcludedService.objects.get(insurance_id=1)
		print(excluded_services.excluded_service)
		for service in excluded_services.excluded_service.all():
			print(service,'\n', 'dddd',visit_bill.visiting_card.service)
			if visit_bill.visiting_card.service == excluded_services.excluded_service:
				messages.error(request, 'The Requested Service Is Not Covered By Insurance!')
	except:
		print('dd')				
	context = {'visit_bill':visit_bill}
	return render(request,'billing_app/visit_bill_detail.html',context)

def PatientInsuranceFormPage(request, patient_id):
	insurance_form = PatientInsuranceForm()
	excluded_form = InsuranceExcludedForm()

	if request.method == 'POST':
		insurance_form = PatientInsuranceForm(request.POST)
		excluded_form = InsuranceExcludedForm(request.POST)		
		if all([insurance_form.is_valid(), excluded_form.is_valid()]) :
			insurance_model = insurance_form.save(commit=False)
			excluded_service_model = excluded_form.save(commit=False)
			insurance_model.patient = Patient.objects.get(id=patient_id)
			insurance_model.save()
			excluded_service_model.insurance = insurance_model
			excluded_service_model.save()
			return redirect('outpatient_list')
			messages.success(request, 'Insurance Information Saved')
	context = {'insurance_form':insurance_form, 'excluded_form':excluded_form}
	return render(request,'billing_app/patient_insurance_form.html',context)

def GiveService(request, patient_id):
	patient = Patient.objects.get(id=patient_id)
	
	qs = ServiceBillDetail.objects.none()
	ServiceBillFormset = modelformset_factory(ServiceBillDetail, form=ServiceForm, extra=0)
	service_bill_formset = ServiceBillFormset(request.POST or None, queryset=qs)
	
#	service_form = ServiceForm()
	if request.method == 'POST':
		service_bill_formset = ServiceBillFormset(request.POST)
		if service_bill_formset.is_valid():
			bill = ServiceBill()
			for form in service_bill_formset:
				service_bill_model = form.save(commit=False)
				
				service_bill_model.bill = bill
				service_bill_model.patient = patient
				print(service_bill_model.patient,'\n')
				bill.save()
				service_bill_model.save()
			messages.success(request, 'Successfully Saved!')

	context = {'service_bill_formset':service_bill_formset}
	return render(request,'billing_app/give_service.html',context)

def ServiceBillList(request):
	service_list = ServiceBillDetail.objects.filter(service_price=None)
	context = {'service_list':service_list}
	return render(request,'billing_app/service_bill_list.html',context)

def GenerateServiceBill(request, bill_id):

	service_bill = ServiceBillDetail.objects.get(id=bill_id)
	service_bill_form = ServiceBillDetailForm()

	if request.method == 'POST':
		service_bill_form = ServiceBillDetailForm(request.POST)
		if service_bill_form.is_valid():
			bill_detail_model = service_bill_form.save(commit=False)
			if bill_detail_model.discount == 'Yes':
				service_bill.service_price = service_bill.service.service_discounted_price
			else:
				service_bill.service_price = service_bill.service.service_price
			if bill_detail_model.insurance == 'Yes':
				try:
					patient_insurance = PatientInsurance.objects.get(patient=service_bill.patient)
					try:
						excluded_services = InsuranceExcludedService.objects.get(insurance=patient_insurance)
						for service in excluded_services.excluded_service.all():
							print(service,'\n', 'dddd',visit_bill.visiting_card.service)
							if visit_bill.visiting_card.service == excluded_services.excluded_service:
								messages.error(request, 'The Requested Service Is Not Covered By Insurance!')
					except:
						print('No excluded_services!!')
				except:
					messages.error(request, 'Pateint Has No Insurance')
					return redirect('generate_service_bill', bill_id)
				try:
					insurance_bills = ServiceBillDetail.objects.filter(patient=service_bill.patient, insurance='Yes')
					insurance_bill_sum_dict = insurance_bills.aggregate(Sum('service_price'))
					insurance_bill_sum = insurance_bill_sum_dict['service_price__sum']
					print('yoo','\n', insurance_bill_sum)
				except:
					print('not wor')
				service_bill.insurance = 'Yes'
			else:
				service_bill.insurance = 'No'
			service_bill.registered_on = datetime.now()
			service_bill.save()
			messages.success(request, 'Successfully Saved!')
	context = {'service_bill_form':service_bill_form}
	return render(request,'billing_app/generate_service_bill.html',context)

def LabTestPriceFormPage(request):
	test_price_form = LabTestPriceForm()
	if request.method == 'POST':
		test_price_form = LabTestPriceForm(request.POST)
		if test_price_form.is_valid():
			test_price_model = test_price_form.save(commit=False)
			test_price_model.effective_date = datetime.now()
			test_price_model.save()
			messages.success(request,'Test Price Successfully Created')
			
	context = {'test_price_form':test_price_form}
	return render(request,'billing_app/lab_test_price_form.html',context)

def LabTestBill(request):
	test_bills = LabBillDetail.objects.filter(test__paid=False)

	context = {'test_bills':test_bills}
	return render(request,'billing_app/lab_test_bill.html',context)
