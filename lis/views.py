from typing import Sequence
from datetime import datetime

from django import forms
from django.contrib import messages
from django.contrib.auth import get_user
from django.contrib.auth.decorators import login_required
from django.db.models.query import QuerySet
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from notification.models import notify
from .utils import GeneralReport

from .forms import (LaboratoryTestForm, LabTestResultTypeForm, LabTestTypeForm, NormalRangeForm,
					OrderForm, ReferredTestResultForm, ResultEntryForm,
					SampleTypeForm, SpecimenForm,SelectTestForm,EditSpecimenForm,
					LaboratorySectionForm)
from .models import (LaboratorySection, LaboratoryTest, LaboratoryTestResult,
					 LaboratoryTestResultType, LaboratoryTestType, NormalRange,
					 Order, Patient, ReferredTestResult, Specimen,
					 TestResultChoice, Laboratory, LabEmployee, )
from outpatient_app.models import PatientVisit, OutpatientLabResult
from inpatient_app.fusioncharts import FusionCharts
from billing_app.models import Item,BillableItem

from staff_mgmt.models import Employee
from datetime import timedelta
from collections import OrderedDict

@method_decorator(login_required, 'dispatch')
class CreateOrder(View):
	# creates laboratory orders
	# requires authenticated user

	def __init__(self, *args, **kwargs) -> None:
		self.TestFormSet = modelformset_factory(LaboratoryTest, LaboratoryTestForm, extra=1)
		super().__init__(*args, **kwargs)
	
	def get(self, *args, **kwargs):
		# returns a form to create order,
		# tests that belong to that order are selected from table
		order_form = OrderForm()
		return render(self.request, 'lis/create_order.html', {
			'order_form': order_form,
			'test_type_set': LaboratoryTestType.objects.all(),
			'lab_sections': LaboratorySection.objects.all(),
			'active_link': 'lab',
		})

	def post(self, *args, **kwargs):
		# gets the id of selected test types from POST data, 
		# if no test is selected sends error messages and redirect to create-order
		# checks if OrderForm is valid, if it's saves order and 
		# adds selected test types to that order
		order_form = OrderForm(self.request.POST)
		test_type_list = [int(id) for id in self.request.POST.getlist('tests')]
		if not test_type_list:
			messages.error(self.request, "Atleast one test should be selected.")
			return redirect('create-order')
		if order_form.is_valid():
			order: Order = order_form.save(commit=False)
			order.ordered_by = get_user(self.request)
			order.save()
			for test_id in test_type_list:
				test = LaboratoryTest()
				test_type = LaboratoryTestType.objects.get(id=test_id)
				test.test_type = test_type
				# read special inst from request
				spec_inst = self.request.POST.get(f'special_inst_for_{test_id}', None)
				test.special_instructions = spec_inst
				test.order = order
				test.save()
				try:
					item = Item.objects.get(lab_test=test_type)
					print('item: ',item,'\n')
					billable_item =BillableItem()
					billable_item.item = item
					billable_item.patient = patient
					billable_item.active = True
					billable_item.registered_on = datetime.now()
					billable_item.save()
				except Exception as e:
					raise e
			order.save()
		return redirect('core:add_lab_request')


@method_decorator(login_required, 'dispatch')
class OrderForPatient(View):

	def get(self, *args, **kwargs):
		# generates OrderForm for the given patient_id
		# returns order_form and patient object
		order_form = OrderForm()
		order_form.fields.pop('patient_id')
		patient_id = kwargs['patient_id']
		patient = Patient.objects.get(id=patient_id)
		return render(self.request, 'lis/order_for_patient.html', {
			'patient': patient,
			'order_form': order_form,
			'test_type_set': LaboratoryTestType.objects.all(),
			'lab_sections': LaboratorySection.objects.all(),
			'active_link': 'lab',
		})

	def post(self, *args, **kwargs):
		# gets the id of selected test types from POST data, 
		# if no test is selected sends error messages and redirect to create-order
		# checks if OrderForm is valid, if it's saves order and 
		# adds selected test types to that order
		patient_id = kwargs['patient_id']
		patient = Patient.objects.get(id=patient_id)
		order_form = OrderForm(self.request.POST)
		order_form.fields.pop('patient_id') # remove patient id field since patient id is given in the url
		test_type_list = [int(id) for id in self.request.POST.getlist('tests')]
		if not test_type_list:
			messages.error(self.request, "Atleast one test should be selected.")
			return redirect('order-for-patient')
		if order_form.is_valid():
			order: Order = order_form.save(commit=False)
			order.patient = patient
			order.ordered_by = Employee.objects.get(user_profile=self.request.user)
			order.save()
			for test_id in test_type_list:
				test:LaboratoryTest = LaboratoryTest()
				test_type = LaboratoryTestType.objects.get(id=test_id)
				test.test_type = test_type
				# read special inst from request
				spec_inst = self.request.POST.get(f'special_inst_for_{test_id}', '')
				test.special_instructions = spec_inst
				test.order = order
				test.save()
				try:
					item = Item.objects.get(lab_test=test_type)
					print('item: ',item,'\n')
					billable_item =BillableItem()
					billable_item.item = item
					billable_item.patient = patient
					billable_item.active = True
					billable_item.registered_on = datetime.now()
					billable_item.save()
				except:
					print('')
			order.save()
			messages.success(self.request, "Order created successfully!")
			return redirect('core:lab_requests',order.patient.id )
		print("Order form errors are: ", order_form.errors)
		return redirect('core:lab_requests', patient_id) # redirect to view-order on success


@method_decorator(login_required, 'dispatch')
class MyOrders(View):
	# returns list of orders logged in user has made

	def get(self, *args, **kwargs):
		logged_in_user = get_user(self.request)
		return render(self.request, 'lis/view_orders.html', {
			'order_set': Order.objects.filter(ordered_by=logged_in_user),
			'active_link': 'lab'
		})


@method_decorator(login_required, 'dispatch')
class ViewOrderList(View):
	# returns a complete list of orders

	def get(self, *args, **kwargs):
		return render(self.request, 'lis/view_orders.html', {
			'order_set': Order.objects.all(),
			'active_link': 'lab',
			'process_payment': True,
		})


