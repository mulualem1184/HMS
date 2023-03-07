from django.shortcuts import render
from .models import *
from core.models import *
from pharmacy_app.models import *
from django.contrib import messages
from .forms import *
from pharmacy_app.forms import *
from django.shortcuts import redirect
from django.contrib import messages
from datetime import datetime
from datetime import timedelta

from django.forms.models import modelformset_factory
from django.views import View
from dateutil.tz import UTC
from collections import OrderedDict
from pharmacy_app.fusioncharts import FusionCharts

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
				reconcilation.finance_employee = Employee.objects.get(user_profile=request.user)
				reconcilation.debt = debt

			if debt.cash_debt - amount > 1:
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


class Invoices(View):

	def get(self, *args, **kwargs):

		invoices = Invoice.objects.filter(active=True,estimate=False,receipt=False)[::1]


		if self.request.htmx:
			print('HTMX','\n')
			value = self.request.GET.get('last_x_days')
			status_value = self.request.GET.get('status_value')
			if status_value == 'Open':
				invoices = Invoice.objects.filter(paid=False,active=True)
			elif status_value == 'Closed':
				invoices = Invoice.objects.filter(paid=True,active=True)
			else:
				invoices = Invoice.objects.filter(active=True)


			today = datetime.now(UTC)
			if value == None:
				print('')
			elif value == '0':
				invoices = Invoice.objects.filter(active=True)

			else:
				last_x_day = today - timedelta(days=int(value))
				invoices = invoices.filter(registered_on__range=[last_x_day,today],active=True)
			invoices = invoices[::1]
			context2 = {
						'invoices':invoices,
						'invoice_form':InvoiceForm(),
						'payment_form':PaymentForm()

			}
			return render(self.request,'billing_app/partials/htmx/invoice_list_htmx.html', context2)

		context = {'invoices':invoices,
					'invoice_form':InvoiceForm(),
					'payment_form':PaymentForm()
					}

		return render(self.request, 'billing_app/invoices.html',context)

class Payments(View):

	def get(self, *args, **kwargs):

		payments = Payment.objects.all()[::1]
		invoices = Invoice.objects.all()
		if self.request.htmx:
			value = self.request.GET.get('last_x_days')
			status_value = self.request.GET.get('status_value')
			if status_value == 'Open':
				payments = Payment.objects.filter(active=True)
			else:
				payments = Payment.objects.filter(active=True)


			today = datetime.now()
			if value == None:
				print('')
			elif value == '0':
				payments = Payment.objects.filter(active=True)

			else:
				last_x_day = today - timedelta(days=int(value))
				payments = payments.filter(registered_on__range=[last_x_day,today],active=True)

			context2 = {
						'payments':payments,
						'invoices':invoices,
						'invoice_form':InvoiceForm(),
						'prepayment_form':PrePaymentForm()

			}
			return render(self.request,'billing_app/partials/htmx/payment_list_htmx.html', context2)

		context = {'payments':payments,
					'invoices':invoices,
					'invoice_form':InvoiceForm(),
					'prepayment_form':PrePaymentForm()
					}

		return render(self.request, 'billing_app/payments.html',context)


class Receipts(View):

	def get(self, *args, **kwargs):

		receipts = Invoice.objects.filter(due_date__isnull=True)

		context = {'receipts':receipts,
					'invoice_form':InvoiceForm(),
					'payment_form':PaymentForm(),
					}

		return render(self.request, 'billing_app/receipts.html',context)


class Estimates(View):

	def get(self, *args, **kwargs):

		estimates = Invoice.objects.filter(due_date__isnull=True,estimate=True)

		context = {'estimates':estimates,
					'invoice_form':InvoiceForm(),
					'payment_form':PaymentForm(),
					}

		return render(self.request, 'billing_app/estimates.html',context)

class AddInvoice(View):

	def get(self, *args, **kwargs):

		item_sales = ItemSaleInfo.objects.filter(temp_active=True,active=True)

		context = {
					'invoice_form':InvoiceForm(),
					'item_form':ItemSaleInfoForm(),
					'item_sales':item_sales
					}

		return render(self.request, 'billing_app/add_invoice.html',context)


