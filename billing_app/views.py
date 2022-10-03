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
	service_list = Service.objects.all()
	visiting_card_list = VisitingCardPrice.objects.all()
	service_form = CreateServiceForm()
	visiting_price_form = VisitingBillForm()

	if request.method == 'POST':
		service_form = CreateServiceForm(request.POST)
		if service_form.is_valid():
			service_model = service_form.save()
			messages.success(request,'Service Successfully Created')
			return redirect('service_form')
	context = {'service_form':service_form,
				'service_list':service_list,
				'visiting_card_list':visiting_card_list,
				'visit_form':visiting_price_form,
	}
	return render(request,'billing_app/service_form.html',context)

def CreateVisitingCard(request):
	if request.method == 'POST':
		visiting_price_form = VisitingBillForm(request.POST)
		if visiting_price_form.is_valid():
			visiting_price_model = visiting_price_form.save()
			messages.success(request,'Service Successfully Created')
			return redirect('service_form')
		else:
			messages.error(request,visiting_price_form.errors)
			return redirect('service_form')

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
	patient = visit_bill.patient
	#discount_form = VisitBillDiscountForm(initial={'discount':'No'})
	#insurance_form = VisitBillInsuranceForm(initial={'insurance':'No'})
	visit_bill_detail = VisitBillDetail.objects.get(id=bill_id)
	visit_bill_detail.selling_price = visit_bill_detail.visiting_card.visiting_price
	#service_team = ServiceTeam.objects.filter(service__id=service_recieved).first()
	#service_room_provider = ServiceRoomProvider.objects.filter(service_team=service_team.team).last()

	#service_room_provider = ServiceRoomProvider.objects.filter(service_team=visit_bill_detail.visiting_card.service.service_team.team).last()
	#room = service_room_provider.room
	"""
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
	"""
	if visit_bill_detail.free== True:
		visit_bill_detail.selling_price = 0	

	#bill.save()
	patient_visit = PatientVisit.objects.get(visit_status = 'Pending', payment_status='not_paid', patient=patient)
	patient_visit.payment_status = 'paid'

	visit_bill_detail.registered_by = Employee.objects.get(user_profile=request.user, designation__name='Cashier')
	today = datetime.today()
	#today = now.day
	if CashierDebt.objects.filter(cashier__user_profile=request.user, reconciled=False, debt_date=today).last():
		cashier_debt = CashierDebt.objects.get(cashier__user_profile=request.user, reconciled=False, debt_date=today)
		cashier_debt.cash_debt = cashier_debt.cash_debt + visit_bill_detail.selling_price 
	else:
		cashier_debt = CashierDebt()
		cashier_debt.cashier = 	Employee.objects.get(user_profile=request.user, designation__name='Cashier')
		cashier_debt.cash_debt = visit_bill_detail.selling_price 
		cashier_debt.date = today

	cashier_debt.save()
	visit_bill_detail.save()
	patient_visit.save()
#	patient_visit_model.save()
	try:
		room_queue = VisitQueue.objects.filter(visit__service_room=patient_visit_model.service_room, visit__visit_status='Pending')
		last_visit_queue = room_queue.last()
		print(last_visit_queue.queue_number)
		"""
		last_visit_queue = VisitQueue.objects.last()
		"""
		new_visit_queue = VisitQueue()
		new_visit_queue.visit = patient_visit
		new_visit_queue.queue_number = last_visit_queue.queue_number + 1
		#new_visit_queue.visit.visit_status = 'Pending'
		new_visit_queue.visit.save()
		new_visit_queue.save()
		messages.success(request, 'Successfully Assigned!')
#				return redirect('assign_patient')

	except:
		new_visit_queue = VisitQueue()
		new_visit_queue.visit = patient_visit
		new_visit_queue.queue_number = 1
#				new_visit_queue.visit.visit_status = 'Pending'
		new_visit_queue.visit.save()
		new_visit_queue.save()
		messages.success(request, 'Successfully Assigned!')
#				return redirect('assign_patient')			

		return redirect('visit_bill_detail', bill_id)
		messages.success(request,'Bill Successfully Generated')

#	context = {'discount_form': discount_form, 'insurance_form':insurance_form}
#	return render(request,'billing_app/generate_visit_bill.html',context)

def LabOrderList(request):
	order_list = Order.objects.all()
	unpaid_orders_array = []
	for order in order_list:
		unpaid_orders = order.test_set.filter(paid=False)
		if unpaid_orders:
			for u in unpaid_orders:
				#print(u,'\n')
				if u.order not in unpaid_orders_array:
					unpaid_orders_array.append(u.order)
	for u in unpaid_orders_array:

		print(u.priority,'\n')
	context = {'unpaid_orders_array':unpaid_orders_array}
	return render(request,'billing_app/lab_order_list.html',context)

def ViewLabOrderDetail(request, order_id):
	order = Order.objects.get(id=order_id)
	test_types = order.test_set.all()
	context = {'test_types':test_types}
	return render(request,'billing_app/view_lab_order_detail.html',context)