@method_decorator(login_required, 'dispatch')
class ViewOrder(View):
	# gets order_id from url and returns the 
	# corresponding Order and test_set

	def get(self, *args, **kwargs):
		order_id = kwargs['order_id']
		order:Order = get_object_or_404(Order, id=order_id)
		return render(self.request, 'lis/view_order.html', {
			'order': order,
			'test_set': order.test_set.all(),
			'active_link': 'lab',
		})


@method_decorator(login_required, 'dispatch')
class MarkOrderAsPaid(View):
	# gets order_id from url then gets order using order_id
	# changes the paid status of tests that belong to this order

	def get(self, *args, **kwargs):
		redirect_to = self.request.GET.get('next', '')
		order_id = kwargs['order_id']
		order: Order =  get_object_or_404(Order, id=order_id)
		order.mark_as_paid()
		order.save()
		messages.success(self.request, "Order status updated to PAID.")
		if redirect_to:
			return redirect(redirect_to)
		return redirect('view-orders') # on success redirect to orders-list


@method_decorator(login_required, 'dispatch')
class ViewTestList(View):
	# returns the list of tests,
	# if section is passed in the get request it returns 
	# filtered result for that laboratory section

	def get(self, *args, **kwargs):
		filtered_dept = self.request.GET.get('section', None)
		test_set = None
		if filtered_dept:
			test_set = LaboratoryTest.objects.filter(test_type__section__name__iexact=filtered_dept)
			if not test_set:
				messages.error(self.request, f'Could not find tests for section `{filtered_dept}`')
		else:
			test_set = LaboratoryTest.objects.all()
		return render(self.request, 'lis/view_tests.html', {
			'test_set': test_set,
			'active_link': 'lab'
		})


@method_decorator(login_required, 'dispatch')
class ViewTest(View):
	# returns test from the given test_id via the url
	# with specimen_form that will be used to create/edit the
	# specimen info with modal

	def get(self, *args, **kwargs):
		test_id = kwargs['test_id']
		test:LaboratoryTest = get_object_or_404(LaboratoryTest, id=test_id)
		specimen_form = SpecimenForm()
		#if test.specimen:
		#	specimen_form = SpecimenForm(instance=test.specimen)
		return render(self.request, 'lis/view_test.html', {
			'test': test,
			'specimen_form': specimen_form,
			'active_link': 'lab', 
		})


@method_decorator(login_required, 'dispatch')
class ToggleTestPaidStatus(View):
	# toggles paid status of a given test
	# if a test was referred, paid status can not be changed 
	# since it will be done on other labs and only the result is expected

	def get(self, *args, **kwargs):
		test_id = kwargs['test_id']
		test:LaboratoryTest = LaboratoryTest.objects.get(id=test_id)
		if test.referred:
			messages.error(self.request, "can not update payment status of a referred laboratory test.")
			return redirect('view-test', test_id)
		_message = "Test marked as UNPAID" if test.paid else "Test marked as PAID"
		test.paid = not test.paid
		test.save()
		messages.success(self.request, _message)
		return redirect('view-test', test.id)


@method_decorator(login_required, 'dispatch')
class ViewSpecimen(View):
	
	def post(self, *args, **kwargs):
		# returns specimen object for the given accession_number
		accession_number = self.request.POST['accession_number']
		specimen = Specimen.objects.get(accession_number=accession_number)
		return render(self.request, 'view_specimen.html', {
			'specimen': specimen,
			'active_link': 'lab',
		})


@method_decorator(login_required, 'dispatch')
class AddSpecimen(View):

	def get(self, *args, **kwargs):
		# if test already has specimen info,
		# it generates edit specimen form, if test doesn't have 
		# specimen info generates create specimen form
		test_id = kwargs['test_id']
		print('Test id is: ', test_id)
		test = LaboratoryTest.objects.get(id=test_id)
		specimen_form = SpecimenForm()
		if not test.specimen:
			return render(self.request, 'add_specimen.html', {
				'specimen_form': specimen_form, 
			})
		specimen_form = SpecimenForm(instance=test.specimen)
		return render(self.request, 'add_specimen.html', {
			'specimen_form': specimen_form,
		})

	def post(self, *args, **kwargs):
		# if test already has specimen edit it by giving 
		# the specimen instance and POST data,
		# if test doesn't have specimen create a new instance of specimen
		# and add it to the test, then change test status to 'SPECIMEN COLLECTED'
		test_id = kwargs['test_id']
		test:LaboratoryTest = LaboratoryTest.objects.get(id=test_id)
		specimen_form = None
		#if not test.specimen:
			# create new instance of Specimen
		specimen_form = SpecimenForm(self.request.POST)
		if specimen_form.is_valid():
			specimen = specimen_form.save()
			#test.specimen = specimen
			
			# then update test status to 'SPECIMEN COLLECTED'
			test.status = 'SPECIMEN COLLECTED'
			#test.save()
			test.specimen.add(specimen)
			test.save()
			messages.success(self.request, "Specimen info added successfully!")
			return redirect('core:add_lab_case', test.order.id)
		else:
			print('Specimen Form Errors:', specimen_form.errors)
			messages.error(self.request, specimen_form.errors)
			return redirect('core:add_lab_case', test.order.id)
			return render(self.request, 'lis/add_specimen.html', {
				'specimen_form': specimen_form,
				'error': True, # error flag or error message???
				'active_link': 'lab',
			})
		"""
		else:
			# if test already has specimen registered,
			# proceed to editing it
			specimen_form = SpecimenForm(self.request.POST, instance=test.specimen)
			if specimen_form.is_valid():
				specimen_form.save()
				# on success redirect to view test page
				messages.success(self.request, "Specimen info edited successfully!")
				return redirect('view-test', test_id)
			# on error show error messages
			return render(self.request, 'lis/add_specimen.html', {
				'specimen_form': specimen_form,
				'error': True, # error flag or error message???
				'active_link': 'lab',
			})
		"""
	