class AddReceipt(View):

	def get(self, *args, **kwargs):

		item_sales = ItemSaleInfo.objects.filter(temp_active=True,active=True)

		context = {
					'receipt': True,
					'invoice_form':InvoiceForm(),
					'item_form':ItemSaleInfoForm(),
					'item_sales':item_sales
					}

		return render(self.request, 'billing_app/add_receipt.html',context)

class AddEstimate(View):

	def get(self, *args, **kwargs):

		item_sales = ItemSaleInfo.objects.filter(temp_active=True,active=True)

		context = {
					'invoice_form':InvoiceForm(),
					'item_form':ItemSaleInfoForm(),
					'item_sales':item_sales
					}

		return render(self.request, 'billing_app/add_estimate.html',context)


class RecievePayment(View):
	def post(self, *args, **kwargs):
		invoice_id = kwargs['invoice_id']
		invoice = Invoice.objects.get(id=invoice_id)
		payment_form = PaymentForm(self.request.POST)
		if payment_form.is_valid():
			payment = payment_form.save(commit=False)
			payment.active = True
			payment.patient = invoice.patient
			payment.registered_on = datetime.now()
			payment.registered_by = Employee.objects.get(user_profile=self.request.user)
			if payment.amount_paid > invoice.unpaid_amount:
				messages.error(self.request, 'Payment Cannot Exceed Invoiced Amount')
				return redirect('invoices')

			reconcilation = InvoiceReconcilation()
			reconcilation.invoice = invoice
			reconcilation.payment = payment
			reconcilation.amount_paid = payment.amount_paid
			reconcilation.registered_on = datetime.now()
			reconcilation.registered_by = Employee.objects.get(user_profile=self.request.user)

			cashier_debt = CashierDebt()
			cashier_debt.cashier = 	Employee.objects.get(user_profile=self.request.user)
			cashier_debt.cash_debt = payment.amount_paid
			cashier_debt.date = datetime.now()
			cashier_debt.save()
			if invoice.unpaid_amount == 0:
				reconcilation.fully_paid = True
				invoice.paid = True
			else:
				print('')

			for info in invoice.item_info.all():
				if info.item.lab_test == None:
					print('')
				else:
					lab_test = LaboratoryTest.objects.filter(test_type=info.item.lab_test)
					for test in lab_test:
						print(test,test,'\n')
						test.paid=True
						test.save()

				info.temp_active = False
				info.save()
			invoice.save()
			payment.save()
			payment.invoice.add(invoice)
			payment.save()
			reconcilation.save()
			messages.success(self.request, 'Payment Successfully Recieved')
			return redirect('invoices')
		else:
			messages.error(self.request, str(payment_form.errors))
			return redirect('invoices')


class ReceivePrePayment(View):
	def post(self, *args, **kwargs):
		payment_form = PrePaymentForm(self.request.POST)
		if payment_form.is_valid():
			payment = payment_form.save(commit=False)
			payment.active = True
			payment.pre_payment = True
			payment.registered_on = datetime.now()
			payment.registered_by = Employee.objects.get(user_profile=self.request.user)
			payment.save()
			messages.success(self.request, 'Pre Payment Successfully Recieved')
			return redirect('payments')
		else:
			messages.error(self.request, str(payment_form.errors))
			return redirect('payments')