def MarkLabTestAsPaid(request, test_id):
	test = LaboratoryTest.objects.get(id=test_id)
	lab_bill = LabBillDetail()
	lab_bill.test = test.test_type
	lab_bill.test_price=LaboratoryTestPrice.objects.get(test_type=test.test_type,active=True)
	lab_bill.patient = test.order.patient
	lab_bill.registered_on = datetime.now()
	lab_bill.registered_by = Employee.objects.get(user_profile=request.user, designation__name='Cashier')
	today = datetime.today()
	#today = now.day
	if CashierDebt.objects.filter(cashier__user_profile=request.user, reconciled=False, debt_date=today).last():
		cashier_debt = CashierDebt.objects.get(cashier__user_profile=request.user, reconciled=False,debt_date=today) 
		cashier_debt.cash_debt = cashier_debt.cash_debt + lab_bill.test_price.price 
	else:
		cashier_debt = CashierDebt()
		cashier_debt.cashier = 	Employee.objects.get(user_profile=request.user, designation__name='Cashier')
		cashier_debt.cash_debt = lab_bill.test_price.price 
		cashier_debt.date = today
	payment_status = PatientPaymentStatus.objects.get(patient=test.order.patient, active=True)
	if payment_status.payment_status == 'Free':
		lab_bill.discount = False
		lab_bill.insurance = False
		lab_bill.credit = False
		lab_bill.free = True
	elif payment_status.payment_status == 'Insurance':
		lab_bill.discount = False
		lab_bill.free = False
		lab_bill.credit = False
		lab_bill.insurance = True		
	elif payment_status.payment_status == 'Credit':
		lab_bill.discount = False
		lab_bill.free = False
		lab_bill.credit = False
		lab_bill.insurance = True		
	elif payment_status.payment_status == 'Discount':
		lab_bill.discount = True
		lab_bill.free = False
		lab_bill.credit = False
		lab_bill.insurance = False
	else:
		lab_bill.discount = False
		lab_bill.free = False
		lab_bill.credit = False
		lab_bill.insurance = False
	bed = Bed.objects.first()
	allocated_patients = bed.return_ward_patients	
	for p in allocated_patients:
		print('\n',p)
	if lab_bill.patient in allocated_patients:
		lab_bill.department = 'Inpatient'
	else:
		lab_bill.department = 'Outpatient'
	test.paid = True
	cashier_debt.save()
	test.save()
	lab_bill.save()
	messages.success(request,'Bill Generated Successfully!')
	return redirect('view_lab_order_detail', test.order.id)
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

def CashierList(request):
	cashier_list = []

	#cashier_list = LabBillDetail.objects.filter(test__paid=False)
	for debt in CashierDebt.objects.filter(reconciled=False):
		if debt.cashier not in cashier_list:
			cashier_list.append(debt.cashier)

	#Employee.objects.get(user_profile=request.user, designation__name='Cashier')

	context = {'cashier_list':cashier_list}
	return render(request,'billing_app/cashier_list.html',context)

def CashierDebtList(request, cashier_id):

	debt_list = CashierDebt.objects.filter(cashier__id=cashier_id, reconciled=False)	
	#cashier_list = LabBillDetail.objects.filter(test__paid=False)

	#Employee.objects.get(user_profile=request.user, designation__name='Cashier')

	context = {'debt_list':debt_list}
	return render(request,'billing_app/cashier_debt_list.html',context)

def ReconcileFullDebt(request, debt_id):

	debt = CashierDebt.objects.get(id=debt_id)	
	#cashier_list = LabBillDetail.objects.filter(test__paid=False)
	debt.reconciled =True
	reconcilation = CashierReconcilation()
	reconcilation.finance_employee = Employee.objects.get(user_profile=request.user, designation__name='Finance Personnel')
	reconcilation.debt = debt
	reconcilation.remaining_amount = 0
	reconcilation.registered_on = datetime.now()

	debt.save()
	reconcilation.save()
	#Employee.objects.get(user_profile=request.user, designation__name='Cashier')
	messages.success(request,'Successful!')
	return redirect('cashier_debt_list', debt.cashier.id)

def PartialReconcilation(request, debt_id):

	debt = CashierDebt.objects.get(id=debt_id, reconciled=False)	
	#cashier_list = LabBillDetail.objects.filter(test__paid=False)
	try:
		reconcilation2 = CashierReconcilation.objects.get(debt=debt)
	except:
		reconcilation2 = None

	rec_form = PartialReconcilationForm()
	#Employee.objects.get(user_profile=request.user, designation__name='Cashier')

	if request.method == 'POST':
		rec_form = PartialReconcilationForm(request.POST)
		if rec_form.is_valid():
			#print(inventory_structure_form.data['stock'])
			amount = int(rec_form.data['amount_paid'])
			#shelf_amount =int( rec_form.data['shelf_amount'])
			try:
				reconcilation = CashierReconcilation.objects.get(debt=debt)
			except:
				reconcilation = CashierReconcilation()
				reconcilation.finance_employee = Employee.objects.get(user_profile=request.user, designation__name='Finance Personnel')
				reconcilation.debt = debt

			if debt.cash_debt - amount > -1:
				if reconcilation.remaining_amount:
					if reconcilation.remaining_amount - amount <0:
						messages.error(request,"Paid Amount Cannot Exceed Debt!")
						return redirect('partial_reconcilation', debt.id)
					else:
						reconcilation.remaining_amount = reconcilation.remaining_amount - amount
						reconcilation.registered_on = datetime.now()
						reconcilation.save()
					
				else:
					reconcilation.remaining_amount = debt.cash_debt - amount
					reconcilation.registered_on = datetime.now()
					reconcilation.save()
			elif debt.cash_debt - amount<0:
				messages.error(request,"Paid Amount Cannot Exceed Debt!")
				return redirect('partial_reconcilation', debt.id)

			if reconcilation.remaining_amount  == 0:
				debt.reconciled = True
				debt.save()
				messages.success(request,"Successfully Reconciled!")
				return redirect('cashier_debt_list', debt.cashier.id)
			return redirect('partial_reconcilation',debt.id)
	context = {'debt':debt,
				'rec_form':rec_form,
				'reconcilation2':reconcilation2

	}
	return render(request,'billing_app/partial_reconcilation_form.html',context)