class SetSpecimenForTest(View):

	def post(self, *args, **kwargs):
		# if the specimen being used has already been registred, the -
		# accession number of the specimen is given and test will use the previously stored specimen
		# if the given accession number is not found, error message will be sent back
		test_id = kwargs['test_id']
		test: LaboratoryTest = get_object_or_404(LaboratoryTest, id=test_id)
		acc_number = self.request.POST.get('accession_number')
		try:
			specimen: Specimen = Specimen.objects.get(accession_number=acc_number)
			test.specimen = specimen
			# update test status to 'SPECIMEN COLLECTED'
			test.status = 'SPECIMEN COLLECTED' 
			test.save()
			messages.success(self.request, "Specimen info added to test.")
			return redirect('view-test', test_id)
		except Specimen.DoesNotExist:
			messages.error(self.request, "Specimen with provided accession number is not found.")
			return redirect('view-test', test_id)

		
@method_decorator(login_required, 'dispatch')
class EnterTestResult(View):

	# generates the appropriate form that is expected from a given test result
	# setup_form method create form_fields, expected result input are found from
	# objects from LaboratorTestResultType by applying test type filter
	# expected input types are number, choice, bool and text
	# if input type is CHOICE, choices will be TestResultChoice objects

	def setup_form(self, test_id):
		self.test = LaboratoryTest.objects.get(id=test_id)
		self.form_fields = {}
		self.normal_range = {}
		for result_type in LaboratoryTestResultType.objects.filter(test_type=self.test.test_type):
			if result_type.input_type == 'NUMBER':
				form_field = forms.FloatField(widget=forms.NumberInput(
					attrs={
						'min': 1,
						'class': 'form-control',
					}
				))
				if self.test.order.patient.age:
					age = self.test.order.patient.age
				else:
					age = 24
				normal_range = NormalRange.get_range(result_type, age, 'M') #TO-DO pass patient age and sex
				self.normal_range.update({
					f'id_{result_type.name}' : normal_range,
					})
				self.form_fields.update({result_type.name : form_field})
			elif result_type.input_type == "CHOICE":
				choice_set = [(x.choice, x.choice) for x in result_type.choice_set.all()]
				self.form_fields.update({result_type.name : forms.TypedChoiceField(choices=choice_set, widget=forms.Select(
					attrs={
						'class': 'form-control',
					}
				))})
			elif result_type.input_type == 'BOOL':
				self.form_fields.update({result_type.name : forms.BooleanField(required=False, widget=forms.CheckboxInput(
					attrs={
						'id': 'checkboxbg1'
					}
				))})
			elif result_type.input_type == 'TEXT':
				self.form_fields.update({result_type.name : forms.CharField(widget=forms.Input(
					attrs={
						'class': 'form-control',
					}
				))})

	def get(self, *args, **kwargs):
		# using the form fields created in setup_form method
		# a form for entering the test result will be generated
		# if a test already has test result entered it will be redirected to edit-test-result
		logged_in_user = get_user(self.request)
		result_entry_form = ResultEntryForm()
		test_id = kwargs['test_id']
		test:LaboratoryTest = LaboratoryTest.objects.get(id=test_id)
		# if test is not paid show error message and redirect to view-test
		"""
		if not test.paid and not test.referred:
			messages.error(self.request, "Test can not be processed before payment")
			return redirect('view-test', test_id)
		if not test.specimen and not test.referred:
			messages.error(self.request, "Test can not be processed before adding specimen info")
			return redirect('view-test', test_id)
		# if test already has results entered redirect to editing it
		"""
		if test.result_set.count() > 0:
			return redirect('edit-test-result', test_id)
		self.setup_form(test_id)
		result_entry_form.fields.update(self.form_fields)
		return render(
			self.request, 'lis/enter_result.html', {
				'test_id': test_id,
				'test': self.test,
				'form': result_entry_form,
				# if test was referred include a form to enter lab/hospital info
				'referred_test_result_form': ReferredTestResultForm() if self.test.referred else None,
				'nranges': self.normal_range,
				'active_link': 'lab',
			}
		)


	def post(self, *args, **kwargs):
		# for every expected input of a test in LaboratoryTestResultType
		# data provided in the POST data will be its value and a 
		# LaboratoryTestResult object is created
		logged_in_user = get_user(self.request)
		test_id = kwargs['test_id']
		test:LaboratoryTest = get_object_or_404(LaboratoryTest, id=test_id)
		self.setup_form(test_id)
		result_entry_form = ResultEntryForm(data=self.request.POST, dynamic_fields=self.form_fields)
		result_entry_form.fields = self.form_fields
		# form validation check
		if result_entry_form.is_valid():
			result_types:Sequence[LaboratoryTestResultType] = LaboratoryTestResultType.objects.filter(test_type=test.test_type)
			for field in self.form_fields:
				for req_result in result_types:
					if req_result.name == field:
						result_value = None
						try:
							result_value = result_entry_form.data[field]
						except KeyError:
							if req_result.input_type == 'BOOL':
								result_value = 'off'
						test_result = LaboratoryTestResult(test=test, reported_by=logged_in_user, result_type=req_result, value=result_value)
						#test_result.save()
						lab_history = OutpatientLabResult()
						patient = test_result.test.order.patient
						lab_history.patient = patient
						lab_history.visit = PatientVisit.objects.get(patient =patient, id__isnull=False, visit_status='Pending')
						lab_history.lab_result = test_result 
						#medication_history.doctor = 
						lab_history.registered_on = datetime.now()

						test_result.save()
						lab_history.save()

						# check if test was referred and save lab info
						if test.referred:
							_form = ReferredTestResultForm(self.request.POST)
							if _form.is_valid():
								referral_info = ReferredTestResult(lab_name=_form.fields['lab_name'], test=test)
								referral_info.save()            # check if all the required result inputs are entered
			# if all are entered test status will be changed to 'COMPLETED'
			test_results = LaboratoryTestResult.objects.filter(test=test)
			if len(result_types) == len(test_results):
				test.status = 'COMPLETED'
				test.save()
				# send notifications if test.order is complete
				if test.order.is_complete:
					redirect_url = ''
					try:
						redirect_url = reverse('view-order', kwargs={'order_id':test.order.id}) # url for view-order
						notify(self.test.ordered_by, 'info', f' Order {test.order.pk} is complete.', link=redirect_url)
					except:
						pass      
			# on success redirect to view-test
			messages.success(self.request, 'Test result entered successfully')
			return redirect('core:add_lab_case', test.order.id)
			return redirect('view-test', test_id)
		else:
			# Send error messages
			for error in result_entry_form.errors:
				messages.error(self.request, error)
			return redirect('enter-test-result', test_id)