class ReconcileInvoices(View):
	def post(self, *args, **kwargs):
		#payment_id = kwargs['payment_id']
		#payment = Payment.objects.get(id=payment_id)
		invoice_ids = [int(id) for id in self.request.POST.getlist('invoices')]
		payment_ids = [int(id) for id in self.request.POST.getlist('payments')]
		payments = []
		invoices = []
		for invoice_id in invoice_ids:
			invoices.append(Invoice.objects.get(id=invoice_id))
		for payment_id in payment_ids:
			payments.append(Payment.objects.get(id=payment_id))

		#invoices = self.request.POST.getlist('invoices')
		#payments = self.request.POST.getlist('payments')
		patient_array = []
		count = 0
		for invoice in invoices:
			print('patient: i',invoice)
			if invoice.patient in patient_array:
				if count > 1:
					messages.error(self.request, "Cannot Recoincile Invoice And Payment With Different Patient")
					return redirect('payments')
				else:
					print('')
			else:
				patient_array.append(invoice.patient)
				count += 1
		for payment  in payments:
			if count > 1:
				messages.error(self.request, "Cannot Recoincile Invoice And Payment With Different Patient")
				return redirect('payments')

			if payment.patient in patient_array:
					print('')

			else:
				patient_array.append(payment.patient)
				count += 1

		if count > 1:
			messages.error(self.request, "Cannot Recoincile Invoice And Payment With Different Patient")
			return redirect('payments')

		for invoice in invoices:
			for payment in payments:			
				if invoice.unpaid_amount > 0:
					if payment.remaining_amount > 0:
						print('')
					else:
						messages.error(self.request, str(invoice)+"Cannot be Reconciled Due To Insufficient Funds")
						return redirect('payments')
					print('remaining: ',payment.remaining_amount,'\n')
					print('unpaid: ',invoice.unpaid_amount,'\n')
					if payment.remaining_amount > invoice.unpaid_amount:
						print('hererere')
						reconcilation = InvoiceReconcilation()
						reconcilation.invoice = invoice
						reconcilation.payment = payment
						print('unpaid: ',invoice.unpaid_amount,'\n')
						reconcilation.amount_paid = invoice.unpaid_amount
						reconcilation.registered_on = datetime.now()
						reconcilation.registered_by = Employee.objects.get(user_profile=self.request.user)
						reconcilation.fully_paid = True
						invoice.paid = True
						payment.invoice.add(invoice)
						payment.save()
						invoice.save()
					else:
						reconcilation = InvoiceReconcilation()
						reconcilation.invoice = invoice
						reconcilation.payment = payment
						reconcilation.amount_paid = payment.remaining_amount
						reconcilation.registered_on = datetime.now()
						reconcilation.registered_by = Employee.objects.get(user_profile=self.request.user)
						payment.invoice.add(invoice)
						payment.save()

					reconcilation.save()

			messages.success(self.request, 'Invoices Successfully Reconciled!')
			return redirect('invoices')

class EditInvoice(View):

	def get(self, *args, **kwargs):

		item_sales = ItemSaleInfo.objects.filter(temp_active=True,active=True)
		patient_id = kwargs['patient_id']
		patient = Patient.objects.get(id=patient_id)
		invoice_form = InvoiceForm(initial={'patient':patient})
		context = {
					'invoice_form':invoice_form,
					'item_form':ItemSaleInfoForm(),
					'item_sales':item_sales,
					'patient':patient,
					'edit':True,
					}

		return render(self.request, 'billing_app/add_invoice.html',context)


class EditEstimate(View):

	def get(self, *args, **kwargs):

		item_sales = ItemSaleInfo.objects.filter(temp_active=True,active=True)
		patient_id = kwargs['patient_id']
		patient = Patient.objects.get(id=patient_id)
		invoice_form = InvoiceForm(initial={'patient':patient})
		context = {
					'invoice_form':invoice_form,
					'item_form':ItemSaleInfoForm(),
					'item_sales':item_sales,
					'patient':patient,
					'edit':True,
					}

		return render(self.request, 'billing_app/add_estimate.html',context)

class ConvertEstimateToInvoice(View):

	def get(self, *args, **kwargs):

		invoice_id = kwargs['invoice_id']
		estimate = Invoice.objects.get(id=invoice_id)
		estimate.estimate = False
		estimate.save()
		messages.success(self.request, "Successfully Converted")
		return redirect('add_invoice')

		return redirect('estimates')

class EditInvoice2(View):

	def get(self, *args, **kwargs):

		invoice_id = kwargs['invoice_id']

		invoice = Invoice.objects.get(id=invoice_id)
		invoice_form = InvoiceForm(initial={'patient':invoice.patient})
		context = {'invoice':invoice,
					'invoice_form':invoice_form,
					'item_form':ItemSaleInfoForm(),
					'patient':invoice.patient,
					'edit':True,
					}

		return render(self.request, 'billing_app/edit_invoice2.html',context)

