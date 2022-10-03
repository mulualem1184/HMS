from django.shortcuts import render
from .models import *
from .utils import return_triaged_patient, return_room_queue

from core.models import *
from staff_mgmt.models import StaffTeam,Department,Designation

from pharmacy_app.models import *
from inpatient_app.models import *
from billing_app.models import *
from lis.models import LaboratorySection
from django.contrib import messages
from core.forms import PatientPaymentStatusForm, InsuranceDetailForm
from .forms import *
from billing_app.forms import ServiceForm, InsuranceExcludedServiceForm, PatientInsuranceDetailForm
from staff_mgmt.forms import CreateStaffTeamForm

from django.shortcuts import redirect
from django.contrib import messages
from datetime import datetime
import itertools
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from collections import OrderedDict
from .fusioncharts import FusionCharts


# Create your views here.
def myFirstChart(request):
# Chart data is passed to the `dataSource` parameter, like a dictionary in the form of key-value pairs.
	dataSource = OrderedDict()

# The `chartConfig` dict contains key-value pairs of data for chart attribute
	chartConfig = OrderedDict()
	chartConfig["caption"] = "Countries With Most Oil Reserves [2017-18]"
	chartConfig["subCaption"] = "In MMbbl = One Million barrels"
	chartConfig["xAxisName"] = "Country"
	chartConfig["yAxisName"] = "Reserves (MMbbl)"
	chartConfig["numberSuffix"] = "K"
	chartConfig["theme"] = "fusion"

	dataSource["chart"] = chartConfig
	dataSource["data"] = []
# The data for the chart should be in an array wherein each element of the array  is a JSON object having the `label` and `value` as keys.
# Insert the data into the `dataSource['data']` list.
	for drug in Dosage.objects.all():
		dispensed_drugs = DrugDispensed.objects.filter(bill_no__drug=drug)
		drug_sum = 0
		if dispensed_drugs:
			for sd in dispensed_drugs:
				price = DrugPrice.objects.get(drug=sd.bill_no.drug,active='active')
				drug_sum = drug_sum + price.selling_price
			print('Drug: ',str(drug), ' Sum: ', drug_sum)
			dataSource["data"].append({"label": str(drug), "value": drug_sum})

# Create an object for the column 2D chart using the FusionCharts class constructor
# The chart data is passed to the `dataSource` parameter.
	column2D = FusionCharts("column2d", "myFirstChart", "600", "400", "myFirstchart-container", "json", dataSource)
	#return render(request, 'index.html', {'output': column2D.render()})
	context = {'output': column2D.render()}
	return render(request,'outpatient_app/index33.html',context)

def PatientRegistration(request):
	#age = datetime.strptime(request.GET.get('birth_date') or '1998-09-02', '%Y-%m-%d')
	age = datetime.now()
	patient_form = PatientRegistrationForm()
	payment_status_form = PatientPaymentStatusForm()
	if request.method == 'POST':
		patient_form = PatientRegistrationForm(request.POST)
		payment_status_form = PatientPaymentStatusForm(request.POST)
		if patient_form.is_valid():
			patient_model = patient_form.save(commit=False)
			status_model = payment_status_form.save(commit=False)
			#patient_model.age = age
			patient_model.save()
			status_model.patient = patient_model
			status_model.active = True
			status_model.registered_on = datetime.now()
			status_model.save()
			if status_model.payment_status == 'Insurance':
				return redirect('enter_insurance_detail', patient_model.id)
			messages.success(request, patient_model.first_name + " " + patient_model.last_name + " has been successfully registered!")

		else:
			messages.error(request, str(patient_form.errors))
	context = {'patient_form':patient_form,
				'payment_status_form':payment_status_form
				}
	return render(request,'outpatient_app/patient_registration.html',context)

def EnterInsuranceDetail(request, patient_id):
	patient = Patient.objects.get(id=patient_id)
	insurance_info_form = InsuranceDetailForm()
	insurance_detail_form = PatientInsuranceDetailForm()
	insurance_excluded_form = InsuranceExcludedServiceForm()

	if request.method == 'POST':
		insurance_info_form = InsuranceDetailForm(request.POST)
		insurance_detail_form = PatientInsuranceDetailForm(request.POST)
		insurance_excluded_form = InsuranceExcludedServiceForm()
		if insurance_info_form.is_valid():
			insurance_model = insurance_info_form.save()
			insurance_detail = insurance_detail_form.save(commit=False)
			excluded_model = insurance_excluded_form.save(commit=False)

			patient_insurance = PatientInsurance()
			patient_insurance.patient = patient
			patient_insurance.insurance_detail = insurance_model
			patient_insurance.active = True

			insurance_detail.patient = patient
			insurance_detail.insurance = patient_insurance


			excluded_model.insurance = patient_insurance

			patient_insurance.save()
			insurance_detail.save()
			excluded_model.save()

			messages.success(request, patient.first_name + " " + patient.last_name + " has been successfully registered!")
			return redirect('patient_registration')

	context = {'insurance_info_form':insurance_info_form,
				'insurance_detail_form':insurance_detail_form,
				'insurance_excluded_form':insurance_excluded_form,
				}
	return render(request,'outpatient_app/enter_insurance_detail.html',context)

def OutpatientTriageForm(request):
	service_list = ServiceCopy.objects.all()
	service_team_array = []
	service_array = []
	"""
	for service in service_list:
		copy = ServiceCopy()
		copy.service = service
		copy.save()
	"""
	arrival_form = PatientArrivalForm()
	complaint_form = ChiefComplaintForm()
	vital_sign_form = VitalSignForm()
	service_team_form = ServiceTeamForm()
	patient_list = Patient.objects.exclude(inpatient='yes')
	"""
	allocated_patient_array = []
	patient_compliant = OutpatientChiefComplaint.objects.filter(active=True)
	for patient in patient_compliant:
		allocated_patient_array.append(patient.patient.id)
		print('\n', patient.patient,'\n')
	"""

	not_inpatient = Patient.objects.exclude(inpatient='yes')
	not_outpatient = not_inpatient.exclude(id__in=return_triaged_patient())
	complaint_form.fields['patient'].queryset = not_outpatient
#	service_team_form.fields['service_team'].queryset = ServiceTeam.objects.filter( id__in=service_teams)
	room_array = []
	queue_amount_array = []
	rooms = ServiceRoom.objects.all()
	for room in rooms:
		queue = VisitQueue.objects.filter(visit__service_room=room, visit__visit_status='Pending')
		queue_amount = queue.count()
		queue_amount_array.append(queue_amount)
		room_array.append(room)
#		print('yeaaaaaaa',queue_amount,'\n')
	room_zip = zip(room_array, queue_amount_array )
	rq = return_room_queue()
	for a,b in rq:
		print(a,b,'\n')
	if request.method == 'POST':
		arrival_form = PatientArrivalForm(request.POST)
		complaint_form = ChiefComplaintForm(request.POST)
		vital_sign_form = VitalSignForm(request.POST)
		#service_team_form = ServiceTeamForm(request.POST)
		service_recieved = request.POST.get('service_name', None)
		print('It Worked!!!!!!! ',service_recieved,'\n')

		visiting_card = VisitingCardPrice.objects.filter(service__id=int(service_recieved)).last()
		print('card : ',visiting_card,'\n')
		
		if all([arrival_form.is_valid(), complaint_form.is_valid(), vital_sign_form.is_valid()]):
			arrival_model = arrival_form.save(commit=False)
			complaint_model = complaint_form.save(commit=False)
			vital_sign_model = vital_sign_form.save(commit=False)
			#service_team_model = service_team_form.save(commit=False)

			patient = complaint_model.patient

			arrival_model.registered_by = Employee.objects.get(user_profile=request.user, designation__name='Outpatient Triage')
			arrival_model.arrival_date = datetime.now()
			arrival_model.vital_sign = vital_sign_model
			arrival_model.active = True
			arrival_model.patient = patient


			complaint_model.patient = patient
			complaint_model.active =True
			try:
				recent_vital_sign = PatientVitalSign.objects.get(patient=patient,active='active')
				recent_vital_sign.active ='not_active'
				recent_vital_sign.save()
			except:
				print('No Vital Signs')

			vital_sign_model.patient = patient
			vital_sign_model.active = 'active'
			vital_sign_model.registered_on = datetime.now()

			bill = VisitBill()
			bill_detail_model = VisitBillDetail()
			bill_detail_model.bill = bill
			#visiting_card = VisitingCardPrice.objects.filter(service__service_team=service_team_model.service_team).last()
			bill_detail_model.visiting_card = visiting_card
			bill_detail_model.patient = patient
			#bill_detail_model.selling_price = visiting_card.visiting_price

			payment_status = PatientPaymentStatus.objects.get(patient=patient,active=True)
			if payment_status.payment_status == 'Free':
				bill_detail_model.free = True
				#bill_detail_model.selling_price = 0
				service_team = ServiceTeam.objects.filter(service__id=service_recieved)
				for team in service_team:
					service_room_provider = ServiceRoomProvider.objects.filter(service_team=team.team)
					for room in service_room_provider:
						room1 = room.room

						patient_visit = PatientVisit()
						patient_visit.patient = bill_detail_model.patient
						#patient_visit.visit_status = 'Pending'
						patient_visit.payment_status = 'paid'

						patient_visit.service_room = ServiceRoom.objects.get(id=1)
						patient_visit.visit_status = 'Active'
				#patient_visit.save()
				#patient_visit_model.save()
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
	#				new_visit_queue.visit.visit_status = 'Pending'
					new_visit_queue.visit.save()
					new_visit_queue.save()
					#messages.success(request, 'Successfully Assigned!')
	#				return redirect('assign_patient')

				except:
					new_visit_queue = VisitQueue()
					new_visit_queue.visit = patient_visit
					new_visit_queue.queue_number = 1
	#				new_visit_queue.visit.visit_status = 'Pending'
					new_visit_queue.visit.save()
					new_visit_queue.save()
					#messages.success(request, 'Successfully Assigned!')

			elif payment_status.payment_status == 'Discount':
				bill_detail_model.discount = True
				#bill_detail_model.selling_price = visiting_card.discounted_price
				patient_visit = PatientVisit()
				patient_visit.patient = bill_detail_model.patient
				patient_visit.payment_status = 'not_paid'

				patient_visit.service_room = ServiceRoom.objects.get(id=1)
				patient_visit.visit_status = 'Pending'

			elif payment_status.payment_status == 'Insurance':
				bill_detail_model.insurance = True
				#bill_detail_model.selling_price = visiting_card.visiting_card.visiting_price				
				patient_visit = PatientVisit()
				patient_visit.patient = bill_detail_model.patient
				patient_visit.payment_status = 'not_paid'
				patient_visit.service_room = ServiceRoom.objects.get(id=1)

				patient_visit.service_room = room
				patient_visit.visit_status = 'Pending'

			else:
				#bill_detail_model.selling_price = visiting_card.visiting_card.visiting_price
				patient_visit = PatientVisit()
				patient_visit.patient = bill_detail_model.patient
				patient_visit.payment_status = 'not_paid'
				patient_visit.service_room = ServiceRoom.objects.get(id=1)

				patient_visit.service_room = room
				patient_visit.visit_status = 'Pending'
				