@method_decorator(login_required, 'dispatch')
class EditTestResult(View):

	def setup_form(self, test_id, include_value=True):
		# same as setup_form for the EnterTestResult view but generates
		# form fields from the LaboratoryTestResult model and when include_value is True
		# it gets the value of that test result to generate a proper form during GET request
		# if the method is POST the value associated with that result is not required
		self.form_fields = {}
		self.test:LaboratoryTest = LaboratoryTest.objects.get(id=test_id)
		result_set: Sequence[LaboratoryTestResult] = LaboratoryTestResult.objects.filter(test=self.test)
		self.normal_range = {}
		for result in result_set:
			attrs = {'class': 'form-control'} # default attribute that all input fields need
			if result.result_type.input_type == 'NUMBER':
				attrs.update({'min': 1})
				if include_value:
					attrs.update({
						'value': result.value,
					})
				normal_range = NormalRange.get_range(result.result_type, 33, 'M') #TO-DO pass patient age and sex
				self.normal_range.update({
					f'id_{result.result_type.name}' : normal_range,
					})
				form_field = forms.FloatField(widget=forms.NumberInput(
					attrs = attrs
				))
				self.form_fields.update({result.result_type.name : form_field})
			elif result.result_type.input_type == "CHOICE":
				choice_set = [(x.choice, x.choice) for x in result.result_type.choice_set.all()]
				self.form_fields.update({result.result_type.name : forms.TypedChoiceField(choices=choice_set, initial=result.value, widget=forms.Select(
					attrs = attrs
				))})
			elif result.result_type.input_type == 'BOOL':
				attrs.pop('class') # remove form-control from checkbox
				attrs.update({
					'id': 'checkboxbg1',
					'checked' if result.value == 'on' else '' : 'true',
				})
				# no need to set value on a checkbox
				self.form_fields.update({result.result_type.name : forms.BooleanField(required=False, widget=forms.CheckboxInput(
					attrs = attrs
				))})
			elif result.result_type.input_type == 'TEXT':
				if include_value:
					attrs.update({'value': result.value})
				self.form_fields.update({result.result_type.name : forms.CharField(widget=forms.Input(
					attrs = attrs
				))})

	def get(self, *args, **kwargs):
		# returns a form using fields in self.form_fields 
		# which is created in setup_form method
		logged_in_user = get_user(self.request)
		result_entry_form = ResultEntryForm()
		test_id = kwargs['test_id']
		self.setup_form(test_id, include_value=True)
		result_entry_form.fields.update(self.form_fields)
		return render(
			self.request, 'lis/edit_test_result.html', {
				'test_id': test_id,
				'test': self.test,
				'form': result_entry_form,
				'nranges': self.normal_range,
				'active_link': 'lab',
			}
		)

	def post(self, *args, **kwargs):
		test_id = kwargs['test_id']
		self.setup_form(test_id, include_value=False)
		result_entry_form = ResultEntryForm(data=self.request.POST)
		result_entry_form.fields = self.form_fields
		result_set: Sequence[LaboratoryTestResult] = LaboratoryTestResult.objects.filter(test=self.test)
		if result_entry_form.is_valid():
			for result in result_set:
				for field in self.form_fields:
					if field == result.label:
						try:
							if result.result_type.input_type == 'BOOL':
								print('Checkbox input for ', field, ' submitted value is ', result_entry_form.data[field], "z"*100)
							result.value = result_entry_form.data[field]
						except KeyError:
							# check for BOOL input types since checkboxes will not be submitted
							# if they're unchecked
							if result.result_type.input_type == 'BOOL':
								# if it's BOOL/checkbox set its value to off
								result.value = 'off'
						result.save()
			# update test status
			self.test.status = 'COMPLETED'
			self.test.save()
			notify(self.test.ordered_by, 'info', f' {self.test.test_type.name} test with id {self.test.pk} result was edited.')
			messages.success(self.request, "Test result edited successfully!")
			return redirect('edit-test-result', test_id) # redirect back to view-test/edit-test-result/test-result view
		else:
			# send error message
			for error in result_entry_form.errors:
				messages.error(self.request, error)
			return render(self.request, 'lis/edit_test_result.html', {
				'test_id': test_id,
				'test': self.test,
				'form': result_entry_form,
				'active_link': 'lab',
			}
		)


@method_decorator(login_required, 'dispatch')
class ViewTestResult(View):
	# returns test_result of a given test
	# if logged in user is not the same as the user who ordered the test
	# error message will be displayed and page will be redirected to view-tests

	def get(self, *args, **kwargs):
		logged_in_user = get_user(self.request)
		test_id = kwargs['test_id']
		test:LaboratoryTest = get_object_or_404(LaboratoryTest, id=test_id)
		if not (test.ordered_by == logged_in_user):
			messages.error(self.request, "request forbidden: currently logged in user is not allowed to view test result")
			return redirect('view-tests')
		test_results = LaboratoryTestResult.objects.filter(test=test)
		return render(self.request, 'lis/view_test_result.html', {
			'test_id': test_id,
			'test': test,
			'test_result_set': test_results,
			'active_link': 'lab'
		})


class TrackOrderStatus(View):
	# auth not needed
	# generated url/qr/bc or acc number

	def get(self, *args, **kwargs):
		order_id = kwargs['test_id']
		order = Order.objects.get(id=order_id)
		return render(self.request, 'lis/order_status.html', {
			'order': order,
		})