class EditReceipt(View):

	def get(self, *args, **kwargs):
		item_sales = ItemSaleInfo.objects.filter(temp_active=True,active=True)
		patient_id = kwargs['patient_id']
		patient = Patient.objects.get(id=patient_id)
		invoice_form = InvoiceForm(initial={'patient':patient})
		context = {
					'invoice_form':invoice_form,
					'item_form':ItemSaleInfoForm(),
					'item_sales':item_sales,
					'patient':patient,
					'receipt':True,
					'edit':True
					}

		return render(self.request, 'billing_app/add_receipt.html',context)


class AddItemSaleInfo(View):

	def post(self, *args, **kwargs):
		url_arg = kwargs['url_arg']

		invoice_form = InvoiceForm(self.request.POST)
		item_form = ItemSaleInfoForm(self.request.POST)
		if invoice_form.is_valid():
			if item_form.is_valid():
				item_sale_info = item_form.save(commit=False)
				invoice_form = invoice_form.save(commit=False)
				item_sale_info.temp_active = True
				item_sale_info.active = True
				item_sale_info.save()
				if url_arg == 'R':
					return redirect('edit_receipt',invoice_form.patient.id)
				elif url_arg == 'E':
					return redirect('edit_estimate',invoice_form.patient.id)

				else:
					return redirect('edit_invoice',invoice_form.patient.id)
			else:
				messages.error(self.request, str(item_form.errors))
				return redirect('add_invoice')
		else:
			messages.error(self.request, str(invoice_form.errors))
			return redirect('add_invoice')




class DeleteItemSaleInfo(View):

	def get(self, *args, **kwargs):

		patient_id = kwargs['patient_id']
		item_info_id = kwargs['item_info_id']
		item_info = ItemSaleInfo.objects.get(id=item_info_id)
		item_info.active = False
		item_info.save()
		messages.success(self.request, "Successfully Deleted!")
		return redirect('edit_invoice',patient_id)

class SaveInvoice(View):
	def post(self, *args, **kwargs):
		patient_id = kwargs['patient_id']
		patient = Patient.objects.get(id=patient_id)
		due_date = datetime.strptime(self.request.POST.get('due_date') or str(datetime.now().date()),  '%Y%m%d')
		item_sale_list = self.request.POST.getlist('item_sales')
		for item_sale in item_sale_list:
			print(item_sale,'\n')		
		invoice_form = Invoice()
		invoice_form.active = True
		invoice_form.patient = patient
		invoice_form.due_date = due_date
		invoice_form.registered_on = datetime.now()
		invoice_form.registered_by = Employee.objects.get(user_profile=self.request.user)


		invoice_form.save()
		for item_sale in item_sale_list:
			invoice_form.item_info.add(item_sale)
			sale_info = ItemSaleInfo.objects.get(id=int(item_sale))
			sale_info.temp_active = False
			sale_info.save()
		invoice_form.save()
		return redirect('invoices')


class SaveReceipt(View):
	def post(self, *args, **kwargs):
		patient_id = kwargs['patient_id']
		patient = Patient.objects.get(id=patient_id)
		item_sale_list = self.request.POST.getlist('item_sales')
		for item_sale in item_sale_list:
			print(item_sale,'\n')		
		invoice_form = Invoice()
		invoice_form.active = True
		invoice_form.patient = patient
		invoice_form.receipt = True
		invoice_form.registered_on = datetime.now()
		invoice_form.registered_by = Employee.objects.get(user_profile=self.request.user)
		invoice_form.save()
		for item_sale in item_sale_list:
			invoice_form.item_info.add(item_sale)
		invoice_form.save()
		return redirect('receipts')


class SaveEstimate(View):
	def post(self, *args, **kwargs):
		patient_id = kwargs['patient_id']
		patient = Patient.objects.get(id=patient_id)
		item_sale_list = self.request.POST.getlist('item_sales')
		for item_sale in item_sale_list:
			print(item_sale,'\n')		
		invoice_form = Invoice()
		invoice_form.active = True
		invoice_form.patient = patient
		invoice_form.estimate = True
		invoice_form.registered_on = datetime.now()
		invoice_form.registered_by = Employee.objects.get(user_profile=self.request.user)
		invoice_form.save()
		for item_sale in item_sale_list:
			invoice_form.item_info.add(item_sale)
		invoice_form.save()
		return redirect('estimates')