#			visit = PatientVisit.objects.get(payment_status='not_paid', patient=bill_detail_model.patient)
			patient_visit.save()
			#new_visit_queue.visit.save()
			#new_visit_queue.save()

			bill.save()
			bill_detail_model.save()


			vital_sign_model.save()
			complaint_model.save()
			arrival_model.save()

			messages.success(request, 'Success')
			return redirect('visiting_card_list')
		
	context = {'arrival_form':arrival_form,
				'vital_form':vital_sign_form,
				'complaint_form':complaint_form,
				'service_team_form':service_team_form,
				'room_zip':room_zip,
				'service_list':service_list,
	}
	return render(request,'outpatient_app/outpatient_triage_form.html',context)

def AdminDashboard(request):
	for room in ServiceRoom.objects.all():
		print(room,'and ',room.id,'\n')
	lab_test_chart = OrderedDict()


# The data for the chart should be in an array wherein each element of the array  is a JSON object having the `label` and `value` as keys.
# Insert the data into the `dataSource['data']` list.
	#thirty_days_ago = today - datetime.timedelta(days=30)
	

# Chart data is passed to the `dataSource` parameter, like a dictionary in the form of key-value pairs.
	dataSource = OrderedDict()

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

	dataSource["chart"] = chartConfig
	dataSource["data"] = []

	lab_test_chart["chart"] = chartConfig
	lab_test_chart["data"] = []

	lab_test_chart["chart"] = {
		"caption":'Lab Tests Taken Today',
		"subCaption":' In Birr',
		"numberSuffix":' Birr',
		'theme':'fusion',
		'yAxisName':' Lab Tests',
	}

# The data for the chart should be in an array wherein each element of the array  is a JSON object having the `label` and `value` as keys.
# Insert the data into the `dataSource['data']` list.
	#thirty_days_ago = today - datetime.timedelta(days=30)
	
	for drug in Dosage.objects.all():
		dispensed_drugs = DrugDispensed.objects.filter(bill_no__drug=drug)
		drug_sum = 0
		if dispensed_drugs:
			for sd in dispensed_drugs:
				price = DrugPrice.objects.get(drug=sd.bill_no.drug,active='active')
				drug_sum = drug_sum + price.selling_price
			print('Drug: ',str(drug), ' Sum: ', drug_sum)
			dataSource["data"].append({"label": str(drug), "value": drug_sum})
	today = datetime2.now()
	rt = Patient.objects.filter(registered_at__day=today.day)
	if rt:
		new_patients_today = rt.count()
	else:
		new_patients_today = 0

	test_list = []
	test_revenue = []
	for t in LaboratoryTestType.objects.all():
		performed_tests = OutpatientLabResult.objects.filter(lab_result__result_type__test_type=t)
		test_sum = 0
		if performed_tests:
			for d in performed_tests:
				price = LaboratoryTestPrice.objects.get(test_type=d.lab_result.result_type.test_type,active=True)
				test_sum = test_sum + price.price
		test_list.append(t)
		test_revenue.append(test_sum)
		lab_test_chart["data"].append({"label": str(t), "value": test_sum})


	team_setting_form = TeamSettingForm()
	column2D = FusionCharts("column2d", "myFirstChart", "550", "550", "myFirstchart-container", "json", dataSource)
	lab_test_chart = FusionCharts("pie2d", "lab_test_chart", "600", "600", "lab_test_container", "json", lab_test_chart)
	#return render(request, 'index.html', {'output': column2D.render()})

	context = {'team_setting_form':team_setting_form,
				'new_patients_today':new_patients_today,
				'output': column2D.render(),
				'lab_test_chart': lab_test_chart.render()	
	}

	return render(request,'outpatient_app/admin_dashboard.html', context)

def GeneralReport(request):

	today = datetime2.now()

	patient_list = Patient.objects.all()
	patient_amount = patient_list.count()
	today_patient_list = patient_list.filter(registered_at__day=today.day)
	today_patient_amount = today_patient_list.count()

	employee_list = Employee.objects.all()
	employee_amount = employee_list.count()
	today_employee_list = employee_list.filter(employed_date__day=today.day)
	today_employee_amount = today_employee_list.count()

	department_list = Department.objects.all()

	if request.htmx:
		request_name = request.GET.get('id')
		print('HOHOHOHOHOOHOHOHO','\n','jsksksks',request_name)
		#dispensed_drugs2 = DrugDispensed.objects.filter(dispensary_id=dispensary_id)
		if request_name == '45':
			print('sfaaffafafaffaf')
			context2 = {'today_patient_list':today_patient_list}
		elif request_name == '46':
			print('dadadfjfafjkf')
			context2 = {'patient_list':patient_list}

		return render(request,'outpatient_app/partials/patient_table_partial.html', context2)

	context = {#'patient_list':patient_list,
				'patient_amount':patient_amount,
				'today_patient_amount':today_patient_amount,

				#'employee_list':employee_list,
				'employee_amount':employee_amount,
				#'today_employee_list':today_employee_list,
				'today_employee_amount':today_employee_amount,
				'department_list':department_list,

	}

	return render(request,'outpatient_app/general_report.html', context)

def EmployeeListReport(request):
	today = datetime2.now()

	patient_list = Patient.objects.all()
	patient_amount = patient_list.count()
	today_patient_list = patient_list.filter(registered_at__day=today.day)
	today_patient_amount = today_patient_list.count()

	employee_list = Employee.objects.all()
	employee_amount = employee_list.count()
	today_employee_list = employee_list.filter(employed_date__day=today.day)
	today_employee_amount = today_employee_list.count()

	department_list = Department.objects.all()
	designation_list = Designation.objects.all()
	if request.htmx:
		request_name = request.GET.get('id')
		print('HOHOHOHOHOOHOHOHO','\n','jsksksks',request_name)
		#dispensed_drugs2 = DrugDispensed.objects.filter(dispensary_id=dispensary_id)
		if request_name == '45':
			print('sfaaffafafaffaf')
			context2 = {'today_patient_list':today_patient_list}
		elif request_name == '46':
			print('dadadfjfafjkf')
			context2 = {'patient_list':patient_list}

		return render(request,'outpatient_app/partials/patient_table_partial.html', context2)

	context = {#'patient_list':patient_list,
				'employee_list':employee_list,
				'department_list':department_list,
				'designation_list':designation_list	
	}

	return render(request,'pharmacy_app/employee_list_report.html', context)

def PharmacyDashboard(request):
# Chart data is passed to the `dataSource` parameter, like a dictionary in the form of key-value pairs.
	dataSource = OrderedDict()

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

	dataSource["chart"] = chartConfig
	dataSource["data"] = []
# The data for the chart should be in an array wherein each element of the array  is a JSON object having the `label` and `value` as keys.
# Insert the data into the `dataSource['data']` list.
	#thirty_days_ago = today - datetime.timedelta(days=30)
	
	for drug in Dosage.objects.all():
		dispensed_drugs = DrugDispensed.objects.filter(bill_no__drug=drug)
		drug_sum = 0
		if dispensed_drugs:
			for sd in dispensed_drugs:
				price = DrugPrice.objects.get(drug=sd.bill_no.drug,active='active')
				drug_sum = drug_sum + price.selling_price
			print('Drug: ',str(drug), ' Sum: ', drug_sum)
			dataSource["data"].append({"label": str(drug), "value": drug_sum})
	today = datetime2.now()
	rt = Patient.objects.filter(registered_at__day=today.day)
	if rt:
		new_patients_today = rt.count()
	else:
		new_patients_today = 0

	team_setting_form = TeamSettingForm()
	column2D = FusionCharts("column2d", "myFirstChart", "1000", "600", "myFirstchart-container", "json", dataSource)
	#return render(request, 'index.html', {'output': column2D.render()})
	context = {'team_setting_form':team_setting_form,
				'new_patients_today':new_patients_today,
				'output': column2D.render()
	}


	return render(request,'outpatient_app/pharmacy_dashboard.html', context)

def LaboratoryDashboard(request):
# Chart data is passed to the `dataSource` parameter, like a dictionary in the form of key-value pairs.
	dataSource = OrderedDict()