@method_decorator(login_required, 'dispatch')
class UpdateTestStatus(View):
	# changes the status of tests if the test is paid and status is 'SPECIMEN COLLECTED'
	# and displays success message
	# if not redirects to view-test and error message is sent

	def post(self, *args, **kwargs):
		test_id = kwargs['test_id']
		test: LaboratoryTest = get_object_or_404(LaboratoryTest, id=test_id)
		if not (test.paid and test.status == 'SPECIMEN COLLECTED'):
			messages.error(self.request, "Test status can not be updated currently.")
			return redirect('view-test', test_id)
		status = self.request.POST.get('test_status')
		test.status = status
		test.save()
		messages.success(self.request, "Test status updated successfully!")
		return redirect('view-test', test_id)


@method_decorator(login_required, 'dispatch')
class ViewSpecimenImage(View):
	# displays the barcode image of a specimen

	def get(self, *args, **kwargs):
		specimen_id = kwargs['specimen_id']
		specimen: Specimen = get_object_or_404(Specimen, id=specimen_id)
		return render(self.request, 'lis/specimen_image.html', {
			'specimen': specimen,
		})


@method_decorator(login_required, 'dispatch')
class MarkMultipleOrdersAsPaid(View):
	# gets id of orders from POST data
	# if the orders are found they'll be marked as paid
	# if not found error message will be shown abt unexisting orders

	def post(self, *args, **kwargs):
		order_id_list:Sequence[int] = [ int(x) for x in self.request.POST.getlist('orders') ]
		if not order_id_list:
			messages.error(self.request, "No order is selected.")
			return redirect('view-orders')
		paid_orders_list = []
		not_found_orders = []
		for order_id in order_id_list:
			try:
				order:Order = Order.objects.get(id=order_id)
				order.mark_as_paid()
				paid_orders_list.append(order_id)
			except Order.DoesNotExist:
				not_found_orders.append(order_id)
		if not_found_orders:
			messages.error(self.request, f"Orders with id {not_found_orders} do not exist.")
		if paid_orders_list:
			messages.success(self.request, f"Orders with id {paid_orders_list} marked as paid.")
		return redirect('view-orders')


@method_decorator(login_required, 'dispatch')
class CancelOrder(View):
	# if logged in user and user who made the order are the same
	# order will be deleted else error message will be shown and page will be redirected

	def post(self, *args, **kwargs):
		order_id = self.request.POST.get('order_id')
		order:Order = get_object_or_404(Order, id=order_id)
		if not order.ordered_by == get_user(self.request):
			messages.error(self.request, "logged in user is not allowed to cancel selected order.")
			return redirect('view-orders')
		order.delete() # delete/ create inactive status
		messages.success(self.request, f"Order with id: {order_id} is cancelled.")
		return redirect('view-orders')


class FilterTestsBySection(View):
	# takes the name of the lab section either from GET or POST request
	# and returns LaboratorTest of that section

	def get(self, *args, **kwargs):
		section = self.request.GET.get('section', '')
		test_set:Sequence[LaboratoryTest] = LaboratoryTest.objects.filter(test_type__section__name__iexact=section)
		if not test_set:
			messages.error(self.request, f'Could not find tests for section `{section}`')
			return redirect('view-tests')
		return render(self.request, 'lis/view_tests.html', {
			'test_set': test_set,
			'active_link': 'lab'
		})

	def post(self, *args, **kwargs):
		section = self.request.POST.get('section', '')
		test_set:Sequence[LaboratoryTest] = LaboratoryTest.objects.filter(test_type__section__name__iexact=section)
		if not test_set:
			messages.error(self.request, f'Could not find tests for section `{section}`')
			return redirect('view-tests')
		return render(self.request, 'lis/view_tests.html', {
			'test_set': test_set,
			'active_link': 'lab'
		})


class AddSampleType(View):

	def get(self, *args, **kwargs):
		return render(self.request, 'lis/add_sample_type.html', {
			'form': SampleTypeForm()
		})

	def post(self, *args, **kwargs):
		form = SampleTypeForm(data=self.request.POST)
		if form.is_valid():
			form.save()
			messages.success(self.request, 'Sample type added')
			return redirect('site_config:site_settings')
		else:
			messages.error(self.request, 'Error while creating sample type')
			return render(self.request, 'lis/add_sample_type.html', {
				'form': SampleTypeForm()
			})


class CreateLabTestType(View):

	def get(self, *args, **kwargs):
		form = LabTestTypeForm()
		section_form = LaboratorySectionForm()

		test_name = self.request.GET.get('search-test',None)
		if test_name==None:
			test_type_list = LaboratoryTestType.objects.all()
		else:
			test_type_list = LaboratoryTestType.objects.filter(name__icontains=test_name)

		return render(self.request, 'lis/lab_test_type_form.html', {
			'form': form,
			'section_form': section_form,
			'test_type_list': test_type_list
		})

	def post(self, *args, **kwargs):
		form = LabTestTypeForm(data=self.request.POST)
		if form.is_valid():
			test_type:LaboratoryTestType = form.save()
			messages.success(self.request, 'Laboratory test type added.')
			return redirect('edit_lab_test_result_type', test_type.id)
		messages.error(self.request, 'Error while creating test type')
		return render(self.request, 'lis/lab_test_type_form.html', {
			'form': form,
		})



class CreateLabTestItem(View):

	def get(self, *args, **kwargs):
		form = LabTestTypeForm()
		section_form = LaboratorySectionForm()
		item_id = kwargs['item_id']
		item = get_object_or_404(Item, id=item_id)



		return render(self.request, 'lis/create_lab_test_item.html', {
			'form': form,
			'section_form': section_form,
			'item': item,

		})

	def post(self, *args, **kwargs):
		item_id = kwargs['item_id']
		item = Item.objects.get(id=item_id)
	
		form = LabTestTypeForm(self.request.POST)
		if form.is_valid():
			test_type:LaboratoryTestType = form.save(commit=False)
			item.lab_test = test_type
			test_type.save()
			item.save()
			messages.success(self.request, 'Laboratory test type added.')
			return redirect('items')
		messages.error(self.request, 'Error while creating test type')
		return redirect('create_lab_test_item', item.id)
		