class Items(View):

	def get(self, *args, **kwargs):
		search_consultation = self.request.GET.get('searchconsultation',None)

		items = Item.objects.all()
		item_form = CreateItemForm()
		price_form = ItemPriceForm()
		print('\n','\n','ssesees: ',search_consultation,'\n')
		if search_consultation == None:
			print('')
		else:
			items = items.filter(name__icontains=search_consultation)
		associate_form = AssociateItemForm()
		associate_form.fields["drug"].queryset = Item.objects.first().return_unassociated_drugs
		associate_form.fields["lab_test"].queryset = Item.objects.first().return_unassociated_lab_tests

		context = {
					'items':items,
					'item_form':item_form,
					'price_form':price_form,
					'associate_form':associate_form,

					}

		return render(self.request, 'billing_app/items.html',context)


class AssociateDrugItem(View):

	def post(self, *args, **kwargs):

		associate_form = AssociateItemForm(self.request.POST)
		if associate_form.is_valid():
			drug = associate_form.save(commit=False)
			price.registered_on = datetime.now()
			price.registered_by = Employee.objects.get(user_profile=self.request.user)
			item.price_info = price
			item.active = True
			item.registered_on = datetime.now()
			item.registered_by = Employee.objects.get(user_profile=self.request.user)
			price.save()
			item.save()

			if item.medical_type == '2':
				return redirect('create_drug',item.id)
			elif item.medical_type == '6':
				return redirect('create_lab_test_item',item.id)
			else:
				return redirect('items')
		else:
			messages.error(self.request, str(item_form.errors))
			return redirect('items')

class CreateItem(View):

	def post(self, *args, **kwargs):

		item_form = CreateItemForm(self.request.POST)
		price_form = ItemPriceForm(self.request.POST)
		if item_form.is_valid():
			if price_form.is_valid():
				item = item_form.save(commit=False)
				price = price_form.save(commit=False)
				if price.discount_price:
					if price.sale_price < price.discount_price:
						messages.error(self.request, "Discount Price Cannot Exceed Sale Price")
						return redirect('items')
				if price.buy_price:
					if price.sale_price < price.buy_price:
						messages.error(self.request, "Discount Price Cannot Exceed Sale Price")
						return redirect('items')

				price.active= True
				price.registered_on = datetime.now()
				price.registered_by = Employee.objects.get(user_profile=self.request.user)
				item.price_info = price
				item.active = True
				item.registered_on = datetime.now()
				item.registered_by = Employee.objects.get(user_profile=self.request.user)
				price.save()
				item.save()

				if item.medical_type == '2':
					return redirect('create_drug',item.id)
				elif item.medical_type == '6':
					return redirect('create_lab_test_item',item.id)
				else:
					return redirect('items')
			else:
				messages.error(self.request, str(price_form.errors))
				return redirect('items')
		else:
			messages.error(self.request, str(item_form.errors))
			return redirect('items')


class AssociateDrugItem(View):

	def post(self, *args, **kwargs):
		item_id = kwargs['item_id']
		item = Item.objects.get(id=item_id)
		associate_form = AssociateItemForm(self.request.POST)
		if associate_form.is_valid():
			associate = associate_form.save(commit=False)
			item.drug = associate.drug 
			item.save()
			messages.success(self.request,'Drug Successfully Created!')
			return redirect('items')

		else:
			messages.error(self.request, str(item_form.errors))
			return redirect('items')

