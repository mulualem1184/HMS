from notification.models import notify
from typing import Sequence

from django import forms
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import get_user
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from .forms import (LaboratoryTestForm, OrderForm, ReferredTestResultForm,
                    ResultEntryForm, SpecimenForm)
from .models import (LaboratorySection, LaboratoryTest, LaboratoryTestResult,
                     LaboratoryTestResultType, LaboratoryTestType, NormalRange, Order,
                     Patient, ReferredTestResult, Specimen)
from datetime import datetime

from outpatient_app.models import OutpatientLabResult, PatientVisit
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
            order.save()
        return redirect('view-orders') # redirect to view-order on success


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
            order.ordered_by = get_user(self.request)
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
            order.save()
            messages.success(self.request, "Order created successfully!")
            return redirect('view-order', order.id)
        print("Order form errors are: ", order_form.errors)
        return redirect('view-orders') # redirect to view-order on success


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
        if test.specimen:
            specimen_form = SpecimenForm(instance=test.specimen)
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
        if not test.specimen:
            # create new instance of Specimen
            specimen_form = SpecimenForm(self.request.POST)
            if specimen_form.is_valid():
                specimen = specimen_form.save()
                test.specimen = specimen
                # then update test status to 'SPECIMEN COLLECTED'
                test.status = 'SPECIMEN COLLECTED'
                test.save()
                messages.success(self.request, "Specimen info added successfully!")
                return redirect('view-test', test_id)
            else:
                print('Specimen Form Errors:', specimen_form.errors)
                messages.error(self.request, specimen_form.errors)
                return render(self.request, 'lis/add_specimen.html', {
                    'specimen_form': specimen_form,
                    'error': True, # error flag or error message???
                    'active_link': 'lab',
                })
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
                normal_range = NormalRange.get_range(result_type, 33, 'M') #TO-DO pass patient age and sex
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
        if not test.paid and not test.referred:
            messages.error(self.request, "Test can not be processed before payment")
            return redirect('view-test', test_id)
        if not test.specimen and not test.referred:
            messages.error(self.request, "Test can not be processed before adding specimen info")
            return redirect('view-test', test_id)
        # if test already has results entered redirect to editing it
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
                        lab_history = OutpatientLabResult()
                        patient = test_result.test.order.patient
                        lab_history.patient = patient
                        lab_history.visit = PatientVisit.objects.filter(patient = patient).exclude(visit_status='Ended').last()
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
                                referral_info.save()
            # check if all the required result inputs are entered
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