class EditLabTestType(View):

	def get(self, *args, **kwargs):

		id = kwargs['id']
		obj = get_object_or_404(LaboratoryTestType, id=id)
		form = LabTestTypeForm(instance=obj)
		test_type_list = LaboratoryTestType.objects.all()
		return render(self.request, 'lis/lab_test_type_form.html', {
			'form': form,
			'test_type_list': test_type_list
		})

	def post(self, *args, **kwargs):
		id = kwargs['id']
		obj = get_object_or_404(LaboratoryTestType, id=id)
		form = LabTestTypeForm(data=self.request.POST, instance=obj)
		if form.is_valid():
			form.save()
			messages.success(self.request, 'Laboratory test type edited successfully.')
			return redirect('create_lab_test_type')
		messages.error(self.request, 'Error while editing test type')
		return render(self.request, 'lis/lab_test_type_form.html', {
			'form': form,
		})


class RemoveLabTestType(View):

	def get(self, *args, **kwargs):
		id = kwargs['id']
		obj = get_object_or_404(LaboratoryTestType, id=id)
		obj.delete()
		messages.success(self.request, 'Test type has been removed')
		return redirect('create_lab_test_type')


class EditLabTestResultType(View):

	def get(self, *args, **kwargs):
		test_type_id = kwargs['id']
		test_type = get_object_or_404(LaboratoryTestType, id=test_type_id)
		rt_list = LaboratoryTestResultType.objects.filter(test_type=test_type,active=True)
		rt_form = LabTestResultTypeForm()
		normal_range_form = NormalRangeForm()
		return render(self.request, 'lis/edit_result_type.html', {
			'rt_list': rt_list,
			'test_type': test_type,
			'rt_form': rt_form,
			'normal_range_form': normal_range_form,
		})

	def post(self, *args, **kwargs):
		choice_list = []
		test_type_id = kwargs['id']
		test_type = get_object_or_404(LaboratoryTestType, id=test_type_id)
		rt_list = LaboratoryTestResultType.objects.filter(test_type=test_type)
		rt_form = LabTestResultTypeForm(data=self.request.POST)
		if rt_form.is_valid():
			rt:LaboratoryTestResultType = rt_form.save(commit=False)
			rt.test_type = test_type
			if rt.input_type == 'CHOICE':
				choice_list = set(self.request.POST.getlist('choice_name'))
				if not any(choice_list):
					messages.error(self.request, 'No choices provided for expected result field')
					return render(self.request, 'lis/edit_result_type.html', {
						'rt_list': rt_list,
						'test_type': test_type,
						'rt_form': rt_form,
						'no_choice_error': True,
						'normal_range_form': NormalRangeForm(),
					})
			rt.save()
			if choice_list:
				for c in choice_list:
					TestResultChoice.objects.create(test_result_type=rt, choice=c)
			messages.success(self.request, 'Added successfully')
			return redirect('edit_lab_test_result_type', test_type_id)
		messages.error(self.request, 'Error while adding')
		return render(self.request, 'lis/edit_result_type.html', {
			'rt_list': rt_list,
			'test_type': test_type,
			'rt_form': rt_form,
			'normal_range_form': NormalRangeForm(),
		})


class RemoveResultType(View):

	def get(self, *args, **kwargs):
		obj = get_object_or_404(LaboratoryTestResultType, id=kwargs['id'])
		obj.active = False
		obj.save()
		messages.success(self.request, 'Result type deleted.')
		return redirect('edit_lab_test_result_type', obj.test_type.id)


class AddNormalRange(View):

	def post(self, *args, **kwargs):
		id = kwargs['id'] # id of result_type instance of LaboratoryTestResultType
		obj = get_object_or_404(LaboratoryTestResultType, id=id)
		_form = NormalRangeForm(data=self.request.POST)
		if _form.is_valid():
			nr:NormalRange = _form.save(commit=False)
			nr.test_result_type = obj
			try:
				nr.save()
			except ValueError as e:
				messages.error(self.request, str(e))
				return redirect('edit_lab_test_result_type', obj.id)
			messages.success(self.request, 'Normal range added')
			return redirect('edit_lab_test_result_type', obj.test_type.id)
		messages.error(self.request, 'Error while setting normal range')
		return redirect('edit_lab_test_result_type', obj.id)


class ReportPage(View):

	def get(self, *args, **kwargs):
		# lab_test_nos = []
		# lab_section_data = []
		g_report_list = []
		total_no_tests = 0
		total_no_patients = 0
		total_price = 0
		total_avg_per_day = 0
		test_type_list = LaboratoryTestType.objects.all()
		start_date = datetime.strptime(self.request.GET.get('start_date') or '1970-01-01', '%Y-%m-%d')
		end_date = datetime.strptime(self.request.GET.get('end_date') or str(datetime.now().date()),  '%Y-%m-%d')
		lab_section = int(self.request.GET.get('lab_section', '0'))
		if lab_section:
			test_type_list = test_type_list.filter(section__id=lab_section)
		for tt in test_type_list:
			gp = GeneralReport(tt, start_date, end_date)
			g_report_list.append(gp)
			total_no_tests += gp.total_no_tests
			total_no_patients += gp.no_patient
			#total_price += gp.total_price
			total_avg_per_day += gp.avg_per_day
		
		# for ltt in test_type_list:
		#     test_list:Sequence[LaboratoryTest] = LaboratoryTest.objects.filter(test_type=ltt, status='COMPLETED')
		#     if lab_section:
		#         test_list = test_list.filter(test_type__section__id=lab_section)
		#     if start_date:
		#         test_list = [x for x in test_list if (x.ordered_at.date() > start_date) and (x.ordered_at.date() < end_date)]
		#     test_count = test_list.count() if isinstance(test_list, QuerySet) else len(test_list)
		#     if test_count:
		#         lab_test_nos.append((ltt, test_count, test_count*ltt.price))
		# for ls in LaboratorySection.objects.all():
		#     section_tests = LaboratoryTest.objects.filter(test_type__section=ls)
		#     lab_section_data.append((ls, section_tests.count()))
		return render(self.request, 'lis/report.html', {
			# 'lab_test_nos': lab_test_nos,
			# 'lab_section_data': lab_section_data,
			# 'test_type_list': test_type_list,
			'lab_sections': LaboratorySection.objects.all(),
			'general_report_list': g_report_list,
			'total_no_tests': total_no_tests,
			'total_no_patients': total_no_patients,
			#'total_price': total_price,
			'total_avg_per_day': total_avg_per_day,
		})