class CreateDrug(View):

	def get(self, *args, **kwargs):
		item_id = kwargs['item_id']
		item = Item.objects.get(id=item_id)
		drug_profile_form = DrugProfileForm(initial={'commercial_name':item.name,'generic_name':item.generic_name})
		route_form = RouteForm()
		dosage_model_form = DosageForm()

		context = {
					'item':item,
					'drug_profile_form':drug_profile_form,
					'route_form':route_form,
					'dosage_model_form':dosage_model_form,

					}
		return render(self.request, 'pharmacy_app/create_drug.html',context)

	def post(self, *args, **kwargs):
		item_id = kwargs['item_id']
		item = Item.objects.get(id=item_id)
	
		drug_profile_form = DrugProfileForm(self.request.POST)
		route_form = RouteForm(self.request.POST)
		dosage_model_form = DosageForm(self.request.POST)


		drug_profile_form= DrugProfileForm(self.request.POST)
		if drug_profile_form.is_valid():
			drug_profile_model = drug_profile_form.save(commit=False)
			drug_profile_model.registered_by = self.request.user
			drug_profile_model.save()
		else:
			print('drug profile form error', drug_profile_form.errors)
		
		route_form = RouteForm(self.request.POST)
		if route_form.is_valid():
			route_model = route_form.save(commit=False)
			route_model.drug = drug_profile_model
			route_model.registered_by = self.request.user
			route_model.save()
		else:
			print('route form error', route_form.errors)
		
		dosage_model_form = DosageForm(self.request.POST)
		if dosage_model_form.is_valid():
			dosage_model = dosage_model_form.save(commit=False)
			dosage_model.drug = route_model
			item.drug = dosage_model
			dosage_model.save()
			item.save()
			messages.success(self.request,'Drug Successfully Created!')
			return redirect('items')
		else:
			print('dosage error is' , dosage_model_form.errors)
			messages.error(self.request,str(dosage_model_form.errors))
		context = {
					'items':items,
					'item_form':item_form,
					'price_form':price_form,

					}

		return render(self.request, 'billing_app/create_drug.html',context)


class BillingDashboard(View):

	def get(self, *args, **kwargs):
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

		day = datetime.now()
		this_month = (datetime.now() - timedelta(days=60)).month  
		last_month = (datetime.now() - timedelta(days=90)).month
		print(this_month)
		print(last_month)
		
		
		before_date = day - timedelta(days=100)
		patient_array = []
		billable_patients = BillableItem.objects.filter(registered_on__range=[before_date,day],active=True)
		billable_patients1 = []
		for b in billable_patients:
			if b.patient in billable_patients1:
				print('')
			else:
				billable_patients1.append(b.patient)
		print(billable_patients1)
		invoices = Invoice.objects.filter(registered_on__range=[before_date,day])
		payments = Payment.objects.filter(registered_on__range=[before_date,day])
		receipts = Invoice.objects.filter(registered_on__range=[before_date,day],receipt=True)
		paid_invoice = invoices.filter(paid=True).count()
		not_paid_invoice = invoices.filter(paid=False).count()
		payment_count = receipts.count() + payments.count()


		month_array = []
		credit_array = []
		debit_array = []
		balance_array = []

		credit = 0
		debit = 0
		for invoice in invoices:
			if invoice.registered_on.month == 12:
				print('come here')
				month_str = str(invoice.registered_on.year) + "  " + str(invoice.registered_on.month)
				if month_str in month_array:
					print('k')
				else:
					credit = 0
					month_array.append(month_str)
					invoice_list = Invoice.objects.filter(registered_on__month=12)
					for invoice in invoice_list:
						credit += invoice.total_amount
					credit_array.append(credit)
					print('credit: ', credit,'\n')

					debit = 0
					payment_list = Payment.objects.filter(registered_on__month=12)
					for payment in payment_list:
						debit += payment.amount_paid
					debit_array.append(debit)
					balance_array.append(debit - credit) 

		sold_items = ItemSaleInfo.objects.filter(active=True)
		item_count = sold_items.values('item').distinct().count()
		balance_zip = zip(month_array,debit_array,credit_array,balance_array)

		context = {'billable_patients': billable_patients,
					'billable_patients1':billable_patients1,

					'invoices':invoices,
					'payments':payments,
					'receipts':receipts,
					'paid_invoice':paid_invoice,
					'not_paid_invoice':not_paid_invoice,
					'payment_count':payment_count,

					'balance_zip':balance_zip,
					'debit':debit,
					'credit':credit,
					'balance':debit - credit,
					'sold_items':sold_items,
					'item_count':item_count,

					}

		return render(self.request, 'billing_app/billing_dashboard.html',context)