# The `chartConfig` dict contains key-value pairs of data for chart attribute
	chartConfig = OrderedDict()
	chartConfig["caption"] = "Lab Tests Today"
	chartConfig["subCaption"] = "In Birr"
	chartConfig["xAxisName"] = "Country"
	chartConfig["yAxisName"] = "Reserves (MMbbl)"
	chartConfig["numberSuffix"] = " Birr"
	chartConfig["theme"] = "fusion"
	chartConfig["numVisiblePlot"] = "8",
	chartConfig["flatScrollBars"] = "1",
	chartConfig["scrollheight"] = "1",

	dataSource["chart"] = chartConfig
	dataSource["data"] = []
# The data for the chart should be in an array wherein each element of the array  is a JSON object having the `label` and `value` as keys.
# Insert the data into the `dataSource['data']` list.
	#thirty_days_ago = today - datetime.timedelta(days=30)
	
	test_list = []
	test_revenue = []
	for t in LaboratoryTestType.objects.all():
		performed_tests = OutpatientLabResult.objects.filter(lab_result__result_type__test_type=t)
		test_sum = 0
		if performed_tests:
			for d in performed_tests:
				price = LaboratoryTestPrice.objects.get(test_type=d.lab_result.result_type.test_type,active=True)
				test_sum = test_sum + price.price
		test_list.append(t)
		test_revenue.append(test_sum)
		dataSource["data"].append({"label": str(t), "value": test_sum})

	test_revenue_zip = zip(test_list,test_revenue)
	today = datetime2.now()
	rt = Patient.objects.filter(registered_at__day=today.day)
	if rt:
		new_patients_today = rt.count()
	else:
		new_patients_today = 0

	team_setting_form = TeamSettingForm()
	column2D = FusionCharts("column2d", "myFirstChart", "1000", "400", "myFirstchart-container", "json", dataSource)
	context = {'output':column2D.render()}
	return render(request,'outpatient_app/labratory_dashboard.html',context)

def AdminSetting(request):
	"""	
	room_queue = VisitQueue.objects.filter(visit__service_room__room ='Room 1')
	print('\n',room_queue.last(),'\n')
	structure_form = HospitalStructureForm()
	if request.method == "POST":
		structure_form = HospitalStructureForm(request.POST)
		if  structure_form.is_valid():
			building_name = structure_form.data['building_name']
	"""
	team_setting_form = TeamSettingForm()
	context = {'team_setting_form':team_setting_form}

	return render(request,'outpatient_app/admin_settings.html', context)

def PharmacySettings(request):

	return render(request,'outpatient_app/pharmacy_settings.html')

def LabSettings(request):

	return render(request,'outpatient_app/lab_settings.html')

def AdminSetting2(request):
	try:
		current_setting = TeamSetting.objects.get(active=True)
		current_setting = current_setting.setting 
	except :		
		current_setting = None
	team_setting_form = TeamSettingForm()
	if request.method == "POST":
		team_setting_form = TeamSettingForm(request.POST)
		try:
			previous_setting = TeamSetting.objects.get(active=True)
			previous_setting.active = False
			previous_setting.save()
		except :
			print('none')

		if  team_setting_form.is_valid():
			setting_model = team_setting_form.save(commit=False)
			setting_model.registered_by = Employee.objects.get(user_profile=request.user, designation__name='Admin')
			setting_model.active = True
			setting_model.save()
			messages.success(request, "Successfully Changed!")
			return redirect('admin_settings2')
	context = {'team_setting_form':team_setting_form,
				'current_setting':current_setting,
			}
	return render(request,'outpatient_app/admin_settings2.html', context)

def ChangeTeamSetting(request):
	if request.method == "POST":
		team_setting_form = TeamSettingForm(request.POST)

		if  team_setting_form.is_valid():
			setting_model = team_setting_form.save(commit=False)
			setting_model.registered_by = Employee.objects.get(user_profile=request.user, designation__name='Admin')
			setting_model.active = True
			try:
				previous_setting = TeamSetting.objects.get(active=True)
				previous_setting.active = False
				previous_setting.save()
			except :
				print('none')

			setting_model.save()
			messages.success(request, "Successful!")
			if setting_model.setting == 'Team':
				return redirect('create_staff_team')
			return redirect('admin_settings2')
		else:
			messages.error(request, str(team_setting_form.errors))
			return redirect('admin_settings2')

def CreateStaffTeam(request):
	staff_team = StaffTeam.objects.all()
	create_form = CreateStaffTeamForm()
	for team in staff_team:
		print(team,'dddddddddddddddddddddddddddddd')
	if request.method == "POST":
		create_form = CreateStaffTeamForm(request.POST)
		
		if  create_form.is_valid():
			team_model = create_form.save(commit=False)
			team_model.registered_on = datetime.now()
			team_model.save()
			messages.success(request, "Successful!")
			return redirect('create_staff_team')
		else:
			messages.error(request,str(create_form.errors))
			return redirect('create_staff_team')

	context = {'staff_team':staff_team,
				'create_form':create_form,
			}
	return render(request,'outpatient_app/create_staff_team.html', context)

def HospitalStructure(request):
	room_queue = VisitQueue.objects.filter(visit__service_room__room ='Room 1')
	print('\n',room_queue.last(),'\n')
	structure_form = HospitalStructureForm()
	if request.method == "POST":
		structure_form = HospitalStructureForm(request.POST)
		if  structure_form.is_valid():
			building_name = structure_form.data['building_name']
			room_amount =int( structure_form.data['room_amount'])
			building_model = ServiceBuilding()
			building_model.building_name = building_name
			building_model.save()				
			for i in range(1,room_amount + 1):
				room_model = ServiceRoom()
				room_model.room = "Room " + str(i)
				room_model.building = building_model
				room_model.save()
			messages.success(request, str(building_name) + " with " + str(room_amount) + " has been created!")

	context = {'structure_form':structure_form}
	return render(request,'outpatient_app/hospital_structure.html',context)
	
def BuildingList(request):
	buildings = ServiceBuilding.objects.all()
	context = {'buildings':buildings}
	return render(request,'outpatient_app/building_list.html',context)

def RoomList(request,pk):
	rooms = ServiceRoom.objects.filter(building_id=pk)
	context = {'rooms':rooms}
	return render(request,'outpatient_app/room_list.html',context)


def EditRoom(request, pk):
	room = ServiceRoom.objects.get(id=pk)
	edit_room_form = EditRoomForm(initial={'room':room.room})
	if request.method == "POST":
		edit_room_form = EditRoomForm(request.POST)
		if  edit_room_form.is_valid:
			room_form = edit_room_form.save(commit=False)
			room.room= room_form.room
			room.save()
	context = {'edit_room_form':edit_room_form}
	return render(request,'outpatient_app/edit_room.html',context)

def PatientList(request):
	patient_list = Patient.objects.all()
	context = {'patient_list':patient_list}
	return render(request,'outpatient_app/patient_list.html',context)