def LaboratoryList(request):
	lab_list = Laboratory.objects.all()

	assigned_emps = LabEmployee.objects.filter(active=True)
	all_emps = Employee.objects.filter(designation__name='Laboratory')
	unassigned_emps = []
	for a in all_emps:
		if LabEmployee.objects.filter(active=True, laboratorist__id =a.id).exists():
			print('Do Nothing')
		else:
			unassigned_emps.append(a.id)
	assign_form = AssignLabEmployeeForm()
	assign_form.fields["laboratorist"].queryset = Employee.objects.filter(id__in=unassigned_emps) 

	return render(self.request, 'lis/laboratory_list.html', {
			'lab_list': lab_list,
			'assign_form': assign_form,

		})

def AssignLabEmployee(request, lab_id):
	lab = Laboratory.objects.get(id=lab_id)
	if request.method == 'POST':
		assign_form = AssignLabEmployeeForm(request.POST)
		if assign_form.is_valid():
			lab_employee = assign_form.save(commit=False)
			lab_employee.laboratory = lab
			lab_employee.active = True
			lab_employee.save()

			messages.success(request,'Successful!')
			return redirect('laboratory_list')
		else:
			messages.error(request,str(assign_form.errors))
			return redirect('laboratory_list')
			#elif user.employee.designation.name == 'Laboratory Head':

class Specimens(View):

	def get(self, *args, **kwargs):
		# generates OrderForm for the given patient_id
		# returns order_form and patient object
		patient_id = kwargs['patient_id']
		patient = Patient.objects.get(id=patient_id)
		#specimen_list = Specimen.objects.first().patient_specimens(patient_id)
		specimen_list = Specimen.objects.all()[::-1]
		context = {'patient': patient,
					'specimen_list':specimen_list,
					'select_test_form':SelectTestForm(),
					'specimen_form':SpecimenForm()
					}

		return render(self.request, 'lis/specimens.html',context)

class AddSpecimenToTest(View):

	def post(self, *args, **kwargs):
		# if test already has specimen edit it by giving 
		# the specimen instance and POST data,
		# if test doesn't have specimen create a new instance of specimen
		# and add it to the test, then change test status to 'SPECIMEN COLLECTED'
		patient_id = kwargs['patient_id']
		patient = Patient.objects.get(id=patient_id)
		print('patient is: ',patient)
		select_test_form = SelectTestForm(self.request.POST)
		specimen_form = SpecimenForm(self.request.POST)
		if specimen_form.is_valid():
			if select_test_form.is_valid():
			
				# then update test status to 'SPECIMEN COLLECTED'
				test_form = select_test_form.save(commit=False)
				test_form.test.status = 'SPECIMEN COLLECTED'
				specimen = specimen_form.save()
				test_form.test.specimen.add(specimen)
				test_form.test.save()

				messages.success(self.request, "Specimen info added successfully!")
				return redirect('specimens', patient.id)
			else:
				print('Errors:', specimen_form.errors)
				messages.error(self.request, specimen_form.errors)
				return redirect('specimens', patient.id)

		else:
			print('Specimen Form Errors:', specimen_form.errors)
			messages.error(self.request, specimen_form.errors)
			return redirect('specimens', patient.id)
			return render(self.request, 'lis/add_specimen.html', {
				'specimen_form': specimen_form,
				'error': True, # error flag or error message???
				'active_link': 'lab',
			})


@method_decorator(login_required, 'dispatch')
class EditSpecimen(View):

	def post(self, *args, **kwargs):
		order_id = kwargs['order_id']
		specimen_id = kwargs['specimen_id']

		order:Order = Order.objects.get(id=order_id)
		specimen = Specimen.objects.get(id=specimen_id)
		specimen_form = EditSpecimenForm(self.request.POST,specimen_id=specimen.id)
		if specimen_form.is_valid():
			specimen_form = specimen_form.save(commit=False)			
			specimen.sample_volume = specimen_form.sample_volume
			specimen.save()
			messages.success(self.request, "Specimen info edited successfully!")
			return redirect('core:add_lab_case', order.id)
		else:
			print('Specimen Form Errors:', specimen_form.errors)
			messages.error(self.request, specimen_form.errors)
			return redirect('core:add_lab_case',order.id)

@method_decorator(login_required, 'dispatch')
class EditSpecimen2(View):

	def post(self, *args, **kwargs):
		specimen_id = kwargs['specimen_id']

		patient = Patient.objects.get(id=patient_id)
		specimen = Specimen.objects.get(id=specimen_id)
		specimen_form = EditSpecimenForm(self.request.POST,specimen_id=specimen.id)
		if specimen_form.is_valid():
			specimen_form = specimen_form.save(commit=False)			
			specimen.sample_volume = specimen_form.sample_volume
			specimen.save()
			messages.success(self.request, "Specimen info edited successfully!")
			return redirect('specimens', patient.id)
		else:
			print('Specimen Form Errors:', specimen_form.errors)
			messages.error(self.request, specimen_form.errors)
			return redirect('specimens',patient.id)

class DeleteSpecimen(View):

	def get(self, *args, **kwargs):
		order_id = kwargs['order_id']
		specimen_id = kwargs['specimen_id']

		order:Order = Order.objects.get(id=order_id)
		specimen = Specimen.objects.get(id=specimen_id)
		specimen.active=False
		specimen.save()
		messages.success(self.request, "Specimen info Deleted successfully!")
		return redirect('core:add_lab_case', order.id)