class PatientBilling(View):

	def get(self, *args, **kwargs):
		patient_id = kwargs['patient_id']
		patient = Patient.objects.get(id=patient_id)
		this_month = datetime.now().month
		last_month = (datetime.now() - timedelta(days=30)).month

		day = datetime.now()
		
		before_date = day - timedelta(days=7)

		billable_patients = BillableItem.objects.filter(registered_on__range=[before_date,day],active=True)
		invoices = Invoice.objects.filter(registered_on__range=[before_date,day],patient=patient)
		payments = Payment.objects.filter(registered_on__range=[before_date,day],patient=patient)
		receipts = Invoice.objects.filter(registered_on__range=[before_date,day],receipt=True,patient=patient)
		paid_invoice = invoices.filter(paid=True).count()
		not_paid_invoice = invoices.filter(paid=False).count()
		payment_count = receipts.count() + payments.count()

		month_array = []
		credit_array = []
		debit_array = []
		balance_array = []

		credit = 0
		debit = 0
		for invoice in invoices:
			if invoice.registered_on.month == this_month:
				month_str = str(invoice.registered_on.year) + " - " + str(invoice.registered_on.month)
				if month_str in month_array:
					print('k')
				else:
					credit = 0
					month_array.append(month_str)
					invoice_list = Invoice.objects.filter(registered_on__month=this_month,patient=patient)
					for invoice in invoice_list:
						credit += invoice.total_amount
					credit_array.append(credit)
					debit = 0
					payment_list = Payment.objects.filter(registered_on__month=this_month,patient=patient)
					for payment in payment_list:
						debit += payment.amount_paid
					debit_array.append(debit)
					balance_array.append(debit - credit) 

		sold_items = ItemSaleInfo.objects.filter(active=True)
		item_count = sold_items.values('item').distinct().count()

		balance_zip = zip(month_array,debit_array,credit_array,balance_array)

		lab_items = Item.objects.filter(medical_type='6')
		type_array = []
		for lab in lab_items:
			if lab.lab_test in type_array:
				print('')
			else:
				type_array.append(lab.lab_test)
		order_list = Order.objects.all()
		unpaid_orders_array = []
		for order in order_list:
			unpaid_orders = order.test_set.filter(paid=False)
			if unpaid_orders:
				for u in unpaid_orders:
					#print(u,'\n')
					if u.order not in unpaid_orders_array:
						unpaid_orders_array.append(u.order)

		context = {'billable_items': billable_patients,
					'invoices':invoices,
					'payments':payments,
					'receipts':receipts,
					'paid_invoice':paid_invoice,
					'not_paid_invoice':not_paid_invoice,
					'payment_count':payment_count,
					'patient':patient,
					'payment_form':PaymentForm(),
					'invoice_form':InvoiceForm(),
					'prepayment_form':PrePaymentForm(),
					'balance_zip':balance_zip,
					'debit':debit,
					'credit':credit,
					'balance':debit - credit,
					'sold_items':sold_items,
					'item_count':item_count,
					'unpaid_orders_array':unpaid_orders_array,
					'type_array':type_array,

					}

		return render(self.request, 'billing_app/patient_billing.html',context)

class PrepareBillableItem(View):
	def post(self, *args, **kwargs):
		patient_id = kwargs['patient_id']
		patient = Patient.objects.get(id=patient_id)
		item_list = self.request.POST.getlist('items')
		item_ids = [int(id) for id in self.request.POST.getlist('items')]
		item_list = []
		for invoice_id in item_ids:
			item_list.append(BillableItem.objects.get(id=invoice_id))

		for item in item_list:
			print(item,'\n')
			print(item.item,'\n')
			item_sale_info = ItemSaleInfo()
			item_sale_info.item = item.item
			item_sale_info.quantity = 1
			item_sale_info.temp_active = True
			item_sale_info.active = True
			item.active=False
			item.save()
			item_sale_info.save()
		return redirect('edit_invoice', patient_id)