def PatientAllergyFormPage(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	allergy_form = PatientAllergyForm()
	if request.method == 'POST':
		allergy_form = PatientAllergyForm(request.POST)
		if allergy_form.is_valid():
			allergy_model = allergy_form.save(commit=False)
			allergy_model.patient = patient
			allergy_model.registered_on = datetime.now()
			allergy_model.active = 'active'
			allergy_model.save()
			messages.success(request,'Successfully Submitted')
			return redirect('outpatient_list')
	context = {'allergy_form':allergy_form}
	return render(request,'outpatient_app/patient_allergy_form.html',context)

def PatientHabitFormPage(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	habit_form = PatientHabitForm()
	if request.method == 'POST':
		habit_form = PatientHabitForm(request.POST)
		if habit_form.is_valid():
			habit_model = habit_form.save(commit=False)
			habit_model.patient = patient
			habit_model.registered_on = datetime.now()
			habit_model.save()
			messages.success(request,'Successfully Submitted')
			return redirect('outpatient_list')
	context = {'habit_form':habit_form}
	return render(request,'outpatient_app/patient_habit_form.html',context)

def PatientMedicalConditionFormPage(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	condition_form = PatientMedicalConditionForm()
	if request.method == 'POST':
		condition_form = PatientMedicalConditionForm(request.POST)
		if condition_form.is_valid():
			condition_model = condition_form.save(commit=False)
			condition_model.patient = patient
			condition_model.registered_date = datetime.now()
			condition_model.save()
			messages.success(request,'Successfully Submitted')
	context = {'condition_form':condition_form,
				'patient':patient}
	return render(request,'outpatient_app/patient_medical_condition_form.html',context)
	

def ScheduleAppointment(request):

	return render(request,'outpatient_app/schedule_appointment.html',context)

def AssignPatient(request):
	room_array = []
	queue_amount_array = []
	rooms = ServiceRoom.objects.all()
	for room in rooms:
		queue = VisitQueue.objects.filter(visit__service_room=room, visit__visit_status='Pending')
		queue_amount = queue.count()
		queue_amount_array.append(queue_amount)
		room_array.append(room)
#		print('yeaaaaaaa',queue_amount,'\n')
	q_zip = zip(room_array, queue_amount_array )

	assigned_patients = []
	assign_patient_form = AssignPatientForm()
	assigned_visits = PatientVisit.objects.filter(visit_status='Pending', payment_status='paid')
	for visit in assigned_visits:
		assigned_patients.append(visit.patient.id)
	unassigned_patients = Patient.objects.filter(id__in=assigned_patients)
	assign_patient_form.fields["patient"].queryset = Patient.objects.filter(id__in=assigned_patients)

	if request.method == "POST":
		assign_patient_form = AssignPatientForm(request.POST)
		if  assign_patient_form.is_valid:
			patient_visit_model = assign_patient_form.save(commit=False)
			patient_visit = PatientVisit.objects.get(patient=patient_visit_model.patient, visit_status='Pending', payment_status='paid')
			patient_visit.service_room = patient_visit_model.service_room
			patient_visit.visit_status = 'Active'
			patient_visit.save()
#			patient_visit_model.save()
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
#				new_visit_queue.visit.visit_status = 'Pending'
				new_visit_queue.visit.save()
				new_visit_queue.save()
				messages.success(request, 'Successfully Assigned!')
				return redirect('assign_patient')

			except:
				new_visit_queue = VisitQueue()
				new_visit_queue.visit = patient_visit
				new_visit_queue.queue_number = 1
#				new_visit_queue.visit.visit_status = 'Pending'
				new_visit_queue.visit.save()
				new_visit_queue.save()
				messages.success(request, 'Successfully Assigned!')
				return redirect('assign_patient')			
		else:
			print('\n',assign_patient_form.errors)
	context = {'assign_form':assign_patient_form, 'q_zip':q_zip}			
	return render(request,'outpatient_app/assign_patient.html',context)


def RoomQueue(request,pk):
	room_queue = VisitQueue.objects.filter(visit__service_room_id = pk, visit__visit_status='Pending').order_by('queue_number')
	print(room_queue.first())
	room = ServiceRoom.objects.get(id=pk)
	context = {'room_queue':room_queue,'room':room, 'room_pk':pk}
	return render(request,'outpatient_app/room_queue.html',context)



def DisplayRoomAvailibility(request):
	room_array = []
	queue_amount_array = []
	rooms = ServiceRoom.objects.all()
	for room in rooms:
		queue = VisitQueue.objects.filter(visit__service_room=room)
		queue_amount = queue.count()
		queue_amount_array.append(queue_amount)
		room_array.append(room)
		#print('yeaaaaaaa',queue_amount,'\n')
	q_zip = zip(room_array, queue_amount_array )
	print(request.user)
	service_provider = ServiceProvider.objects.get(service_provider__user_profile=request.user)
	if service_provider.service_provider.user_profile == request.user:
		print(service_provider.service, '\n', service_provider.service_provider)
	context = {'room_array':room_array, 'queue_amount_array':queue_amount_array, 'q_zip':q_zip}
	return render(request,'outpatient_app/room_availibility.html', context)

def ViewRoomSchedule(request):

	return render(request,'outpatient_app/assign_patient.html',context)

def ChangeQueueOrder(request, pk, room_pk):
	patient_queue = VisitQueue.objects.get(id=pk)
	queue_form = ChangeQueueOrderForm()
	room_queue = VisitQueue.objects.filter(visit__service_room=patient_queue.visit.service_room)
	

	if request.method == 'POST':
		queue_form = ChangeQueueOrderForm(request.POST)
		if queue_form.is_valid():
			queue_number = int(queue_form.data['queue_number'])
			if queue_number < patient_queue.queue_number:
				queue_range_array = []
				for queue_no in range(queue_number, patient_queue.queue_number):
					queue_range_array.append(queue_no)
					#print(queue_number,'\n')
				before_queue_patients = VisitQueue.objects.filter(queue_number__in=queue_range_array, visit__service_room=patient_queue.visit.service_room)
				for patient_q in before_queue_patients:
					patient_q.queue_number = patient_q.queue_number + 1
					patient_q.save()
					print(patient_q.queue_number, '\n')
				patient_queue.queue_number = queue_number
				patient_queue.save()
				return redirect('room_queue', room_pk)

			elif room_queue.last().queue_number + 1 > queue_number > patient_queue.queue_number:
				queue_range_array = []
				for queue_no in range(patient_queue.queue_number + 1 , queue_number + 1):
					queue_range_array.append(queue_no)

				after_queue_patients = VisitQueue.objects.filter(queue_number__in=queue_range_array, visit__service_room=patient_queue.visit.service_room)					
				for queue in after_queue_patients:
					queue.queue_number = queue.queue_number - 1
					queue.save()
				patient_queue.queue_number = queue_number
				patient_queue.save()
				return redirect('room_queue', room_pk)
			else:
				messages.error(request, 'Fill a number within bounds!')

	context = {'queue_form':queue_form, 'patient':patient_queue.visit.patient}
	return render(request,'outpatient_app/change_queue_order.html',context)

def ReassignRoom(request, pk, room_pk):
	reassign_form = ReassignRoomForm()
	original_room = ServiceRoom.objects.get(id=room_pk)
	if request.method == 'POST':
		reassign_form = ReassignRoomForm(request.POST)
		if reassign_form.is_valid():
			room = reassign_form.save(commit=False)
			patient_visit_model = VisitQueue.objects.get(id=pk)
#			print('first room:', patient_visit_model.visit.service_room,'\n')
#			print('second room:', room.service_room,'\n')

			patient_visit_model.visit.service_room = room.service_room
#			print('third room:', patient_visit_model.visit.service_room,'\n')

			original_room_queue = VisitQueue.objects.filter(visit__service_room=original_room).order_by('queue_number')
			
			queue_range_array = []
			for  queue in range(patient_visit_model.queue_number + 1, original_room_queue.last().queue_number + 1 ):
				print('\n',queue)
				queue_range_array.append(queue)
			queue_patients = VisitQueue.objects.filter(queue_number__in=queue_range_array, visit__service_room=original_room)
			for queue in queue_patients:
				queue.queue_number = queue.queue_number - 1
				queue.save()	
				

			room_queue = VisitQueue.objects.filter(visit__service_room=room.service_room).order_by('queue_number')
			try:
				last_queue_number = room_queue.last().queue_number
				patient_visit_model.queue_number = last_queue_number + 1			
				patient_visit_model.visit.save()
				
			except:
				patient_visit_model.queue_number = 1			
				patient_visit_model.visit.save()

			patient_visit_model.save()
			return redirect('room_queue', room.service_room.id)
	context = {'reassign_form':reassign_form}
	return render(request,'outpatient_app/reassign_room.html',context)
"""
def DoctorQueue(request):
	acs = OutpatientChiefComplaint.objects.all()
	for a in acs:
		a.active=False
		a.save()	
	print(request.user)
	service_team = ServiceTeam.objects.filter(service_provider__user_profile=request.user)
	#service_provider = ServiceProvider.objects.get(service_provider__user_profile=request.user)
	room_array = []
	for team in service_team:
		room = ServiceRoomProvider.objects.filter(service_team=team.team)
		for room in room:
			room_array.append(room.room)

	for room in room_array:
		visit_queue = VisitQueue.objects.filter(visit__service_room=room.room).exclude(visit__visit_status='Ended').order_by('queue_number')
	arrival_detail_array = []
	for visit in visit_queue:
		arrival_detail = PatientArrivalDetail.objects.filter(patient=visit.visit.patient, active=True).last()		
		print(visit.queue_number,'s')
		visit_array.append(visit)
		arrival_detail_array.append(arrival_detail)
	visit_zip = zip(visit_array,arrival_detail_array)
#	for v,s in visit_zip:
#		print(v,s,'\n')
	context = {'visit_zip':visit_zip, 'room':room}
	return render(request,'outpatient_app/doctor_queue.html',context)
"""

#Original Queue
def DoctorQueue(request):
	service_team = ServiceTeam.objects.get(service_provider__user_profile=request.user)
	#service_provider = ServiceProvider.objects.get(service_provider__user_profile=request.user)
	room = ServiceRoomProvider.objects.get(service_team=service_team.team)
	print(room.room)
	visit_queue = VisitQueue.objects.filter(visit__service_room=room.room).exclude(visit__visit_status='Ended').order_by('queue_number')
	visit_array = []
	arrival_detail_array = []
	for visit in visit_queue:
		arrival_detail = PatientArrivalDetail.objects.filter(patient=visit.visit.patient, active=True).last()		
		print(visit.queue_number,'s')
		visit_array.append(visit)
		arrival_detail_array.append(arrival_detail)
	visit_zip = zip(visit_array,arrival_detail_array)
#	for v,s in visit_zip:
#		print(v,s,'\n')
	context = {'visit_zip':visit_zip, 'room':room}
	return render(request,'outpatient_app/doctor_queue.html',context)

def OutpatientMedicalNotePage(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	arrival_detail = PatientArrivalDetail.objects.filter(patient=patient, active=True).last()
	intervention_list = OutpatientIntervention.objects.filter(patient=patient,visit__visit_status='Active')
	visit = PatientVisit.objects.filter(patient = patient).exclude(visit_status='Ended').last()
	medication_list = OutpatientMedication.objects.filter(visit=visit, patient=patient)
	lab_result_list = OutpatientLabResult.objects.filter(visit=visit, patient=patient)
	rad_result_list = OutpatientRadiologyResult.objects.filter(visit=visit,patient=patient)
	service_list = ServiceBillDetail.objects.filter(visit=visit)
	complaint = OutpatientChiefComplaint.objects.filter(active=True, patient=patient).last()
	#print('\n',complaint.complaint,'\n')
	vital_sign = PatientVitalSign.objects.filter(active='active',patient=patient).last()
	print('\n',vital_sign,'\n')

	service_form = ServiceForm()
	medical_note_form = OutpatientMedicalNote()
	intervention_form = OutpatientInterventionForm()
	note_form = OutpatientMedicalNote()
	if request.method == 'POST':
		intervention_form = OutpatientInterventionForm(request.POST)
		if intervention_form.is_valid():
			intervention_model = intervention_form.save(commit=False)
			intervention_model.patient = patient
			intervention_model.service_provider = Employee.objects.get(user_profile=request.user, designation__name='Doctor')
			intervention_model.registered_on = datetime.now()
			intervention_model.save()
			messages.success(request,'Successfully Registered!')
			return redirect('outpatient_medical_note', patient.id)
		else:
			messages.error(request,str(intervention_form.errors))
			return redirect('outpatient_medical_note', patient.id)

	context = {'intervention_form':intervention_form,
				'note_form':note_form,
				'patient':patient,
				'arrival_detail':arrival_detail,
				'medical_note_form':medical_note_form,
				'service_form':service_form,
				'medication_list':medication_list,
				'lab_result_list':lab_result_list,
				'service_list':service_list,
				'rad_result_list':rad_result_list,
				'complaint':complaint,
				'vital_sign':vital_sign,

	}
	return render(request,'outpatient_app/opd_doctor_note.html',context)


def OpdInvestigation(request, patient_id):
	patient = Patient.objects.get(id=patient_id)
	question_form = QuestionForPatientForm()
	response_form = OpdPatientResponseForm()
	response_form2 = OpdPatientResponseForm2()

	if request.method == 'POST':
		question_form = QuestionForPatientForm(request.POST)
		response_form2 = OpdPatientResponseForm2(request.POST)
		if question_form.is_valid():
			if response_form2.is_valid():

				question_model = question_form.save(commit=False)
				response_model = response_form2.save(commit=False)

				question_model.registered_by = Employee.objects.get(user_profile=request.user, designation__name='Doctor')
				question_model.registered_on = datetime.now()
				response_model.question = question_model
				response_model.visit = PatientVisit.objects.filter(patient=patient, visit_status='Active').last()
				response_model.registered_by = Employee.objects.get(user_profile=request.user, designation__name='Doctor')
				response_model.registered_on = datetime.now()

				question_model.save()
				response_model.save()
				return redirect('outpatient_medical_note',patient.id)
				messages.success(request,'successful!')
			else:
				messages.error(request,str(response_form2.errors))

		else:
			messages.error(request,str(question_form.errors))
	context = {'question_form':question_form,
				'response_form':response_form,
				'response_form2':response_form2,
				'patient':patient,
	}
	return render(request, 'outpatient_app/opd_investigation.html',context)

#This function saves responses made by patient 
def SavePatientResponseForm(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	if request.method == 'POST':
		response_form = OpdPatientResponseForm(request.POST)
		if response_form.is_valid():

			response_model = response_form.save(commit=False)

			response_model.visit = PatientVisit.objects.filter(patient=patient, visit_status='Active').last()
			response_model.registered_by = Employee.objects.get(user_profile=request.user, designation__name='Doctor')
			response_model.registered_on = datetime.now()
			response_model.save()
			messages.success(request,'Successfully Registered!')
			return redirect('outpatient_medical_note', patient.id)
		else:
			messages.error(request,str(note_form.errors))
			return redirect('outpatient_medical_note', patient.id)

#This function saves notes made by doctor 
def SaveOutpatientNote(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	if request.method == 'POST':
		note_form = OutpatientMedicalNote(request.POST)
		if note_form.is_valid():
			note_model = note_form.save(commit=False)
			note_model.patient = patient
			note_model.service_provider = Employee.objects.get(user_profile=request.user, designation__name='Doctor')
			note_model.registered_on = datetime.now()
			note_model.save()
			messages.success(request,'Successfully Registered!')
			return redirect('outpatient_medical_note', patient.id)
		else:
			messages.error(request,str(note_form.errors))
			return redirect('outpatient_medical_note', patient.id)

def SaveServiceBill(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	if request.method == 'POST':
		service_form = ServiceForm(request.POST)

		if service_form.is_valid():
			service_bill_detail = service_form.save(commit=False)
			service_bill_detail.patient = patient
			#bill = ServiceBill()
			#service_bill_detail.bill = bill
			service_bill_detail.visit = PatientVisit.objects.get(visit_status='Active',patient=patient)
			#bill.save()
			payment_status = PatientPaymentStatus.objects.get(patient=patient,active=True)
			price = ServicePrice.objects.get(service=service_bill_detail.service,active=True)
			service_bill_detail.service_price = price.price

			service_bill.registered_by = Employee.objects.get(user_profile=request.user, designation__name='Cashier')
			today = datetime.today()
			#today = now.day
			if CashierDebt.objects.filter(cashier__user_profile=request.user, reconciled=False, date=today).last():
				cashier_debt = CashierDebt.objects.get(cashier__user_profile=request.user, reconciled=False) 
				cashier_debt.cash_debt = cashier_debt.cash_debt + price.price 
			else:
				cashier_debt = CashierDebt()
				cashier_debt.cashier = 	Employee.objects.get(user_profile=request.user, designation__name='Cashier')
				cashier_debt.cash_debt = price.price
				cashier_debt.date = today

			if payment_status.payment_status=='Free':
				service_bill_detail.free = True
				service_bill_detail.discount = False
				service_bill_detail.insurance = False
				service_bill_detail.credit = False
				service_bill_detail.service_price = 0

			elif payment_status.payment_status == 'Insurance':
				service_bill_detail.free = False
				service_bill_detail.discount = False
				service_bill_detail.insurance = True
				service_bill_detail.credit = False

			elif payment_status.payment_status == 'discount':
				service_bill_detail.free = False
				service_bill_detail.discount = True
				service_bill_detail.insurance = False
				service_bill_detail.credit = False

			else:
				service_bill_detail.free = False
				service_bill_detail.discount = False
				service_bill_detail.insurance = False
				service_bill_detail.credit = False

			service_bill_detail.registered_on = datetime.now()
			cashier_debt.save()
			service_bill_detail.save()
	
			messages.success(request,'Successfully Registered!')
			return redirect('outpatient_medical_note', patient.id)
		else:
			messages.error(request,str(service_form.errors))
			return redirect('outpatient_medical_note', patient.id)

	"""
		
	if service_provider.service_provider.user_profile == request.user:
		print(service_provider.service, '\n', service_provider.service_provider)
		service_provider = 
	return render(request,'outpatient_app/change_queue_order.html',context)
	"""
def ViewPatientSymptom(request, patient_id):
	try:
		symptom = PatientSymptom.objects.get(patient_id=patient_id, active='active')
		symptom = symptom.symptom
	except:
		symptom = 'No symptom has been recorded for this patient.'
	try:
		anthropometry = PatientAnthropometry.objects.get(patient_id=patient_id)
	except:
		anthropometry = None	
	context = {'symptom':symptom,
				'anthropometry':anthropometry}
	return render(request,'outpatient_app/view_patient_symptom.html',context)

def PatientAnthropometry(request):
	patient_anthropometry_form = PatientAnthropometryForm()
	if request.method == 'POST':
		patient_anthropometry_form = PatientAnthropometryForm(request.POST)
		if patient_anthropometry_form.is_valid():
			patient_anthropometry_model = patient_anthropometry_form.save()
			return redirect('vital_sign_form',  patient_anthropometry_model.patient.id)
#			messages.success(request,'Patient registered successfully!')
	context = {'patient_anthropometry_form':patient_anthropometry_form}
	return render(request,'outpatient_app/patient_anthropometry.html',context)

def FillPatientSymptom(request, patient_id):
	patient = Patient.objects.get(id=patient_id)
	patient_symptom_form = PatientSymptomForm(initial = {'patient':patient})
	if request.method == 'POST':
		patient_symptom_form = PatientSymptomForm(request.POST)
		if patient_symptom_form.is_valid():
			patient_symptom_model = patient_symptom_form.save(commit=False)
			patient_symptom_model.active = 'active'
			patient_symptom_model.save()
			return redirect('assign_patient')
#			messages.success(request,'Patient registered successfully!')

	context = {'patient_symptom_form':patient_symptom_form}
	return render(request, 'outpatient_app/patient_symptom.html',context)

def PatientPrescription(request, patient_id, patient_visit_id, room_id, visit_queue_id):
	patient = Patient.objects.get(id=patient_id)
	room = ServiceRoom.objects.get(id=room_id)
	prescription_form = PatientPrescriptionForm()
	print(request.user)
	if request.method == 'POST':
		prescription_form = PatientPrescriptionForm(request.POST)
		if prescription_form.is_valid():			
			drug_prescription_model = prescription_form.save(commit=False)
			drug_prescription_model.patient = patient 
			drug_prescription_model.prescriber = request.user #Assign user(doctor) to prescriber field in DrugPrescription model
			drug_prescription_model.registered_on = datetime.now()
			drug_prescription_model.save()
		
			patient_visit = PatientVisit.objects.get(id=patient_visit_id)
			patient_visit.visit_status = 'Ended'
			patient_visit.save()
			print(' success 1','\n')
			try:
				patient_symptom = PatientSymptom.objects.get(patient=patient)
				patient_symptom.active = 'not_active'
				patient_symptom.save()
				print(' success 2 ', '\n')
			except:
				print('no patient symptom')	
				messages.success(request,'Successfully Prescribed!')

			patient_medication = InpatientMedication()
			patient_medication.patient = patient
			patient_medication.stay_duration = stay_duration

			patient_medication.diagnosis = drug_prescription_model.diagnosis
			patient_medication.drug_prescription = drug_prescription_model
			patient_medication.doctor = Employee.objects.get(user_profile=request.user, designation__name='Nurse')
#			patient_medication.date = date 
			patient_medication.save()
			return redirect('doctor_queue')
		else:
			print('error: ', prescription_form.errors)
	else:
		print('Not POST')
	context = {'prescription_form':prescription_form}
	return render(request, 'outpatient_app/patient_prescription2.html', context)

def PatientSurgeryHistoryFormPage(request, patient_id):
	patient = Patient.objects.get(id=patient_id)
	surgery_form = PatientSurgeryHistoryForm()
	if request.method == 'POST':
		surgery_form = PatientSurgeryHistoryForm(request.POST)
		if surgery_form.is_valid():			
			surgery_history_model = surgery_form.save(commit=False)
			surgery_history_model.patient = patient
			surgery_history_model.registered_by = request.user
			surgery_history_model.registered_on = datetime.now()
			surgery_history_model.save()
			messages.success(request, "Successful! ")
	context = {'surgery_form':surgery_form}
	return render(request, 'outpatient_app/patient_surgery_history_form.html', context)
"""
def PatientAllergyFormPage(request):

def PatientHabit(request):
"""
def PatientRecord(request, patient_id):
	patient = Patient.objects.get(id=patient_id)
	try:
		patient_medication = InpatientMedication.objects.filter(patient=patient)
	except:
		patient_medication = None
	try:
		patient_medical_condition = InpatientMedicalCondition.objects.filter(patient=patient)
	except:
		patient_medical_condition = None
	pateint_surgery = PatientSurgeryHistory.objects.filter(patient=patient)
	patient_allergy = PatientAllergy.objects.filter(patient=patient)

	context = {'patient':patient,
				'patient_medication':patient_medication,
				'patient_medical_condition':patient_medical_condition,
				'pateint_surgery':pateint_surgery,
				'patient_allergy':patient_allergy
				}

	return render(request, 'outpatient_app/patient_profile1.html', context)

def VitalSignFormPage(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	vital_form = VitalSignForm()
	if request.method == 'POST':
		vital_form = VitalSignForm(request.POST)
		if vital_form.is_valid():
			vital_sign_model = vital_form.save(commit=False)
			vital_sign_model.patient=Patient.objects.get(id=patient_id)
			try:
				last_sign = PatientVitalSign.objects.get(patient=patient, active='active')
				last_sign.active = 'not_active'
				print('\n', 'Done!')
				last_sign.save()
			except:
				last_sign = None
			vital_sign_model.active = 'active'
			vital_sign_model.save()
			messages.success(request, ' Successfully Assigned!')
			redirect('patient_symptom', patient_id)
	context = {'vital_form':vital_form}
	return render(request, 'outpatient_app/vital_sign_form.html', context)

def PatientMedicalConditionPage(request, patient_id):
	patient = Patient.objects.get(id=patient_id)
	try:
		patient_medical_condition = PatientMedicalCondition.objects.filter(patient=patient)
		
	except:
		patient_medical_condition = None
		print('None')
	context = {'patient':patient,
				'patient_medical_condition':patient_medical_condition}
	
	return render(request, 'outpatient_app/patient_medical_condition.html', context)

def AssignServiceProvider(request):
	assign_form = AssignServiceProviderForm()

	assigned_providers = []
	assign_form = AssignServiceProviderForm()
	assigned_visits = ServiceRoomProvider.objects.all()
	for visit in assigned_visits:
		assigned_providers.append(visit.service_team.id)
	unassigned_providers = ServiceTeam.objects.exclude(id__in=assigned_providers)
	assign_form.fields["service_team"].queryset = ServiceTeam.objects.exclude(id__in=assigned_providers)

	if request.method == 'POST':
		assign_form = AssignServiceProviderForm(request.POST)
		if assign_form.is_valid():
			service_provider_room = assign_form.save()
			messages.success(request, ' Successfully Assigned!')
	context = {'assign_form':assign_form}
	return render(request, 'outpatient_app/assign_service_provider.html', context)

def AssignServiceTeam(request):
	assign_form = AssignServiceTeamForm()
	"""
	assigned_providers = []
	assigned_visits = ServiceRoomProvider.objects.all()
	for visit in assigned_visits:
		assigned_providers.append(visit.service_team.id)
	unassigned_providers = ServiceProvider.objects.exclude(id__in=assigned_providers)
	assign_form.fields["service_provider"].queryset = ServiceProvider.objects.exclude(id__in=assigned_providers)
	"""
	if request.method == 'POST':
		assign_form = AssignServiceTeamForm(request.POST)
		if assign_form.is_valid():
			service_team = assign_form.save()
			messages.success(request, ' Successfully Assigned!')
	context = {'assign_form':assign_form}
	return render(request, 'outpatient_app/assign_service_team.html', context)

def AddFollowUp(request, patient_id):
	patient = Patient.objects.get(id=patient_id)
	visit = PatientVisit.objects.filter(patient = patient).exclude(visit_status='Ended').last()

	follow_up_form = PatientFollowUpForm()
	if request.method == 'POST':
		follow_up_form = PatientFollowUpForm(request.POST)
		if follow_up_form.is_valid():
			follow_up_model = follow_up_form.save(commit=False)
			follow_up_model.patient = patient
			follow_up_model.ordered_by = Employee.objects.get(user_profile=request.user, designation__name='Doctor')
			follow_up_model.visit = visit
			follow_up_model.registered_on = datetime.now()
			follow_up_model.save()
			messages.success(request, 'Successful!')
			return redirect('doctor_queue')
	context = {'follow_up_form':follow_up_form}
	return render(request, 'outpatient_app/add_follow_up.html', context)


def DischargeOutpatientFormPage(request, patient_id):
	patient = Patient.objects.get(id=patient_id)
	visit = PatientVisit.objects.filter(patient = patient).exclude(visit_status='Ended').last()

	discharge_form = DischargeOutpatientForm()
	if request.method == 'POST':
		discharge_form = DischargeOutpatientForm(request.POST)
		if discharge_form.is_valid():
			discharge_model = discharge_form.save(commit=False)
			discharge_model.patient = patient
			discharge_model.discharged_by = Employee.objects.get(user_profile=request.user, designation__name='Doctor')
			discharge_model.visit = visit
			discharge_model.registered_on = datetime.now()
			discharge_model.save()
			messages.success(request, 'Successful!')
			return redirect('discharge_outpatient', patient.id)
	context = {'discharge_form':discharge_form,'patient_id': patient_id}
	return render(request, 'outpatient_app/discharge_outpatient_form.html', context)

def DischargeOutpatient(request, patient_id):
	patient = Patient.objects.get(id=patient_id)

	all_visit = PatientVisit.objects.filter(patient=patient).exclude(visit_status='Ended')
	for visit in all_visit:
		visit.visit_status='Ended'
		visit.save()
	#stay_duration.leave_date = datetime.now()

	arrival_detail = PatientArrivalDetail.objects.filter(patient = patient, active=True)
	for detail in arrival_detail:
		detail.active=False
		detail.save()

	all_complaint = OutpatientChiefComplaint.objects.filter(patient=patient,active=True)
	for complaint in all_complaint:
		complaint.active=False
		complaint.save()
	messages.success(request, 'Successful!')
	return redirect('add_follow_up',patient_id)

def OPDReport(request):
	dataSource = OrderedDict()
	used_service_chart = OrderedDict()
	dispensary_supply_chart = OrderedDict()
	discharge_chart = OrderedDict()
	payment_status_chart = OrderedDict()
	occupancy_chart = OrderedDict()

	building_revenue_chart = OrderedDict()

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

	used_service_chart["chart"] = chartConfig
	used_service_chart["chart"] = {
		"caption":'Total Used Resource By Patient',
		"subCaption":'In Unit',
		"numberSuffix":'Units',
		'theme':'fusion',
		'yAxisName':'Number Of Patients',
	}
	used_service_chart["data"] = []

	dispensary_supply_chart["chart"] = {
		"caption":'Total Drugs Supplied',
		"subCaption":'In Unit',
		"numberSuffix":'Units',
		'theme':'fusion',
	}

	dispensary_supply_chart["data"] = []

	payment_status_chart["chart"] = {
		"caption":'Admission By Payment status',
		"subCaption":'In Unit',
		"numberSuffix":'Patients',
		'theme':'fusion',
		'yAxisName':'Number Of Patients',
	}
	payment_status_chart["data"] = []

	discharge_chart["chart"] = chartConfig
	discharge_chart["chart"] = {
		"caption":'Patients By Discharge Condition',
		"subCaption":' In Unit',
		"numberSuffix":' Patients',
		'theme':'fusion',
		'yAxisName':'Patients',
	}
	discharge_chart["data"] = []

	occupancy_chart["chart"] = chartConfig
	occupancy_chart["chart"] = {
		"caption":'Room Occupancy',
		"subCaption":' In Unit',
		"numberSuffix":' Rooms',
		'theme':'fusion',
		'yAxisName':' Rooms',
	}
	occupancy_chart["data"] = []

	building_revenue_chart["chart"] = chartConfig
	building_revenue_chart["chart"] = {
		"caption":'Revenue By Building Unit',
		"subCaption":' In Birr',
		"numberSuffix":' Birr',
		'theme':'fusion',
		'yAxisName':' Buildings',
	}
	building_revenue_chart["data"] = []

	start_date = datetime.strptime(request.GET.get('start_date') or '1970-01-01', '%Y-%m-%d')
	end_date = datetime.strptime(request.GET.get('end_date') or str(datetime.now().date()),  '%Y-%m-%d')
	today =  str(datetime.now().date()),  '%Y-%m-%d'

#	lab_section = int(self.request.GET.get('lab_section', '0'))
	filtered_room_id = int(request.GET.get('room','0')) or 'None'
	filtered_sex = int(request.GET.get('sex','0')) or 'None'

	print('here is: ',filtered_room_id)

	visit = PatientVisit.objects.filter(patient__isnull=False,registered_on__range=[start_date,end_date])

	medication = OutpatientMedication.objects.filter(visit__isnull=False, registered_on__range=[start_date,end_date]).values('visit__id').distinct()
	lab_test = OutpatientLabResult.objects.filter(visit__isnull=False, registered_on__range=[start_date,end_date]).values('visit__id').distinct()
	rad_test = OutpatientRadiologyResult.objects.filter(visit__isnull=False, registered_on__range=[start_date,end_date]).values('visit__id').distinct()

	if filtered_room_id == 'None' or filtered_room_id == '0':
		print('do nothing')
	else:
		medication = medication.filter( visit__service_room=ServiceRoom.objects.get(id=filtered_room_id))
		lab_test = lab_test.filter(visit__service_room=ServiceRoom.objects.get(id=filtered_room_id))
		rad_test = rad_test.filter(visit__service_room=ServiceRoom.objects.get(id=filtered_room_id))

	if filtered_sex == 'MALE' or filtered_sex =='FEMALE':
		if filtered_sex == 'MALE':
			medication = medication.filter(patient__sex='MALE',visit__isnull=False, visit__service_room=ServiceRoom.objects.get(id=filtered_room_id)).values('visit__id').distinct()
			lab_test = lab_test.filter(patient__sex='MALE',visit__isnull=False, registered_on__range=[start_date,end_date]).values('visit__id').distinct()
			rad_test = rad_test.filter(patient__sex='MALE',visit__isnull=False, registered_on__range=[start_date,end_date]).values('visit__id').distinct()

		if filtered_sex == 'FEMALE':
			medication = medication.filter(patient__sex='FEMALE',visit__isnull=False, visit__service_room=ServiceRoom.objects.get(id=filtered_room_id)).values('visit__id').distinct()
			lab_test = lab_test.filter(patient__sex='FEMALE',visit__isnull=False, registered_on__range=[start_date,end_date]).values('visit__id').distinct()
			rad_test = rad_test.filter(patient__sex='FEMALE',visit__isnull=False, registered_on__range=[start_date,end_date]).values('visit__id').distinct()

	used_service_chart["data"].append({"label": "Taken Medication", "value": medication.count()})
	used_service_chart["data"].append({"label": "Taken Lab Test", "value": lab_test.count()})
	used_service_chart["data"].append({"label": "Taken Rad Test", "value": rad_test.count()})
	used_service_chart["data"].append({"label": "Admitted To Ward", "value": 7})



	room = ServiceRoom.objects.all()
	sex = ['MALE','FEMALE']
	payment_status = ['Insurance','Free','Credit','Default']

	ps = PatientPaymentStatus.objects.first()

	payment_status_chart["data"].append({"label": 'Insurance', "value": ps.insurancePatientAmount})
	payment_status_chart["data"].append({"label": 'Free', "value": ps.freePatientAmount})
	payment_status_chart["data"].append({"label": 'Discount', "value": ps.discountPatientAmount})
	payment_status_chart["data"].append({"label": 'Default', "value": ps.defaultPatientAmount})

	#assign_to_ward
	#
	#print('firssss:',count,'\n','seccc',medication.count())

	#Average Usage
	#visit = PatientVisit.objects.filter(patient__isnull=False).distinct('patient__id')
	#visit = OutpatientMedication.objects.filter(patient__isnull=False).values('visit').distinct()
	#medication = OutpatientMedication.objects.filter(visit__isnull=False).values('visit__id').distinct()
	#for m in visit:
	#	print(m,'\n')	
	if visit.count()==0:	
		average_medication = 0
		average_lab_test = 0	
		average_xray_test = 0
	else:
		average_medication = medication.count()/visit.count()
		average_lab_test = lab_test.count() / visit.count()	
		average_xray_test = rad_test.count()/visit.count()

	total_discharge = OutpatientDischargeSummary.objects.filter(patient__isnull=False).count() 
	follow_up_discharge = FollowUp.objects.all().count()
	completed_discharge = total_discharge - follow_up_discharge
	incomplete_discharge = 5
	discharge_chart["data"].append({"label": "Completed Treatment", "value": completed_discharge})
	discharge_chart["data"].append({"label": "Discharge With Follow up", "value": follow_up_discharge})

	allocated_rooms = PatientVisit.objects.filter(visit_status='Active').count()
	total_rooms = ServiceRoom.objects.all().count()
	free_rooms = total_rooms - allocated_rooms
	occupancy_chart["data"].append({"label": "Free Rooms", "value": free_rooms})
	occupancy_chart["data"].append({"label": "Allocated Rooms", "value": allocated_rooms})

	drug_name = []
	drug_usage= []
	for drug in Dosage.objects.all():		
		all_medication = OutpatientMedication.objects.filter(drug_prescription__drug=drug).count()
		drug_name.append(str(drug))
		if all_medication:
			drug_usage.append(all_medication)
		else:
			drug_usage.append(0)
	drug_zip =zip(drug_name,drug_usage)

	test_name = []
	test_usage = []
	for section in LaboratorySection.objects.all():
		all_test = OutpatientLabResult.objects.filter(lab_result__result_type__test_type__section=section).count()
		test_name.append(section)
		if all_test:
			test_usage.append(all_test)
		else:
			test_usage.append(0)
	xray_tests = OutpatientRadiologyResult.objects.all().count()
	test_name.append('Xray Test')
	test_name.append(xray_tests)
	lab_zip = zip(test_name,test_usage)
	#for m in all_medication:

	waiting_time_label = ['Until Room Assignment', 'Until Doctor Visit']
	waiting_time = [1.37,2.3]

	payment_status_label = ['Insurance','Free','Credit','Default']
	payment_status = ['Insurance','Free','Credit','Default']
	print(visit.count())

	#address_region = ['Insurance','Free','Credit','Default']
	age = []
	for i in range(1,120):
		age.append(i)
	#for age in age:
	#	print(age,'\n')

	age_array = age

	total_service_bill = ServiceBillDetail.objects.filter(service_price__isnull=False,registered_on__range=[start_date,end_date])
	service_list = []
	service_revenue = []
	for s in Service.objects.all():
		services = total_service_bill.filter(service=s, service_price__isnull=False)
		service_sum = 0
		if services:
			for d in services:
				service_sum = service_sum + d.service_price
		service_list.append(s)
		service_revenue.append(service_sum)
	service_revenue_zip = zip(service_list,service_revenue)


	drug_list3 = []
	drug_revenue = []
	total_drug_bill = BillDetail.objects.filter(selling_price__isnull=False,registered_on__range=[start_date,end_date])
	drug_sum = 0
	for drug in Dosage.objects.all():
		drug_bills = total_drug_bill.filter(drug=drug)
		if drug_bills:
			for bill in drug_bills:
				if bill.discount ==True:
					drug_sum = drug_sum + (bill.quantity * bill.selling_price.discounted_price)
				else:
					drug_sum = drug_sum + (bill.quantity * bill.selling_price.selling_price)

		drug_list3.append(drug)
		drug_revenue.append(drug_sum)
	drug_revenue_zip = zip(drug_list3,drug_revenue)

	test_list = []
	test_revenue = []
	total_lab_bill = LabBillDetail.objects.filter(registered_on__range=[start_date,end_date])
	lab_sum = 0
	for section in LaboratorySection.objects.all():
		lab_bills = total_lab_bill.filter(test__section=section)
		if lab_bills:
			for bill in lab_bills:
				if bill.discount ==True:
					lab_sum = lab_sum + bill.test_price.discounted_price
				else:
					lab_sum = lab_sum + bill.test_price.price

		test_list.append(section)
		test_revenue.append(lab_sum)
	test_revenue_zip = zip(test_list,test_revenue)

	total_revenue = lab_sum + drug_sum + service_sum
	"""
	test_sum = 0
	building_tests = OutpatientLabResult.objects.filter(visit__service_room__building=b)
	if building_tests:
		for d in building_tests:
			price = LaboratoryTestPrice.objects.get(test_type=d.lab_result.result_type.test_type,active=True)
			test_sum = test_sum + price.price

		building_list.append(b)
		building_revenue.append(test_sum + drug_sum)
		building_revenue_chart["data"].append({"label": str(b), "value": test_sum + drug_sum})

	building_revenue_zip = zip(building_list,building_revenue)


	drug_list3 = []
	drug_revenue = []
	for d in Dosage.objects.all():
		sold_drugs = OutpatientMedication.objects.filter(drug_prescription__drug=d)
		drug_sum = 0
		if sold_drugs:
			for sd in sold_drugs:
				price = DrugPrice.objects.get(drug=sd.drug_prescription.drug,active='active')
				drug_sum = drug_sum + price.selling_price
		drug_list3.append(d)
		drug_revenue.append(drug_sum)
	drug_revenue_zip = zip(drug_list3,drug_revenue)

	test_list = []
	test_revenue = []
	for t in LaboratoryTestType.objects.all():
		performed_tests = OutpatientLabResult.objects.filter(lab_result__result_type__test_type=t)
		test_sum = 0
		if performed_tests:
			for d in performed_tests:
				price = LaboratoryTestPrice.objects.get(test_type=d.lab_result.result_type.test_type,active=True)
				test_sum = test_sum + price.price
		test_list.append(t)
		test_revenue.append(test_sum)
	test_revenue_zip = zip(test_list,test_revenue)

	service_list = []
	service_revenue = []
	for s in Service.objects.all():
		services = ServiceBillDetail.objects.filter(service=s, service_price__isnull=False)
		service_sum = 0
		if services:
			for d in services:
				service_sum = service_sum + d.service_price
	service_list.append(s)
	service_revenue.append(service_sum)
	service_revenue_zip = zip(service_list,service_revenue)
	"""
	used_service_chart = FusionCharts("column2d", "used_service_chart", "500", "300", "used_service_bar_chart_container", "json", used_service_chart)
	payment_status_chart_doughnut = FusionCharts("column2d", "payment_status_chart_doughnut", "500", "300", "payment_status_doughnut_container", "json", payment_status_chart)
	payment_status_chart_pie = FusionCharts("pie2d", "payment_status_chart_pie", "500", "300", "payment_status_pie_container", "json", payment_status_chart)
	discharge_chart = FusionCharts("doughnut2d", "discharge_chart", "500", "300", "discharge_doughnut_container", "json", discharge_chart)
	occupancy_chart = FusionCharts("pie2d", "occupancy_chart", "400", "300", "occupancy_pie_container", "json", occupancy_chart)
	building_revenue_chart = FusionCharts("column2d", "building_revenue_chart", "500", "300", "building_bar_container", "json", building_revenue_chart)

	context = {'total_visit':visit.count(),
				'medicated':medication.count(),
				'lab_tested':lab_test.count(),
				'rad_tested':rad_test.count(),
				'used_service_chart':used_service_chart.render(),

				'room':room,
				'sex':sex,
				'payment_status':payment_status,
				'average_medication':average_medication,
				'average_xray_test':average_xray_test,
				'average_lab_test':average_lab_test,

				'total_discharge':total_discharge,
				'completed_discharge':completed_discharge,
				'incomplete_discharge':incomplete_discharge,
				'follow_up_discharge':follow_up_discharge,
				'discharge_chart':discharge_chart.render(),

				'ipa':ps.insurancePatientAmount,
				'dpa':ps.discountPatientAmount,
				'fpa':ps.freePatientAmount,
				'dfpa':ps.defaultPatientAmount,
				'payment_status_chart_pie':payment_status_chart_pie.render(),
				'payment_status_chart_doughnut':payment_status_chart_doughnut.render(),

				'allocated_rooms':allocated_rooms,
				'total_rooms':total_rooms,
				'free_rooms':free_rooms,
				'occupancy_chart':occupancy_chart.render(),

				'drug_zip':drug_zip,
				'lab_zip':lab_zip,

				'age_array':age_array,

				#'building_revenue_zip':building_revenue_zip,
				#'building_revenue_chart':building_revenue_chart.render(),

				'total_revenue':total_revenue,
				'drug_revenue_zip':drug_revenue_zip,
				'test_revenue_zip':test_revenue_zip,
				'service_revenue_zip':service_revenue_zip,

	}
	return render(request, 'outpatient_app/opd_report.html', context)


def LabBillReport(request):
	filtered_drug = request.GET.get('drug') or 'None2'
	filtered_dispensary = request.GET.get('dispensary') or 'None2'

	bill_list = LabBillDetail.objects.all()
	"""
	if filtered_drug == 'None2' or filtered_drug == 0:
		supplied_list = DrugSupplyToDispensary.objects.all()
	else:
		drug = Dosage.objects.get(id=filtered_drug)
		supplied_list = supplied_list.filter(drug=drug)
	if filtered_dispensary == 'None2' or filtered_dispensary == 0:
		print('Do Nothing')
	else:
		dispensary = Dispensary.objects.get(id=filtered_dispensary)
		supplied_list = supplied_list.filter(dispensary=dispensary)	
	"""
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

	return render(request, 'outpatient_app/lab_bill_report.html',context)

def VisitingCardBillReport(request):
	start_date = datetime.strptime(request.GET.get('start_date') or '1970-01-01', '%Y-%m-%d')
	end_date = datetime.strptime(request.GET.get('end_date') or str(datetime.now().date()),  '%Y-%m-%d')

	filtered_drug = request.GET.get('drug') or 'None2'
	filtered_dispensary = request.GET.get('dispensary') or 'None2'

	bill_list = VisitBillDetail.objects.filter(registered_on__range=[start_date,end_date])
	"""
	if filtered_drug == 'None2' or filtered_drug == 0:
		supplied_list = DrugSupplyToDispensary.objects.all()
	else:
		drug = Dosage.objects.get(id=filtered_drug)
		supplied_list = supplied_list.filter(drug=drug)
	if filtered_dispensary == 'None2' or filtered_dispensary == 0:
		print('Do Nothing')
	else:
		dispensary = Dispensary.objects.get(id=filtered_dispensary)
		supplied_list = supplied_list.filter(dispensary=dispensary)	
	"""
	service_list = Service.objects.all()
	dispensary_list = Dispensary.objects.all()
	age = []
	for i in range(1,120):
		age.append(i)
	sex = ['MALE','FEMALE']
	department = ['Inpatient','Outpatient']

	payment_statuses = ['Insurance','Free','Credit','Default']
	dosage_forms = ['Tablet','Capsule','Oral_solution','Injection','Injection with Dilutent']

	context = {'bill_list':bill_list,
				'dispensary_list':dispensary_list,
				'age_array':age,
				'payment_statuses':payment_statuses,
				'department':department,
				'service_list':service_list,
	}

	return render(request, 'outpatient_app/visiting_card_bill_report.html',context)

def ServiceBillReport(request):
	start_date = datetime.strptime(request.GET.get('start_date') or '1970-01-01', '%Y-%m-%d')
	end_date = datetime.strptime(request.GET.get('end_date') or str(datetime.now().date()),  '%Y-%m-%d')


	
	filtered_service = request.GET.get('service') or 'None2'
	filtered_dispensary = request.GET.get('dispensary') or 'None2'

	bill_list = ServiceBillDetail.objects.filter(registered_on__range=[start_date,end_date])
	
	if filtered_service == 'None2' or filtered_service == '0':
		print('Do Nothing')
	else:
		service = Service.objects.get(id=filtered_service)
		bill_list = bill_list.filter(service=service)
	"""
	if filtered_dispensary == 'None2' or filtered_dispensary == 0:
		print('Do Nothing')
	else:
		dispensary = Dispensary.objects.get(id=filtered_dispensary)
		supplied_list = supplied_list.filter(dispensary=dispensary)	
	"""
	service_list = Service.objects.all()
	dispensary_list = Dispensary.objects.all()
	age = []
	for i in range(1,120):
		age.append(i)
	sex = ['MALE','FEMALE']
	department = ['Inpatient','Outpatient']

	payment_statuses = ['Insurance','Free','Credit','Default']
	dosage_forms = ['Tablet','Capsule','Oral_solution','Injection','Injection with Dilutent']

	context = {'bill_list':bill_list,
				'dispensary_list':dispensary_list,
				'age_array':age,
				'payment_statuses':payment_statuses,
				'department':department,
				'service_list':service_list,
	}

	return render(request, 'outpatient_app/service_bill_report.html',context)

def RadiologyBillReport(request):
	filtered_drug = request.GET.get('drug') or 'None2'
	filtered_dispensary = request.GET.get('dispensary') or 'None2'

	bill_list = SerivceBillDetail.objects.all()
	"""
	if filtered_drug == 'None2' or filtered_drug == 0:
		supplied_list = DrugSupplyToDispensary.objects.all()
	else:
		drug = Dosage.objects.get(id=filtered_drug)
		supplied_list = supplied_list.filter(drug=drug)
	if filtered_dispensary == 'None2' or filtered_dispensary == 0:
		print('Do Nothing')
	else:
		dispensary = Dispensary.objects.get(id=filtered_dispensary)
		supplied_list = supplied_list.filter(dispensary=dispensary)	
	"""
	service_list = Service.objects.all()
	dispensary_list = Dispensary.objects.all()
	age = []
	for i in range(1,120):
		age.append(i)
	sex = ['MALE','FEMALE']
	department = ['Inpatient','Outpatient']

	payment_statuses = ['Insurance','Free','Credit','Default']
	dosage_forms = ['Tablet','Capsule','Oral_solution','Injection','Injection with Dilutent']

	context = {'bill_list':bill_list,
				'dispensary_list':dispensary_list,
				'age_array':age,
				'payment_statuses':payment_statuses,
				'department':department,
				'service_list':service_list,
	}

	return render(request, 'outpatient_app/service_bill_report.html',context)

def VisitReportChart(request):
	return render(request, 'pharmacy_app/visit_report_chart.html')


class VisitReportChartData(APIView):
	authentication_classes = []
	permission_classes = []

	def get(self, request, format=None, *args, **kwargs):

		drug_use_labels = ['Took Drug','Took No Drug']
		drug_use_array = []
		lab_use_array = []
		rad_use_array = []
		visit = PatientVisit.objects.filter(patient__isnull=False)
		medication = OutpatientMedication.objects.filter(visit__isnull=False).values('visit__id').distinct().count()
		lab_test = OutpatientLabResult.objects.filter(visit__isnull=False).values('visit__id').distinct().count()
		rad_test = OutpatientRadiologyResult.objects.filter(visit__isnull=False).values('visit__id').distinct().count()
		
		#medicated = visit.count() - medication
		drug_use_array.append(visit.count() - medication)
		drug_use_array.append(medication)

		lab_use_array.append(visit.count() - lab_test)
		lab_use_array.append(lab_test)
		
		rad_use_array.append(visit.count() - rad_test)		
		rad_use_array.append(rad_test)		


		waiting_time_label = ['Until Room Assignment', 'Until Doctor Visit','Average Hospital Stay']
		waiting_time = [1.37,4.4,25.5]

		payment_status_label = ['Insurance','Free','Credit','Default']
		payment_status = [3,2,4,8]


		unadmitted = visit.count()-7
		admission_label = ['Admitted To Ward', 'Discharged']
		admission = [7,unadmitted]
		labels = ['one','two','three']
		number = [10]
		
		age = []

		data = {'labels':drug_use_labels,
				'numbers':drug_use_array,
				'lab_numbers':lab_use_array,
				'rad_numbers':rad_use_array,
				'wait_labels':waiting_time_label,
				'wait_numbers':waiting_time,
				'payment_labels':payment_status_label,
				'payment_numbers':payment_status,
				'admission_label':admission_label,
				'admission':admission,
				'age':age,
				}
		return Response(data)

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