@method_decorator(login_required, 'dispatch')
class LabDashboard(View):

	def get(self, *args, **kwargs):
		stats_chart = OrderedDict()

		# The `chartConfig` dict contains key-value pairs of data for chart attribute
		chartConfig = OrderedDict()
		chartConfig["caption"] = "Stats Values"
		chartConfig["subCaption"] = ""
		chartConfig["xAxisName"] = "Date"
		chartConfig["yAxisName"] = "Value"
		chartConfig["numberSuffix"] = ""
		chartConfig["theme"] = "fusion"
		chartConfig["numVisiblePlot"] = "8",
		chartConfig["flatScrollBars"] = "1",
		chartConfig["scrollheight"] = "1",
		chartConfig["type"] = "pie2d",

		stats_chart["chart"] = chartConfig
		stats_chart["data"] = []


		# generates OrderForm for the given patient_id
		# returns order_form and patient object
		patient_id = kwargs['patient_id']
		patient = Patient.objects.get(id=patient_id)
		#specimen_list = Specimen.objects.first().patient_specimens(patient_id)
		day = datetime.now()
		
		before_date = day - timedelta(days=100)

		test_list = LaboratoryTest.objects.filter(order__ordered_at__range=[before_date,day])
		pending_test_count = test_list.filter(status='PENDING').count()
		completed_test_count = test_list.filter(status='COMPLETED').count()
		test_list = test_list[::-1]
		test_type_count = []
		test_types = []
		groups = []
		group_count = []

		for test_type in LaboratoryTestType.objects.all():
			test_count = LaboratoryTest.objects.filter(order__ordered_at__range=[before_date,day],test_type=test_type).count()
			group = LaboratoryTest.objects.filter(order__ordered_at__range=[before_date,day],test_type__section=test_type.section)

			if test_count>0:
				test_types.append(test_type)
				test_type_count.append(test_count)
			if group.count()>0:
				if test_type.section in groups:
					print('already in group')
				else:
					groups.append(test_type.section)
					group_count.append(group.count())

		test_type_zip = zip(test_types,test_type_count)
		group_zip = zip(groups,group_count)

		this_month = datetime.now().month
		last_month = (datetime.now() -timedelta(days=30)).month
		print('this month',this_month)
		month_request_count = []
		month_array = []
		all_request_list = LaboratoryTest.objects.filter(order__ordered_at__range=[before_date,day])
		for request in all_request_list:
			if request.order.ordered_at.month == this_month:
				month_str = str(request.order.ordered_at.year) + " - " + str(request.order.ordered_at.month)
				if month_str in month_array:
					print('k')
				else:
					month_array.append(month_str)
					month_request_list = LaboratoryTest.objects.filter(order__ordered_at__month=this_month)
					month_request_count.append(month_request_list.count())
					stats_chart["data"].append({"label": month_str, "value": month_request_list.count()})

			elif request.order.ordered_at.month == last_month:
				month_str = str(request.order.ordered_at.year) + " - " + str(request.order.ordered_at.month)
				if month_str in month_array:
					print('k')
				else:
					month_array.append(month_str)
					month_request_list = LaboratoryTest.objects.filter(order__ordered_at__month=last_month)
					month_request_count.append(month_request_list.count())
					stats_chart["data"].append({"label": month_str, "value": month_request_list.count()})
		stats_overview_zip = zip(month_array,month_request_count)
		stats_chart = FusionCharts("line", "stats_chart", "560", "400", "stats_chart_container", "json", stats_chart)

		if self.request.htmx:
			value = self.request.GET.get('last_x_days')


			today = datetime.now()
			if value == None:
				print('')
			elif value == '0':
				test_list = LaboratoryTest.objects.filter(order__ordered_at__range=[before_date,day])

			else:
				last_x_day = today - timedelta(days=int(value))
				test_list = LaboratoryTest.objects.filter(order__ordered_at__range=[last_x_day,day])
			pending_test_count = test_list.filter(status='PENDING').count()
			completed_test_count = test_list.filter(status='COMPLETED').count()

			test_list = test_list[::-1]

			context2 = {'patient': patient,
						'test_list':test_list,
						'pending_test_count':pending_test_count,
						'completed_test_count':completed_test_count,
						'total_request_count':pending_test_count + completed_test_count,

						'test_type_zip':test_type_zip,
						'group_zip':group_zip,
						'stats_chart':stats_chart.render(),
						'stats_overview_zip':stats_overview_zip,

						}
			return render(self.request,'lis/partials/htmx/test_list_htmx.html', context2)
		context = {'patient': patient,
					'test_list':test_list,
					'pending_test_count':pending_test_count,
					'completed_test_count':completed_test_count,
					'total_request_count':pending_test_count + completed_test_count,

					'test_type_zip':test_type_zip,
					'group_zip':group_zip,
					'stats_chart':stats_chart.render(),
					'stats_overview_zip':stats_overview_zip,

					}

		return render(self.request, 'lis/lab_dashboard.html',context)

@method_decorator(login_required, 'dispatch')
class LabResultRanges(View):

	def get(self, *args, **kwargs):
		# generates OrderForm for the given patient_id
		# returns order_form and patient object
		result_type_id = kwargs['result_type_id']
		result_type = LaboratoryTestResultType.objects.get(id=result_type_id)
		#specimen_list = Specimen.objects.first().patient_specimens(patient_id)

		range_list = NormalRange.objects.filter(test_result_type=result_type)

		context = {
					'range_list':range_list,
					}

		return render(self.request, 'lis/lab_result_ranges.html',context)

@method_decorator(login_required, 'dispatch')
class LabResults(View):

	def get(self, *args, **kwargs):
		# generates OrderForm for the given patient_id
		# returns order_form and patient object
		patient_id = kwargs['patient_id']
		patient = Patient.objects.get(id=patient_id)
		#specimen_list = Specimen.objects.first().patient_specimens(patient_id)

		result_list = LaboratoryTestResult.objects.all()

		context = {'patient':patient,
					'result_list':result_list,
					}

		return render(self.request, 'lis/results.html',context)
