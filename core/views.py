from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_list_or_404, get_object_or_404
from core.models import * 
from core.forms import *
from outpatient_app.models import TeamSetting,PatientVisit
from inpatient_app.models import Bed, BedCategory
from pharmacy_app.models import DrugPrescription
from inpatient_app.forms import ManualTreatmentForm, DynamicTreatmentForm,PerformPlanForm,IPDTreatmentPlanForm,TolerableDifferenceForm

from lis.models import LaboratoryTestType,LaboratorySection,Order,LaboratoryTestResult
from lis.forms import SpecimenForm,ResultEntryForm
from outpatient_app.forms import PatientRegistrationForm2,PatientEmailForm,AppointmentForm

from billing_app.models import PatientStayDuration,Item,BillableItem
from billing_app.models import *
from inpatient_app.models import InpatientDischargeSummary,IPDTreatmentPlan
from pharmacy_app.forms import PrescriptionForm,PrescriptionInfoForm
from dateutil.rrule import *
from collections import OrderedDict
from inpatient_app.fusioncharts import FusionCharts
from django.shortcuts import redirect, render, get_object_or_404
from itertools import chain
class IndexView(View):

	def get(self, *args, **kwargs):
		if self.request.user.is_anonymous:
			return redirect('core:login')
		return render(self.request, 'core/index.html')


class LoginView(View):
	
	def get(self, *args, **kwargs):
		return render(self.request, 'core/login.html')

	def post(self, *args, **kwargs):
		email = self.request.POST.get('email')
		password = self.request.POST.get('password')
		user = authenticate(email=email, password=password)
		try:
			setting = TeamSetting.objects.get(active=True)
		except :
			setting = None
		if user:
			login(self.request, user)
			messages.success(self.request, f'Welcome, {user.full_name}')
			print(user.employee.designation,'\n')
			if user.employee.designation.name == 'Doctor':
				return redirect('patient_list_for_doctor')
			elif user.employee.designation.name == 'Nurse':
				return redirect('patient_list_for_nurse')
			elif user.employee.designation.name == 'Cashier':
				return redirect('visiting_card_list')
			elif user.employee.designation.name == 'Inpatient Triage':
				return redirect('patient_list')
			elif user.employee.designation.name == 'Outpatient Triage':
				return redirect('outpatient_triage_form')

			elif user.employee.designation.name == 'Nurse Head':
				if setting.setting == 'Team':
					return redirect('nurse_team_list')
				else:
					return redirect('nurse_list')
			elif user.employee.designation.name == 'Doctor Head':
				return redirect('ward_team_list')
			elif user.employee.designation.name == 'Card Room':
				return redirect('patient_registration')
			elif user.employee.designation.name == 'Radiology':
				return redirect('radiology:order_list')
			elif user.employee.designation.name == 'Pharmacy':
				return redirect('inpatient_prescription_list')
			elif user.employee.designation.name == 'Laboratory':
				return redirect('view-orders')
			elif user.employee.designation.name == 'Admin':
				return redirect('admin_dashboard')
			elif user.employee.designation.name == 'Pharmacy Head':
				return redirect('pharmacy_dashboard')
			elif user.employee.designation.name == 'Laboratory Head':
				return redirect('pharmacy_dashboard')
			elif user.employee.designation.name == 'Medical Director':
				return redirect('drug_request_second_approval')
			elif user.employee.designation.name == 'Stock Management':
				return redirect('request_list_from_stock')
			elif user.employee.designation.name == 'Finance Personnel':
				return redirect('cashier_list')
			elif user.employee.designation.name == 'xxxx':
				return redirect('whole_ward_view')

				

				#return redirect('core:index')
		messages.error(self.request, 'Wrong email or password')
		return render(self.request, 'core/login.html', {
			'login_error': True,
		})


class LogoutView(View):

	def get(self, *args, **kwargs):
		logout(self.request)
		return redirect('core:login')


class PatientHistory(View):

	def get(self, *args, **kwargs):
		return render(self.request, 'core/pinfo.html', {
			'patient' : get_object_or_404(Patient, id=kwargs['id'])
		})

class PatientHistory2(View):

	def get(self, *args, **kwargs):
		patient = get_object_or_404(Patient, id=kwargs['id'])
		stay_duration = PatientStayDuration.objects.filter(patient=patient).exclude(leave_date__isnull=True)
		summary_array = []
		for duration in stay_duration:
			summary = InpatientDischargeSummary.objects.filter(stay_duration=duration).last()
			summary_array.append(summary)

		stay_duration_zip = zip(stay_duration, summary_array)    
		return render(self.request, 'core/patient_history.html', {
			'stay_duration_zip':stay_duration_zip,            
		})
class PatientVisitDetail(View):

	def get(self, *args, **kwargs):
		patient = get_object_or_404(Patient, id=kwargs['id'])
		"""
		lvs = PatientVitalSign.objects.filter(patient=patient).last()
		fam_history = FamilyHistory.objects.filter(patient=patient)
		#appointments = PatientAppointment.objects.all()
		lab_tests = None
		latest_order:Order = Order.objects.filter(patient=patient).last()
		if latest_order:
			lab_tests = latest_order.test_set.all()
		"""
		return render(self.request, 'core/patient_visit_detail.html', {
			'patient': patient,
			#'vital_sign': lvs,
			#'fam_history': fam_history,
			#'appts': appointments,
			#'tests': lab_tests,
		})

def PatientChartHistory(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	registration_form = PatientRegistrationForm2(patientid=patient.id)
	medical_form = PatientMedicalHistoryForm(patientid=patient.id)
	social_form = PatientSocialHistoryForm(patientid=patient.id)
	surgery_form = PatientSurgeryHistoryForm(patientid=patient.id)
	family_form = PatientFamilyHistoryForm(patientid=patient_id)


	context = {'patient':patient,
				'medical_form':medical_form,
				'social_form':social_form,
				'family_form':family_form,
				'surgery_form':surgery_form,
	}
	return render(request,'core/patient_chart_history.html', context)

def PatientTimeline(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	clinical_finding = PatientClinicalFinding.objects.filter(patient=patient)
	consultation = PatientConsultation.objects.filter(patient=patient)
	consultation_array = []
	for c in consultation:
		con = c.__dict__
		for field,value in con.items():
			print('fie',field)
		consultation_array.append(con)
	demo_values = PatientDemoValues.objects.all()
	wall = list(chain(consultation, clinical_finding,demo_values))
	wall.sort(key=lambda x: x.registered_on)
	for w in wall :
		print(w,w.registered_on)

	context = {'patient':patient,
				'objects':wall,
				'consultation_objects':consultation,
				'demo_objects':demo_values,
	}
	return render(request,'core/patient_timeline.html', context)

def PatientActivities(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	prescription_form = PrescriptionForm()
	info_form = PrescriptionInfoForm()

	clinical_finding = PatientClinicalFinding.objects.filter(patient=patient)
	consultation = PatientConsultation.objects.filter(patient=patient)
	demo_values = PatientDemoValues.objects.all()
	wall = list(chain(consultation, clinical_finding,demo_values))
	wall.sort(key=lambda x: x.registered_on)
	date_array = []
	for w in wall:
		if w.registered_on.date in date_array: 
			print('al')
		else:
			print('date',w.registered_on.day)
			date_array.append(w.registered_on.day)
		print(w,w.registered_on)
		try:
			if w.title:
				for s in w.clinical_finding.all():
					print('issssss',s)            
		except:
			print("d")
	for date in date_array:
		print(date,'\n')
	context = {'patient':patient,
				'objects':wall,
				'date_array':date_array,
				'info_form':info_form,
				'prescription_form':prescription_form,

	}
	return render(request,'core/patient_activities.html', context)

def Consultations(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	consultation_list = PatientConsultation.objects.filter(patient=patient)
	date_array = []
	date_array.append(datetime.datetime.now()-datetime.timedelta(days=200))
	context = {'patient':patient,
				'consultation_list':consultation_list,
				'date_array':date_array,

	}
	return render(request,'core/consultations.html', context)


def Checkins(request,patient_id):
	today = datetime.datetime.now()
 
	patient = Patient.objects.get(id=patient_id)
	checkin_form = PatientCheckinForm()
	checkin_list = PatientCheckin.objects.filter(patient=patient)
	context = {'patient':patient,
				'checkin_form':checkin_form,
				'checkin_list':checkin_list,

				'initial_date': str(today),

	}
	return render(request,'core/chekins.html', context)

def Resources(request,patient_id):
	days_after = request.GET.get('days_after_amount',None)
	days_before = request.GET.get('days_before_amount',None)

	patient = Patient.objects.get(id=patient_id)
	resource_form = PatientResourceForm()
	create_resource_form = CreateResourceForm()
	resource_list = Resource.objects.all()
	if days_after == None:
		week_after = datetime.datetime.now() + datetime.timedelta(days=7)
		month_after = datetime.datetime.now() + datetime.timedelta(days=30)
	else:
		week_after = datetime.datetime.now() + datetime.timedelta(days=days_after)
		month_after = datetime.datetime.now() + datetime.timedelta(days=days_after)

	if days_before == None:
		tommorow = datetime.datetime.now() + datetime.timedelta(days=1)
		today = datetime.datetime.now()
	else:
		tommorow = datetime.datetime.now() - datetime.timedelta(days=days_before)
		today = datetime.datetime.now() - datetime.timedelta(days=days_before)

	hour_list = list(rrule(HOURLY, today,until=tommorow))
	day_list = list(rrule(DAILY, today,until=week_after))
	month_day_list = list(rrule(DAILY, today,until=month_after))

	resource = Resource.objects.filter().last()
	"""    
	for day in day_list:
		print(day,'\n')
		print(resource.is_scheduled(day,resource.id)) 
	"""
	context = {'patient':patient,
				'resource_form':resource_form,
				'create_resource_form':create_resource_form,
				'resource_list':resource_list,
				'hour_list':hour_list,
				'day_list':day_list,
				'month_day_list':month_day_list,
				'initial_date': str(today),
				'today':today,
	}
	return render(request,'core/resources.html', context)


def ScheduleResource(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	start_date = datetime.datetime.strptime(request.POST.get('start_date') or '2022-10-01', '%Y-%m-%d')
	end_date = datetime.datetime.strptime(request.POST.get('end_date') or str(datetime.datetime.now().date()),  '%Y-%m-%d')
	end_time = datetime.datetime.strptime(request.POST.get('end_time') or '13:30', '%H:%M')
	start_time = datetime.datetime.strptime(request.POST.get('start_time')  or '14:30', '%H:%M')
	print('first date', start_date,'\n')
	start_date = start_date + datetime.timedelta(hours=start_time.hour)
	start_date = start_date + datetime.timedelta(minutes=start_time.minute)
	end_date = end_date + datetime.timedelta(hours=end_time.hour)
	end_date = end_date + datetime.timedelta(minutes=end_time.minute)

	print('start_time',start_time,'\n','end_time: ',end_time,'start_date',start_date)    
	if request.method == 'POST':
		resource_form = PatientResourceForm(request.POST)
		if resource_form.is_valid():
			resource_model = resource_form.save(commit=False)
			resource_model.registered_on = datetime.datetime.now()
			resource_model.registered_by = Employee.objects.get(user_profile=request.user)
			resource_model.active=True
			resource_model.patient = patient
			resource_model.start_time = start_date
			resource_model.end_time = end_date
			#resource_model.start_time.time = start_time
			#resource_model.end_time.time = end_time

			resource_model.save()
			messages.success(request, 'Successful!')
			return redirect('core:resources',patient.id)
		else:
			messages.error(request,str(resource_form.errors))
			return redirect('core:resources',patient.id)

def CreateResource(request):
	if request.method == 'POST':
		resource_form = CreateResourceForm(request.POST)
		if resource_form.is_valid():
			resource_model = resource_form.save(commit=False)
			resource_model.registered_on = datetime.datetime.now()
			resource_model.registered_by = Employee.objects.get(user_profile=request.user)
			resource_model.active=True
			resource_model.save()
			messages.success(request, 'Successful!')
			return redirect('core:resources',22)
		else:
			messages.error(request,str(resource_form.errors))
			return redirect('core:resources',22)

def EditResourceSchedule(request,schedule_id):
	schedule = PatientResource.objects.get(id=schedule_id)
	start_date = datetime.datetime.strptime(request.POST.get('start_date') or '2022-10-01', '%Y-%m-%d')
	end_date = datetime.datetime.strptime(request.POST.get('end_date') or str(datetime.datetime.now().date()),  '%Y-%m-%d')
	end_time = datetime.datetime.strptime(request.POST.get('end_time') or '13:30', '%H:%M')
	start_time = datetime.datetime.strptime(request.POST.get('start_time')  or '14:30', '%H:%M')
	print('first date', start_date,'\n')
	start_date = start_date + datetime.timedelta(hours=start_time.hour)
	start_date = start_date + datetime.timedelta(minutes=start_time.minute)
	end_date = end_date + datetime.timedelta(hours=end_time.hour)
	end_date = end_date + datetime.timedelta(minutes=end_time.minute)
	if request.method == 'POST':
		edit_resource_form = EditPatientResourceForm(request.POST,resource_id=schedule.id)
		if edit_resource_form.is_valid():
			edit_resource_model = edit_resource_form.save(commit=False)
			edit_resource_model.start_time = start_date
			edit_resource_model.end_time = end_date
			edit_resource_model.save()
			messages.success(request, 'Successful!')
			return redirect('core:resources',edit_resource_model.patient.id)
		else:
			messages.error(request,str(edit_resource_form.errors))
			return redirect('core:resources',schedule.patient.id)

def AddCheckin(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	if request.method == 'POST':
		checkin_form = PatientCheckinForm(request.POST)
		if checkin_form.is_valid():
			checkin_model = checkin_form.save(commit=False)
			checkin_model.registered_on = datetime.datetime.now()
			checkin_model.registered_by = Employee.objects.get(user_profile=request.user)
			checkin_model.active=True
			checkin_model.patient = patient
			checkin_model.save()
			messages.success(request, 'Successful!')
			return redirect('core:checkins',patient.id)
		else:
			messages.error(request,str(checkin_form.errors))
			return redirect('core:checkins',patient.id)



def Home(request):

	day = datetime.datetime.now()
	this_month = datetime.datetime.now().month
	last_month = (datetime.datetime.now() -datetime.timedelta(days=30)).month		
	
	before_date = day - datetime.timedelta(days=7)
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
		if invoice.registered_on.month == last_month:
			month_str = str(invoice.registered_on.year) + " - " + str(invoice.registered_on.month)
			if month_str in month_array:
				print('k')
			else:
				credit = 0
				month_array.append(month_str)
				invoice_list = Invoice.objects.filter(registered_on__month=last_month)
				for invoice in invoice_list:
					print('credit: ', credit,'\n')
					credit += invoice.total_amount
				credit_array.append(credit)
				debit = 0
				payment_list = Payment.objects.filter(registered_on__month=last_month)
				for payment in payment_list:
					debit += payment.amount_paid
				debit_array.append(debit)
				balance_array.append(debit - credit) 

	sold_items = ItemSaleInfo.objects.filter(active=True)
	item_count = sold_items.values('item').distinct().count()
	balance_zip = zip(month_array,debit_array,credit_array,balance_array)

	patient_list = Patient.objects.all()[:5][::-1]
	months_ago = datetime.datetime.now() - datetime.timedelta(days=180)
	until_months = datetime.datetime.now() + datetime.timedelta(days=30)
	month_list = list(rrule(MONTHLY, months_ago,until=until_months))
	months = []
	patient_counts = []
	encounter_counts = []

	for month in month_list:
		months.append(month)
		encounters = PatientConsultation.objects.filter(registered_on__month=month.month,active=True)

		patient_count = encounters.values('patient').distinct().count()
		patient_counts.append(patient_count)
		encounter_counts.append(encounters.count())

	diagnosis_counts = []
	diagnosis_array = []


	encounter_zip = zip(months,patient_counts,encounter_counts)
	task_list = Task.objects.all()
	records_submenu = True
	home_tab = True
	if request.htmx:
		value = request.GET.get('last_x_days')


		today = datetime.datetime.now()
		if value == None:
			print('')
		
		else:
			if value == '6':
				months_ago = datetime.datetime.now() - datetime.timedelta(days=150)
				until_months = datetime.datetime.now() + datetime.timedelta(days=30)
			elif value == '3':
				months_ago = datetime.datetime.now() - datetime.timedelta(days=60)
				until_months = datetime.datetime.now() + datetime.timedelta(days=30)
			elif value == '12':
				months_ago = datetime.datetime.now() - datetime.timedelta(days=330)
				until_months = datetime.datetime.now() + datetime.timedelta(days=30)

			month_list = list(rrule(MONTHLY, months_ago,until=until_months))
			months = []
			patient_counts = []
			encounter_counts = []

			for month in month_list:
				months.append(month)
				encounters = PatientConsultation.objects.filter(registered_on__month=month.month,active=True)

				patient_count = encounters.values('patient').distinct().count()
				patient_counts.append(patient_count)
				encounter_counts.append(encounters.count())

			encounter_zip = zip(months,patient_counts,encounter_counts)

		context2 = {
					'encounter_zip':encounter_zip,

					}
		return render(request,'core/htmx_partials/encounters_table_htmx.html', context2)

	context = {'patient_list':patient_list,
				'records_submenu':records_submenu,
				'home_tab':home_tab,
				'encounter_zip':encounter_zip,
				'total_encounters':PatientConsultation.objects.filter(active=True).count(),
				'balance_zip':balance_zip,
				'debit':debit,
				'credit':credit,
				'balance':debit - credit,
				'sold_items':sold_items,
				'item_count':item_count,
				'task_form':TaskForm(),
				'task_list':task_list,

	}
	return render(request,'core/home.html', context)

def SaveTask(request):
	if request.method == 'POST':
		task_form = TaskForm(request.POST)
		if task_form.is_valid():
			task = task_form.save(commit=False)
			task.registered_on = datetime.datetime.now()
			task.registered_by = Employee.objects.get(user_profile=request.user)
			#task.active=True
			task.save()
			messages.success(request, 'Successful!')
			return redirect('core:home')
		else:
			messages.error(request,str(task_form.errors))
			return redirect('core:home')

def Activities(request,patient_id):
	start_date1 = datetime.datetime.now() - datetime.timedelta(days=500)
	end_date1 = datetime.datetime.now() + datetime.timedelta(days=500)
	filtered_start_date = request.GET.get('start_date',None)
	filtered_end_date = request.GET.get('end_date',None)
	if filtered_start_date == None:
		print('')
	else:
		start_date1 = filtered_start_date
	if filtered_end_date == None:
		print('')
	else:
		end_date1 = filtered_end_date

	patient = Patient.objects.get(id=patient_id)
	clinical_finding = PatientClinicalFinding.objects.filter(patient=patient,registered_on__range=[start_date1,end_date1])
	consultation_list = PatientConsultation.objects.filter(patient=patient,active=True,registered_on__range=[start_date1,end_date1])
	demo_values = PatientDemoValues.objects.all()
	wall = list(chain(consultation_list, clinical_finding,demo_values))
	wall.sort(key=lambda x: x.registered_on)
	image_list = PatientImage.objects.filter(registered_on__range=[start_date1,end_date1])
	file_list = PatientFile.objects.filter(registered_on__range=[start_date1,end_date1])

	treatment_plan_list = IPDTreatmentPlan.objects.filter(patient=patient,registered_on__range=[start_date1,end_date1])

	treatment_list = PatientTreatment.objects.filter(patient=patient,registered_on__range=[start_date1,end_date1],active=True)
	prescription_list = DrugPrescription.objects.filter(patient=patient,registered_on__range=[start_date1,end_date1])

	material_list = PatientMaterial.objects.filter(patient=patient,registered_on__range=[start_date1,end_date1],active=True)
	diagnosis_list = PatientDiagnosis.objects.filter(patient=patient,registered_on__range=[start_date1,end_date1],active=True)

	certificate_list = MedicalCertificate.objects.filter(patient=patient,registered_on__range=[start_date1,end_date1],active=True)
	attendance_list = MedicalAttendance.objects.filter(patient=patient,registered_on__range=[start_date1,end_date1],active=True)

	certificate_form = MedicalCertificateForm()
	diagnosis_form = PatientDiagnosisForm()
	treatment_form = PatientTreatmentForm()
	prescription_form = PrescriptionForm()
	info_form = PrescriptionInfoForm()
	patient_treatment_form = PatientTreatmentForm()
	manual_treatment_form = ManualTreatmentForm()

	edit_treatment_form = EditPatientTreatmentForm(planid=1)
	treatment_tab = False
	dynamic_treatment_form = DynamicTreatmentForm()
	material_form = PatientMaterialForm()
	records_submenu = True
	activities_tab = True
	today3 = datetime.datetime.now() - datetime.timedelta(days=300)
	date_array = []
	date_array.append(today3)
	prescription_date_array = []
	prescription_date_array.append(today3)
	timeline_date_array = []
	timeline_date_array.append(today3)
	image_date_array = []
	image_date_array.append(today3)
	document_date_array = []
	document_date_array.append(today3)
	material_date_array = []
	material_date_array.append(today3)
	diagnosis_date_array = []
	diagnosis_date_array.append(today3)
	certificate_date_array = []
	certificate_date_array.append(today3)
	attendance_date_array = []
	attendance_date_array.append(today3)

	context = {'patient':patient,
				'date_array':date_array,
				'prescription_date_array':prescription_date_array,
				'timeline_date_array':timeline_date_array,
				'image_date_array':image_date_array,
				'document_date_array':document_date_array,
				'material_date_array':material_date_array,
				'diagnosis_date_array':diagnosis_date_array,
				'attendance_date_array':attendance_date_array,
				'certificate_date_array':certificate_date_array,

				'records_submenu':records_submenu,
				'activities_tab':activities_tab,

				'objects':wall,
				'timeline_objects':wall,

				'consultation_list':consultation_list,
				'file_list':file_list,
				'image_list':image_list,
				'treatment_plan_list':treatment_plan_list,
				'prescription_list':prescription_list,
				'treatment_list':treatment_list,
				'treatment_tab':treatment_tab,

				'diagnosis_list':diagnosis_list,
				'diagnosis_form':diagnosis_form,
				'attendance_list':attendance_list,

				'certificate_list':certificate_list,
				'material_list':material_list,

				'certificate_form':certificate_form,
				'treatment_form':treatment_form,
				'prescription_form':prescription_form,
				'info_form2':info_form,
				'info_form':info_form,

				'manual_treatment_form':manual_treatment_form,
				'patient_treatment_form':patient_treatment_form,

				'dynamic_treatment_form':dynamic_treatment_form,
				'edit_treatment_form':edit_treatment_form,

				'material_form':material_form,

	}
	return render(request,'core/activities.html', context)

def AddPatientDocument(request,patient_id,file_type,url_arg):
	
	patient = Patient.objects.get(id=patient_id)
	documents = request.POST.getlist('files')
	for document in documents:
		if file_type == 'Image':
			document_object= PatientImage()
			file_object = Image()
			file_object.image = document
			document_object.image=file_object
		else:	
			document_object= PatientFile()
			file_object = File()
			file_object.file = document
			document_object.file=file_object

		document_object.patient = patient
		document_object.registered_on = datetime.datetime.now()
		document_object.registered_by = Employee.objects.get(user_profile=request.user)
		document_object.active=True

		file_object.save()
		document_object.save()
		if url_arg == 'activities':
			messages.success(request, 'Document Successfuly Added!')
			return redirect('core:activities',patient.id)
		else:
			messages.success(request, 'Document Successfuly Added!')
			return redirect('core:patient_dashboard',patient.id)

def DeletePrescription(request,prescription_id):
	prescription = DrugPrescription.objects.get(id=prescription_id)
	prescription.active=False
	prescription.save()
	messages.success(request, 'Prescription Successfuly Deleted!')
	return redirect('core:activities',prescription.patient.id)

def DeletePatientMaterial(request,material_id):
	material = PatientMaterial.objects.get(id=material_id)
	material.active=False
	material.save()
	messages.success(request, 'Material Successfuly Deleted!')
	return redirect('core:activities',material.patient.id)

def DeletePatientDocument(request,file_id):
	document = PatientFile.objects.get(id=file_id)
	document.active=False 
	document.save()
	messages.success(request, 'Document Successfuly Deleted!')
	return redirect('core:activities',document.patient.id)


def DeletePatientImage(request,image_id):
	image = PatientImage.objects.get(id=image_id)
	image.active=False
	image.save()
	messages.success(request, 'Image Successfuly Deleted!')
	return redirect('core:activities',image.patient.id)

def AddPatientMaterial(request,patient_id):
	patient = Patient.objects.get(id=patient_id)

	if request.method == 'POST':
		material_form = PatientMaterialForm(request.POST)
		if material_form.is_valid():
			material_model = material_form.save(commit=False)
			material_model.registered_on = datetime.datetime.now()
			material_model.registered_by = Employee.objects.get(user_profile=request.user)
			material_model.active=True
			material_model.patient = patient
			material_model.save()
			messages.success(request, 'Successful!')
			return redirect('core:activities',patient.id)
		else:
			messages.error(request,str(material_form.errors))
			return redirect('core:activities',patient.id)

def AddPatientDiagnosis(request,patient_id):
	patient = Patient.objects.get(id=patient_id)

	if request.method == 'POST':
		diagnosis_form = PatientDiagnosisForm(request.POST)
		if diagnosis_form.is_valid():
			diagnosis_model = diagnosis_form.save(commit=False)
			diagnosis_model.registered_on = datetime.datetime.now()
			diagnosis_model.registered_by = Employee.objects.get(user_profile=request.user)
			diagnosis_model.active=True
			diagnosis_model.patient = patient
			diagnosis_model.save()
			messages.success(request, 'Successful!')
			return redirect('core:activities',patient.id)
		else:
			messages.error(request,str(diagnosis_form.errors))
			return redirect('core:activities',patient.id)

def EditPatientDiagnosis(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	if request.method == 'POST':
		diagnosis_form = EditPatientDiagnosisForm(request.POST)
		if diagnosis_form.is_valid():
			diagnosis_model = diagnosis_form.save(commit=False)
			diagnosis_model.save()
			messages.success(request, 'Successful!')
			return redirect('core:activities',patient.id)
		else:
			messages.error(request,str(diagnosis_form.errors))
			return redirect('core:activities',patient.id)

def AddMedicalCertificate(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	start_date = datetime.datetime.strptime(request.POST.get('start_date') or '2022-10-01', '%Y-%m-%d')
	end_date = datetime.datetime.strptime(request.POST.get('end_date') or str(datetime.datetime.now().date()),  '%Y-%m-%d')

	if request.method == 'POST':
		certificate_form = MedicalCertificateForm(request.POST)
		if certificate_form.is_valid():
			certificate_model = certificate_form.save(commit=False)
			certificate_model.registered_on = datetime.datetime.now()
			certificate_model.registered_by = Employee.objects.get(user_profile=request.user)
			certificate_model.active=True
			certificate_model.patient = patient
			certificate_model.start_date = start_date
			certificate_model.end_date = end_date

			certificate_model.save()
			messages.success(request, 'Successful!')
			return redirect('core:activities',patient.id)
		else:
			messages.error(request,str(certificate_form.errors))
			return redirect('core:activities',patient.id)

def EditMedicalCertificate(request,certificate_id):
	certificate = MedicalCertificate.objects.get(id=certificate_id)
	start_date = datetime.datetime.strptime(request.POST.get('start_date') or '2022-10-01', '%Y-%m-%d')
	end_date = datetime.datetime.strptime(request.POST.get('end_date') or str(datetime.datetime.now().date()),  '%Y-%m-%d')

	if request.method == 'POST':
		edit_certificate_form = EditMedicalCertificateForm(request.POST,certificateid=certificate_id)
		if edit_certificate_form.is_valid():
			certificate_model = edit_certificate_form.save(commit=False)
			certificate_model.start_date = start_date
			certificate_model.end_date = end_date
			certificate_model.save()
			messages.success(request, 'Successful!')
			return redirect('core:activities',certificate.patient.id)
		else:
			messages.error(request,str(edit_certificate_form.errors))
			return redirect('core:activities',certificate.patient.id)


def DeleteMedicalCertificate(request,certificate_id):
	certificate = MedicalCertificate.objects.get(id=certificate_id)
	certificate.active = False
	certificate.save()
	messages.success(request, 'Successfuly Deleted!')
	return redirect('core:activities',certificate.patient.id)

def AddMedicalAttendance(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	date = datetime.datetime.strptime(request.POST.get('start_date') or '2022-10-01', '%Y-%m-%d')
	end_time = datetime.datetime.strptime(request.POST.get('end_time') or '13:30', '%H:%M')
	start_time = datetime.datetime.strptime(request.POST.get('start_time')  or '14:30', '%H:%M')
	attendance = MedicalAttendance()
	attendance.date = date
	attendance.start_time = start_time
	attendance.end_time = end_time
	attendance.active = True
	attendance.registered_on = datetime.datetime.now()
	attendance.patient = patient
	attendance.save()
	messages.success(request, 'Successful!')
	return redirect('core:activities',attendance.patient.id)

def EditMedicalAttendance(request,attendance_id):
	attendance = MedicalAttendance.objects.get(id=attendance_id)
	date = datetime.datetime.strptime(request.POST.get('start_date') or '2022-10-01', '%Y-%m-%d')
	end_time = datetime.datetime.strptime(request.POST.get('end_time') or '13:30', '%H:%M')
	start_time = datetime.datetime.strptime(request.POST.get('start_time')  or '14:30', '%H:%M')
	attendance.date = date
	attendance.start_time = start_time
	attendance.end_time = end_time
	attendance_model.save()
	messages.success(request, 'Successful!')
	return redirect('core:activities',attendance.patient.id)

def DeleteMedicalAttendance(request,attendance_id):
	attendance = MedicalAttendance.objects.get(id=attendance_id)
	attendance.active = False
	attendance.save()
	messages.success(request, 'Successfuly Deleted!')
	return redirect('core:activities',attendance.patient.id)

def DeletePatientDiagnosis(request,diagnosis_id):
	diagnosis = PatientDiagnosis.objects.get(id=diagnosis_id)
	diagnosis.active = False
	diagnosis.save()
	messages.success(request, 'Successfuly Deleted!')
	return redirect('core:activities',diagnosis.patient.id)

	"""    
	if request.method == 'POST':
		edit_attendance_form = EditMedicalCertificateForm(request.POST,attendanceid=attendance_id)
		if edit_attendance_form.is_valid():
			attendance_model = edit_attendance_form.save(commit=False)
			attendance_model.start_date = start_date
			attendance_model.end_date = end_date
			attendance_model.save()
			messages.success(request, 'Successful!')
			return redirect('core:activities',attendance.patient.id)
		else:
			messages.error(request,str(edit_attendance_form.errors))
			return redirect('core:activities',attendance.patient.id)
	"""
def PatientDashboard(request, patient_id):
	demo_chart = OrderedDict()

# The `chartConfig` dict contains key-value pairs of data for chart attribute
	chartConfig = OrderedDict()
	chartConfig["caption"] = "Demo Values"
	chartConfig["subCaption"] = ""
	chartConfig["xAxisName"] = "Date"
	chartConfig["yAxisName"] = "Value"
	chartConfig["numberSuffix"] = ""
	chartConfig["theme"] = "fusion"
	chartConfig["numVisiblePlot"] = "8",
	chartConfig["flatScrollBars"] = "1",
	chartConfig["scrollheight"] = "1",
	chartConfig["type"] = "pie2d",

	demo_chart["chart"] = chartConfig
	demo_chart["dataset"] = []
	demo_chart["categories"] = []

	demo_value_list = PatientDemoValues.objects.all()
	latest_value = PatientDemoValues.objects.filter().last()
	for demo in demo_value_list:
		#demo_chart["data"].append({"label": {{value.registered_on}}, "value": {{value.cholestrol}}, 'seriesname':'Cholestrol'})
		#demo_chart["data"].append({"label": {{value.registered_on}}, "value": {{value.HDL}}, 'seriesname':'HDL'})      
		reg = str(demo.registered_on)
		val = int(demo.cholestrol)
		print(demo.cholestrol,'Its co','\n')
		#demo_chart["data"].append({"label": reg, "value": demo.cholestrol,'seriesname':'HDL'})
		#demo_chart["data"].append({"label": 'dd', "value": demo.cholestrol})
	#for i in range(1,5):
	"""
	data = {}
	category = {}
	data2 = {}
	category2 = {}

	data.update({'seriesname':'dd'})
	#data.update({'data':[{'seriesname':'dd'},{'seriesname':"ee"}]})
	data.update({'data':[{'value':1},{'value':2}]})
	category.update({'category':[{'label':"1"},{'label':'2'}]})
	#setattr(demo_chart['dataset'],data)
	demo_chart["dataset"].append(data)
	demo_chart["categories"].append(category)

	#data.update({'seriesname':'cc'})
	#data.update({'data':[{'seriesname':'dd'},{'seriesname':"ee"}]})
	data2.update({'data':[{'value':3},{'value':4}]})
	category2.update({'category':[{'label':"5"},{'label':'6'}]})
	#setattr(demo_chart['dataset'],data)
	demo_chart["dataset"].append(data2)
	demo_chart["categories"].append(category2)
	"""
	#demo_chart["dataset"].append({"data": 'dd', "value": i})
	"""
	for demo in demo_value_list:
		data = {}
		category = {}
		data.update({'seriesname':str(demo.registered_on)})
		#data.update({'data':[{'seriesname':'dd'},{'seriesname':"ee"}]})
		data.update({'data':[{'value':demo.cholestrol},{'value':100}]})
		category.update({'category':[{'label':"1"}]})
		demo_chart["dataset"].append(data)
		demo_chart["categories"].append(category)
	"""   
	data = {}
	category = {}
	data.update({'seriesname':'Cholestrol'})
	#data.update({'data':[{'seriesname':'dd'},{'seriesname':"ee"}]})
	data.update({'data':[{'value':150},{'value':130},{'value':100}]})
	category.update({'category':[{'label':"2022-11-03"},{'label':"2022-11-03"},{'label':"2022-11-04"}]})
	demo_chart["dataset"].append(data)
	demo_chart["categories"].append(category)
	data = {}
	category = {}
	data.update({'seriesname':'HDL'})
	#data.update({'data':[{'seriesname':'dd'},{'seriesname':"ee"}]})
	data.update({'data':[{'value':50},{'value':80},{'value':80}]})
	category.update({'category':[{'label':"2022-11-03"},{'label':"2022-11-03"},{'label':"2022-11-04"}]})
	demo_chart["dataset"].append(data)
	demo_chart["categories"].append(category)

	#3

	data = {}
	category = {}
	data.update({'seriesname':'LDL'})
	#data.update({'data':[{'seriesname':'dd'},{'seriesname':"ee"}]})
	data.update({'data':[{'value':40},{'value':90},{'value':10}]})
	category.update({'category':[{'label':"2022-11-03"},{'label':"2022-11-03"},{'label':"2022-11-04"}]})
	demo_chart["dataset"].append(data)
	demo_chart["categories"].append(category)

	#4
	data = {}
	category = {}
	data.update({'seriesname':'TGO'})
	#data.update({'data':[{'seriesname':'dd'},{'seriesname':"ee"}]})
	data.update({'data':[{'value':30},{'value':40},{'value':80}]})
	category.update({'category':[{'label':"2022-11-03"},{'label':"2022-11-03"},{'label':"2022-11-04"}]})
	demo_chart["dataset"].append(data)
	demo_chart["categories"].append(category)

	#5
	data = {}
	category = {}
	data.update({'seriesname':'TGP'})
	#data.update({'data':[{'seriesname':'dd'},{'seriesname':"ee"}]})
	data.update({'data':[{'value':80},{'value':30},{'value':70}]})
	category.update({'category':[{'label':"2022-11-03"},{'label':"2022-11-03"},{'label':"2022-11-04"}]})
	demo_chart["dataset"].append(data)
	demo_chart["categories"].append(category)

	#chartObj = FusionCharts( 'msline', 'ex1', '600', '400', 'chart-1', 'json', """{
	demo_pie_chart = FusionCharts("msline", "demo_chart88", "450", "350", "demo_line_container", "json", demo_chart)

	patient = Patient.objects.get(id=patient_id)        
	last_visit = PatientVisit.objects.filter(patient=patient).last()
	last_ward_visit = PatientStayDuration.objects.filter(patient=patient).last()
	allergy_form = PatientAllergyForm()
	allergy_list = PatientAllergy.objects.all()
	finding_form = PatientClinicalFindingForm()
	para_form = PatientParaClinicalFindingForm()
	demo_form = DemoValuesForm()
	edit_demo_form = EditDemoValuesForm(patientid=patient.id)

	treatment_form = PatientTreatmentForm()
	image_form = ImageForm()
	prescription_form = PrescriptionForm()
	info_form = PrescriptionInfoForm()
	start_date1 = datetime.datetime.now() - datetime.timedelta(days=500)
	end_date1 = datetime.datetime.now() + datetime.timedelta(days=500)
	filtered_start_date = request.GET.get('start_date',None)
	filtered_end_date = request.GET.get('end_date',None)
	if filtered_start_date == None:
		print('')
	else:
		start_date1 = filtered_start_date
	if filtered_end_date == None:
		print('')
	else:
		end_date1 = filtered_end_date

	surgery_form = PatientSurgeryForm()
	search_consultation = request.GET.get('search-consultation',None)
	consultation_list = PatientConsultation.objects.filter(registered_on__range=[start_date1,end_date1],active=True,patient=patient)
	clinical_finding_list = PatientClinicalFinding.objects.filter(registered_on__range=[start_date1,end_date1],patient=patient)
	para_clinical_finding_list = PatientParaclinicalFinding.objects.filter(registered_on__range=[start_date1,end_date1],patient=patient)
	demo_value_list = PatientDemoValues.objects.filter(registered_on__range=[start_date1,end_date1],patient=patient)
	treatment_plan_list = IPDTreatmentPlan.objects.filter(patient=patient,registered_on__range=[start_date1,end_date1])

	search_prescription = request.GET.get('search-prescription',None)
	search_timeline = request.GET.get('search-timeline',None)
	search_activities = request.GET.get('search-activities',None)

	surgery_list = PatientSurgery.objects.filter(registered_on__range=[start_date1,end_date1],patient=patient)
	image_list = PatientImage.objects.filter(registered_on__range=[start_date1,end_date1],active=True,patient=patient)
	file_list = PatientFile.objects.filter(registered_on__range=[start_date1,end_date1],active=True,patient=patient)
	treatment_list = PatientTreatment.objects.filter(registered_on__range=[start_date1,end_date1],active=True,patient=patient)

	print('\n','\n','ssesees: ',search_consultation,'\n')
	if search_consultation == None:
		print('')
	else:
		consultation_list = consultation_list.filter(registered_on__range=[start_date1,end_date1],title__icontains=search_consultation)

	if search_timeline == None:
		print('')
	else:
		consultation_list = consultation_list.filter(registered_on__range=[start_date1,end_date1],title__icontains=search_timeline)
		clinical_finding_list = clinical_finding_list.filter(clinical_finding__icontains=search_timeline)
		treatment_list = treatment_list.filter(treatment__icontains=search_timeline)

	if search_activities == None:
		print('')
	else:
		consultation_list = consultation_list.filter(registered_on__range=[start_date1,end_date1],title__icontains=search_activities)
		clinical_finding_list = clinical_finding_list.filter(clinical_finding__icontains=search_activities)
		treatment_list = treatment_list.filter(treatment__icontains=search_activities)


	for treatment in treatment_list:
		for area in treatment.image.all():
			print(area)
	for p in consultation_list:
		print (p)
	prescription_list = DrugPrescription.objects.filter(patient=patient,registered_on__range=[start_date1,end_date1])
	timeline_objects = list(chain(consultation_list, clinical_finding_list,demo_value_list,surgery_list,allergy_list,treatment_list))
	timeline_objects.sort(key=lambda x: x.registered_on)
	timeline_objects = timeline_objects[::-1]
	if search_prescription == None:
		print('')
	else:
		prescription_list = prescription_list.filter(registered_on__range=[start_date1,end_date1],info__drug__drug__drug__commercial_name__icontains=search_prescription)

	schedule_stuff_form = ScheduleStuffForm()
	registration_form = PatientRegistrationForm2(patientid=patient.id)
	medical_form = PatientMedicalHistoryForm(patientid=patient.id)
	social_form = PatientSocialHistoryForm(patientid=patient.id)
	surgery_form = PatientSurgeryHistoryForm(patientid=patient.id)
	family_form = PatientFamilyHistoryForm(patientid=patient_id)

	dynamic_treatment_form = DynamicTreatmentForm()
	manual_treatment_form = ManualTreatmentForm()
	appointment_form = AppointmentForm()
	patient_treatment_form = PatientTreatmentForm()
	recurrence_form = RecurrenceForm()
	sign_form = VitalSignForm()
	perform_plan_form = PerformPlanForm()
	treatment_plan_form = IPDTreatmentPlanForm()
	tolerable_form = TolerableDifferenceForm()

	info_form2 = PrescriptionInfoForm()
	patient_treatment_form = PatientTreatmentForm()


	patient_dashboard = True
	records_submenu = True
	today3 = datetime.datetime.now() - datetime.timedelta(days=300)
	date_array = []
	date_array.append(today3)
	prescription_date_array = []
	prescription_date_array.append(today3)
	timeline_date_array = []
	timeline_date_array.append(today3)
	image_date_array = []
	image_date_array.append(today3)
	document_date_array = []
	document_date_array.append(today3)

	context = {#'patient_list':patient_list,

				'date_array':date_array,
				'prescription_date_array':prescription_date_array,
				'timeline_date_array':timeline_date_array,
				'document_date_array':document_date_array,
				'image_date_array':image_date_array,

				'records_submenu':records_submenu,
				'patient_dashboard':patient_dashboard,
				'patient':patient,
				'last_visit':last_visit,
				'last_ward_visit':last_ward_visit,
				'allergy_form':allergy_form,
				'allergy_list':allergy_list,
				'finding_form':finding_form,
				'image_form':image_form,
				'prescription_form':prescription_form,
				'info_form':info_form,
				'info_form2':info_form,
				'tolerable_form':tolerable_form,
				
				'sign_form':sign_form,
				'dynamic_treatment_form':dynamic_treatment_form,
				'manual_treatment_form':manual_treatment_form,
				'appointment_form':appointment_form,
				'patient_treatment_form':patient_treatment_form,
				'recurrence_form':recurrence_form,
				'perform_plan_form':perform_plan_form,
				'treatment_plan_form':treatment_plan_form,
				'patient_treatment_form':patient_treatment_form,

				'surgery_form':surgery_form,
				'demo_chart':demo_pie_chart.render(),
				#'image_formset':image_formset,
 
				'clinical_finding_list':clinical_finding_list,
				'para_list':para_clinical_finding_list,
				'surgery_list':surgery_list,
				'file_list':file_list,
				'image_list':image_list,

				'para_form':para_form,
				'demo_form':demo_form,
				'edit_demo_form':edit_demo_form,
				'schedule_stuff_form':schedule_stuff_form,

				'treatment_form':treatment_form,
				'treatment_list':treatment_list,
				'demo_value_list':demo_value_list,
				'latest_value':latest_value,
				'consultation_list':consultation_list,
				'prescription_list':prescription_list,
				'treatment_plan_list':treatment_plan_list,
				'timeline_objects':timeline_objects,
				'medical_form':medical_form,
				'social_form':social_form,
				'family_form':family_form,
				'surgery_form':surgery_form,

	}
	return render(request,'core/patient_dashboard.html', context)


def AddDemoValue(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	if request.method == 'POST':
		demo_form = DemoValuesForm(request.POST)
		if demo_form.is_valid():
			demo_model = demo_form.save(commit=False)
			demo_model.registered_on = datetime.datetime.now()
			demo_model.registered_by = Employee.objects.get(user_profile=request.user)
			demo_model.active=True
			demo_model.patient = patient
			try:
				demo = PatientDemoValues.objects.get(patient=patient,active=True)
				demo.active=False
				demo.save()
			except:
				print('not worked')
			demo_model.save()
			messages.success(request, 'Successful!')
			return redirect('core:patient_dashboard',patient.id)
		else:
			messages.error(request,str(demo_form.errors))
			return redirect('core:patient_dashboard',patient.id)

def AddAllergy(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	if request.method == 'POST':
		allergy_form = PatientAllergyForm(request.POST)
		if allergy_form.is_valid():
			allergy_model = allergy_form.save(commit=False)
			allergy_model.registered_on = datetime.datetime.now()
			allergy_model.registered_by = Employee.objects.get(user_profile=request.user)
			allergy_model.active=True
			allergy_model.patient = patient
			allergy_model.save()
			messages.success(request, 'Successful!')
			return redirect('core:patient_dashboard',patient.id)
		else:
			messages.error(request,str(allergy_form.errors))
			return redirect('core:patient_dashboard',patient.id)


def EditAllergy(request,allergy_id):
	allergy_model = PatientAllergy.objects.get(id=allergy_id)
	allergy = str(request.POST.get('allergy')) or 'None'
	if allergy == 'None':
		messages.error(request,"Add Allergy!")
		return redirect('core:patient_dashboard',patient.id)
	allergy_model.allergy = allergy
	allergy_model.save()
	messages.success(request, 'Successful!')
	return redirect('core:patient_dashboard',allergy_model.patient.id)

def DeleteAllergy(request,allergy_id):
	allergy_model = PatientAllergy.objects.get(id=allergy_id)
	allergy_model.active=False
	allergy_model.save()

	messages.success(request, 'Successful!')
	return redirect('core:patient_dashboard',allergy_model.patient.id)

def AddClinicalFinding(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	if request.method == 'POST':
		finding_form = PatientClinicalFindingForm(request.POST)
		if finding_form.is_valid():
			finding_model = finding_form.save(commit=False)
			finding_model.registered_on = datetime.datetime.now()
			finding_model.registered_by = Employee.objects.get(user_profile=request.user)
			finding_model.active=True
			finding_model.patient = patient
			finding_model.save()
			messages.success(request, 'Successful!')
			return redirect('core:patient_dashboard',patient.id)
		else:
			messages.error(request,str(finding_form.errors))
			return redirect('core:patient_dashboard',patient.id)

def EditClinicalFinding(request,finding_id):
	finding_model = PatientClinicalFinding.objects.get(id=finding_id)
	finding = str(request.POST.get('finding')) or 'None'
	print('finding: ',finding)
	if finding == 'None':
		messages.error(request,"Add Findings!")
		return redirect('core:patient_dashboard',finding_model.patient.id)
	finding_model.clinical_finding = finding
	finding_model.save()
	messages.success(request, 'Successful!')
	return redirect('core:patient_dashboard',finding_model.patient.id)

def DeleteClinicalFinding(request,finding_id):
	finding_model = PatientClinicalFinding.objects.get(id=finding_id)
	finding_model.active = False
	finding_model.save()

	messages.success(request, 'Successful!')
	return redirect('core:patient_dashboard',finding_model.patient.id)

def AddTreatment(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	if request.method == 'POST':
		treatment_form = PatientTreatmentForm(request.POST)
		if treatment_form.is_valid():
			images = request.POST.getlist('images')
			print('images:',images)
			treatment_model = treatment_form.save(commit=False)
			treatment_model.registered_on = datetime.datetime.now()
			treatment_model.registered_by = Employee.objects.get(user_profile=request.user)
			treatment_model.active=True
			treatment_model.patient = patient
			for image in images:
				print(image)
				image_object= Image()
				image_object.image = image
				if image_object.image:
					image_object.save()
					treatment_model.save()
					treatment_model.image.add(image_object)
			treatment_model.save()
			messages.success(request, 'Successful!')
			return redirect('core:patient_dashboard',patient.id)
		else:
			messages.error(request,str(treatment_form.errors))
			return redirect('core:patient_dashboard',patient.id)

def EditTreatment(request,treatment_id):
	if request.method == 'POST':
		images = request.POST.getlist('images')


		treatment_model = PatientTreatment.objects.get(id=treatment_id)
		treatment = str(request.POST.get('treatment')) or 'None'
		if treatment == 'None':
			messages.error(request,"Add Findings!")
			return redirect('core:patient_dashboard',treatment_model.patient.id)
		treatment_model.treatment = treatment
		for image in images:
			print(image)
			image_object= Image()
			image_object.image = image
			if image_object.image:
				image_object.save()
				treatment_model.save()
				treatment_model.image.add(image_object)

		treatment_model.save()
		messages.success(request, 'Successful!')
		return redirect('core:patient_dashboard',treatment_model.patient.id)

def RemoveTreatmentImage(request,image_id,patient_id):
	patient = Patient.objects.get(id=patient_id)
	image_model = Image.objects.get(id=image_id)
	image_model.delete()

	messages.success(request, 'Successful!')
	return redirect('core:patient_dashboard',patient.id)


def DeleteTreatment(request,treatment_id):
	treatment_model = PatientTreatment.objects.get(id=treatment_id)
	treatment_model.active = False
	treatment_model.save()
	messages.success(request, 'Successful!')
	return redirect('core:patient_dashboard',treatment_model.patient.id)

def AddPrescription(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	if request.POST:
		prescription_form = PrescriptionForm(request.POST)
		if prescription_form.is_valid():
			prescription_model = prescription_form.save(commit=False)

			if prescription_model.info:
				try:
					item = Item.objects.get(drug=prescription_model.info.drug)
					billable_item =BillableItem()
					billable_item.item = item
					billable_item.patient = patient
					billable_item.active = True
					billable_item.registered_on = datetime.datetime.now()
					billable_item.save()
				except:
					print('')
				prescription_model.patient = patient
				prescription_model.department = 'Ward'
				prescription_model.registered_on = datetime.datetime.now()
				prescription_model.active = True
				prescription_model.save()
				messages.success(request,'Successful')
				return redirect('core:patient_dashboard',patient_id)
		else:
			messages.error(request,str(prescription_form.errors))
			return redirect('core:patient_dashboard',patient_id)

		prescription_form = PrescriptionForm(request.POST)
		info_form2 = PrescriptionInfoForm(request.POST)

		if prescription_form.is_valid():

			info_model = info_form2.save(commit=False)
			prescription_model = prescription_form.save(commit=False)
			prescription_model.patient = patient

			prescription_model.department = 'Ward'
			prescription_model.registered_on = datetime.datetime.now()
			prescription_model.info = info_model
			prescription_model.active = True
			try:
				item = Item.objects.get(drug=prescription_model.info.drug)
				billable_item =BillableItem()
				billable_item.item = item
				billable_item.patient = patient
				billable_item.active = True
				billable_item.registered_on = datetime.datetime.now()
				billable_item.save()
			except:
				print('')

			info_model.save()
			prescription_model.save()
			messages.success(request,'Successful')
			return redirect('core:patient_dashboard',patient_id)
		else:
			messages.error(request,str(prescription_form.errors))
			return redirect('core:patient_dashboard',patient_id)
 

def AddParaclinicalFinding(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	if request.method == 'POST':
		para_form = PatientParaClinicalFindingForm(request.POST)
		if para_form.is_valid():
			images = request.POST.getlist('images')
			print('images:',images)
			para_model = para_form.save(commit=False)
			para_model.registered_on = datetime.datetime.now()
			para_model.registered_by = Employee.objects.get(user_profile=request.user)
			para_model.active=True
			para_model.patient = patient
			for image in images:
				print(image)
				image_object= File()
				image_object.file = image
				image_object.save()
				para_model.save()
				para_model.file.add(image_object)
			para_model.save()
			messages.success(request, 'Successful!')
			return redirect('core:patient_dashboard',patient.id)
		else:
			messages.error(request,str(para_form.errors))
			return redirect('core:patient_dashboard',patient.id)


def EditParaclinicalFinding(request,finding_id):
	finding_model = PatientParaclinicalFinding.objects.get(id=finding_id)
	finding = str(request.POST.get('finding')) or 'None'
	print('finding: ',finding)
	if finding == 'None':
		messages.error(request,"Add Findings!")
		return redirect('core:patient_dashboard',finding_model.patient.id)
	finding_model.note = finding
	images = request.POST.getlist('images')
	print('images:',len(images))
	if len(images)>0:
		for image in images:
			print(image)
			image_object= File()
			image_object.file = image
			if image_object.file:
				image_object.save()
				finding_model.save()
				finding_model.file.add(image_object)

	finding_model.save()
	messages.success(request, 'Successful!')
	return redirect('core:patient_dashboard',finding_model.patient.id)

def DeleteParaclinicalFinding(request,finding_id):
	finding_model = PatientParaclinicalFinding.objects.get(id=finding_id)
	findings_model.active = False
	finding_model.save()
	messages.success(request, 'Successful!')
	return redirect('core:patient_dashboard',finding_model.patient.id)

def RemoveFile(request,file_id,patient_id):
	patient = Patient.objects.get(id=patient_id)
	file_model = File.objects.get(id=file_id)
	file_model.delete()

	messages.success(request, 'Successful!')
	return redirect('core:patient_dashboard',patient.id)

def AddSurgery(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	if request.method == 'POST':
		surgery_form = PatientSurgeryForm(request.POST)
		if surgery_form.is_valid():
			surgery_model = surgery_form.save(commit=False)
			surgery_model.registered_on = datetime.datetime.now()
			surgery_model.registered_by = Employee.objects.get(user_profile=request.user)
			surgery_model.active=True
			surgery_model.patient = patient
			surgery_model.save()
			messages.success(request, 'Successful!')
			return redirect('core:patient_dashboard',patient.id)
		else:
			messages.error(request,str(surgery_form.errors))
			return redirect('core:patient_dashboard',patient.id)

def EditSurgery(request,surgery_id):
	surgery_model = PatientSurgery.objects.get(id=surgery_id)
	note = str(request.POST.get('note')) or 'None'
	print('finding: ',note)
	if note == 'None':
		messages.error(request,"Add Surgery!")
		return redirect('core:patient_dashboard',surgery_model.patient.id)
	surgery_model.note = note
	surgery_model.save()
	messages.success(request, 'Successful!')
	return redirect('core:patient_dashboard',surgery_model.patient.id)

def DeleteSurgery(request,surgery_id):
	surgery_model = PatientSurgery.objects.get(id=surgery_id)
	surgery_model.active = False
	surgery_model.save()

	messages.success(request, 'Successful!')
	return redirect('core:patient_dashboard',finding_model.patient.id)


def EditPatient(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	
	registration_form = PatientRegistrationForm2(patientid=patient.id)
	medical_form = PatientMedicalHistoryForm(patientid=patient.id)
	social_form = PatientSocialHistoryForm(patientid=patient.id)
	surgery_form = PatientSurgeryHistoryForm(patientid=patient.id)
	
	email_form = PatientEmailForm(patientid=patient.id)
	blood_group_form = PatientBloodGroupForm(patientid=patient.id)
	family_form = PatientFamilyHistoryForm(patientid=patient_id)
	personal_form = AdditionalPatientInfoForm(patientid=patient.id)
	occupation_form = PatientOccupationForm(patientid=patient.id)
	create_occupation_form = CreateOccupationForm()

	contact_form = PersonInfoForm()
	edit_contact_form = EditPersonInfoForm(patientid=patient_id)
	copayer_form = CopayerForm()

	contact_list = PersonInfo.objects.all()
	copayer_list = Copayer.objects.filter(patient=patient)

	family_medic_form = FamilyMedicForm(patientid=patient.id)
	referrer_form = ReferrerForm()
	note_form = PatientNoteForm(patientid=patient.id)
	systems_form = ReviewOfSystemsForm()


	context = {'patient':patient,
				'registration_form':registration_form,
				'email_form':email_form,
				'blood_group_form':blood_group_form,
				'medical_form':medical_form,
				'social_form':social_form,
				'family_form':family_form,
				'surgery_form':surgery_form,

				'personal_form':personal_form,
				'occupation_form':occupation_form,
				'contact_form':contact_form,
				'edit_contact_form':edit_contact_form,
				'copayer_form':copayer_form,

				'contact_list':contact_list,
				'copayer_list':copayer_list,

				'family_medic_form':family_medic_form,
				'referrer_form':referrer_form,
				'note_form':note_form,
				'create_occupation_form':create_occupation_form,
				'systems_form':systems_form,
	}
	return render(request,'core/edit_patient.html', context)

def EditPatientProcess(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	if request.method == 'POST':
		has_changed2 = 0
		registration_form = PatientRegistrationForm2(request.POST,patientid=patient.id)
		#medical_form = PatientMedicalHistoryForm(request.POST)
		if registration_form.has_changed():
			print('it has changed')
			has_changed2 = 1
			if registration_form.is_valid():
				registration_model = registration_form.save(commit=False)
				for f in registration_form.changed_data:
					print(registration_form.changed_data,'\n')
					field = str(f)
					print(f,field,'\n')
					print(request.POST[f],'\n')
					setattr(patient,f,request.POST[f])
					#patient.f = registration_model.str(field)
					print(patient.grandfather_name,'worked')
				patient.save()
			else:
				messages.error(request,str(registration_form.errors))
				return redirect('core:edit_patient',patient_id)
		email_form = PatientEmailForm(request.POST,patientid=patient.id)
		if email_form.has_changed():
			print('email has changed')
			has_changed2 = 1
			if email_form.is_valid():
				for f in email_form.changed_data:
					print(f,field,'\n')
					print(request.POST[f],'\n')
					setattr(patient,f,request.POST[f])
				patient.save()
			else:
				messages.error(request,str(email_form.errors))
				return redirect('core:edit_patient',patient_id)
	
		blood_group_form = PatientBloodGroupForm(request.POST,patientid=patient.id)
		if blood_group_form.has_changed():
			print('blood group has changed')
			has_changed2 = 1
			if blood_group_form.is_valid():
				try:
					blood_group = PatientBloodGroup.objects.get(patient=patient)
				except Exception as e:
					blood_group = PatientBloodGroup()
					blood_group.patient = patient
					blood_group.active = True
					blood_group.registered_on = datetime.datetime.now()
				for f in blood_group_form.changed_data:
					print(request.POST[f],'\n')
					setattr(blood_group,f,request.POST[f])
				blood_group.save()
			else:
				messages.error(request,str(blood_group_form.errors))
				return redirect('core:edit_patient',patient_id)

		family_medic_form = FamilyMedicForm(request.POST,patientid=patient.id)
		if family_medic_form.has_changed():
			has_changed2 = 1
			if family_medic_form.is_valid():
				try:
					family_medic = PatientFamilyMedic.objects.get(patient=patient)
				except Exception as e:
					family_medic = PatientFamilyMedic()
					family_medic.patient = patient
					family_medic.active = True
					family_medic.registered_on = datetime.datetime.now()

				for f in family_medic_form.changed_data:
					print(f,'\n')
					print('medic',request.POST[f],'\n')
					person = PersonInfo.objects.get(id=request.POST[f])
					setattr(family_medic,f,person)
				family_medic.save()
			else:
				messages.error(request,str(family_medic_form.errors))
				return redirect('core:edit_patient',patient_id)


		note_form = PatientNoteForm(request.POST,patientid=patient.id)
		if note_form.has_changed():
			has_changed2 = 1
			print('55')
			if note_form.is_valid():
				try:
					patient_note = PatientNote.objects.get(patient=patient)
				except Exception as e:
					patient_note = PatientNote()
					patient_note.patient = patient
					patient_note.active = True
					patient_note.registered_on = datetime.datetime.now()

				for f in note_form.changed_data:
					print(request.POST[f],'\n')
					setattr(patient_note,f,request.POST[f])
				patient_note.save()
			else:
				messages.error(request,'error'+str(note_form.errors))
				return redirect('core:edit_patient',patient_id)
		medical_history_form = PatientMedicalHistoryForm(request.POST,patientid=patient.id)
		if medical_history_form.has_changed():
			has_changed2 = 1
			if medical_history_form.is_valid():
				try:
					medical_history = PatientMedicalHistory.objects.get(patient=patient)
				except Exception as e:
					medical_history = PatientMedicalHistory()
					medical_history.patient = patient
				for f in medical_history_form.changed_data:
					print(request.POST[f],'\n')
					setattr(medical_history,f,request.POST[f])
				medical_history.save()
			else:
				messages.error(request,str(medical_history_form.errors))
				return redirect('core:edit_patient',patient_id)
		social_form = PatientSocialHistoryForm(request.POST,patientid=patient.id)
		if social_form.has_changed():
			has_changed2 = 1
			if social_form.is_valid():
				try:
					social_history = PatientSocialHistory.objects.get(patient=patient)
				except Exception as e:
					social_history = PatientSocialHistory()
					social_history.patient = patient
				for f in social_form.changed_data:
					print(request.POST[f],'\n')
					setattr(social_history,f,request.POST[f])
				social_history.save()
			else:
				messages.error(request,str(social_form.errors))
				return redirect('core:edit_patient',patient_id)
		family_form = PatientFamilyHistoryForm(request.POST,patientid=patient.id)
		if family_form.has_changed():
			has_changed2 = 1
			if family_form.is_valid():
				try:
					family_history = PatientFamilyHistory.objects.get(patient=patient)
				except Exception as e:
					family_history = PatientFamilyHistory()
					family_history.patient = patient
				for f in family_form.changed_data:
					print(request.POST[f],'\n')
					setattr(family_history,f,request.POST[f])
				family_history.save()
			else:
				messages.error(request,str(family_form.errors))
				return redirect('core:edit_patient',patient_id)
		occupation_form = PatientOccupationForm(request.POST,patientid=patient.id)
		if occupation_form.has_changed():
			has_changed2 = 1
			if occupation_form.is_valid():
				try:
					occupation = PatientOccupation.objects.get(patient=patient)
				except Exception as e:
					occupation = PatientOccupation()
					occupation.patient = patient
					occupation.active = True
					occupation.registered_on = datetime.datetime.now()

				for f in occupation_form.changed_data:
					print(request.POST[f],'\n')
					setattr(occupation,f,request.POST[f])
				occupation.save()
			else:
				messages.error(request,str(occupation_form.errors))
				return redirect('core:edit_patient',patient_id)
		personal_form = AdditionalPatientInfoForm(request.POST,patientid=patient.id)
		if personal_form.has_changed():
			has_changed2 = 1
			if personal_form.is_valid():
				try:
					info = AdditionalPatientInfo.objects.get(patient=patient)
				except Exception as e:
					info = AdditionalPatientInfo()
					info.patient = patient
					info.active = True
					info.registered_on = datetime.datetime.now()

				for f in personal_form.changed_data:
					print(request.POST[f],'\n')
					setattr(info,f,request.POST[f])
				info.save()
			else:
				messages.error(request,str(personal_form.errors))
				return redirect('core:edit_patient',patient_id)

		print('559')
		print(has_changed2)
		if has_changed2 == 1:
			print('dd')
			messages.success(request,"Successful!")
			return redirect('core:edit_patient',patient_id)
		else:
			print('cc')
			messages.success(request,"No Changes!")
			return redirect('core:edit_patient',patient_id)

def SavePersonInfo(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	if request.method == 'POST':
		info_form = PersonInfoForm(request.POST)
		if info_form.is_valid():
			info_model = info_form.save(commit=False)
			info_model.registered_on = datetime.datetime.now()
			info_model.registered_by = Employee.objects.get(user_profile=request.user)
			info_model.active=True
			info_model.patient = patient
			info_model.save()
			messages.success(request, 'Successful!')
			return redirect('core:edit_patient',patient.id)
		else:
			messages.error(request,str(info_form.errors))
			return redirect('core:edit_patient',patient.id)

def SaveEmergencyContact(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	if request.method == 'POST':
		info_form = PersonInfoForm(request.POST)
		if info_form.is_valid():
			info_model = info_form.save(commit=False)
			info_model.registered_on = datetime.datetime.now()
			info_model.registered_by = Employee.objects.get(user_profile=request.user)
			info_model.active=True
			info_model.patient = patient
			info_model.person_type = 3
			info_model.save()
			messages.success(request, 'Successful!')
			return redirect('core:edit_patient',patient.id)
		else:
			messages.error(request,str(info_form.errors))
			return redirect('core:edit_patient',patient.id)

def EditEmergencyContact(request,contact_id):
	info_model = PersonInfo.objects.get(id=contact_id)
	allergy = str(request.POST.get('allergy')) or 'None'
	if allergy == 'None':
		messages.error(request,"Add Allergy!")
		return redirect('core:patient_dashboard',patient.id)
	allergy_model.allergy = allergy
	allergy_model.save()
	messages.success(request, 'Successful!')
	return redirect('core:patient_dashboard',allergy_model.patient.id)

def CreateOccupation(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	if request.method == 'POST':
		create_occupation_form = CreateOccupationForm(request.POST)
		if create_occupation_form.is_valid():
			create_occupation_form.save()
			messages.success(request, 'Successful!')
			return redirect('core:edit_patient',patient.id)
		else:
			messages.error(request,str(create_occupation_form.errors))
			return redirect('core:edit_patient',patient.id)

def CreateCopayer(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	if request.method == 'POST':
		copayer_form = CopayerForm(request.POST)
		if copayer_form.is_valid():
			copayer_form = copayer_form.save(commit=False)
			copayer_form.patient = patient
			copayer_form.registered_on = datetime.datetime.now()
			copayer_form.active=True
			copayer_form.save()
			messages.success(request, 'Successful!')
			return redirect('core:edit_patient',patient.id)
		else:
			messages.error(request,str(copayer_form.errors))
			return redirect('core:edit_patient',patient.id)


def EditPatientConsultation(request,consultation_id):
	consultation = PatientConsultation.objects.get(id=consultation_id)
	patient = consultation.patient
	edit_consultation_form = EditPatientConsultationForm(consultation_id = consultation.id)
	edit_partial_consultation_form = EditPartialConsultationForm(consultation_id = consultation.id)

	edit_systems_form = EditReviewOfSystemsForm(consultation_id = consultation.id)
	edit_vital_sign_form = EditVitalSignForm(consultation_id = consultation.id)
	edit_physical_exam_form = EditPhysicalExamForm(consultation_id = consultation.id)
	test_type_list = LaboratoryTestType.objects.all()
	section_list = LaboratorySection.objects.all()
	context = {'patient':patient,
				'edit_consultation_form':edit_consultation_form,
				'edit_partial_consultation_form':edit_partial_consultation_form,
				'edit_systems_form':edit_systems_form,
				'edit_vital_sign_form':edit_vital_sign_form,
				'edit_physical_exam_form':edit_physical_exam_form,
				'test_type_list':test_type_list,
				'section_list':section_list,

	}
	return render(request,'core/edit_patient_consultation.html', context)

def DeletePatientConsultation(request,consultation_id,url_arg):
	consultation = PatientConsultation.objects.get(id=consultation_id)
	consultation.active = False
	consultation.save()
	if url_arg == "activities":
		messages.success(request,'Successfuly Deleted!')
		return redirect('core:activities', consultation.patient.id)


def AddPatientConsultation(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	consultation_form = PatientConsultationForm()
	partial_consultation_form = PartialConsultationForm()

	systems_form = ReviewOfSystemsForm()
	vital_sign_form = VitalSignForm()
	physical_exam_form = PhysicalExamForm()
	test_type_list = LaboratoryTestType.objects.all()
	section_list = LaboratorySection.objects.all()
	context = {'patient':patient,
				'consultation_form':consultation_form,
				'partial_consultation_form':partial_consultation_form,
				'systems_form':systems_form,
				'vital_sign_form':vital_sign_form,
				'physical_exam_form':physical_exam_form,
				'test_type_list':test_type_list,
				'section_list':section_list,

	}
	return render(request,'core/add_patient_consultation.html', context)

def SavePatientConsultation(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	if request.method == 'POST':
		consultation_form = PatientConsultationForm(request.POST)
		tag_array = []
		compliant_array = []
		clinical_finding_array = []

		for tag in consultation_form['tags'].value():
			tag, created = Tag.objects.get_or_create(name=tag)
			if created: tag.save()
			tag_array.append(tag)
		for comp in consultation_form['compliant'].value():
			compliant, created = Compliant.objects.get_or_create(compliant=comp)
			if created: compliant.save()
			compliant_array.append(compliant)
		for clinical_finding in consultation_form['clinical_finding'].value():
			clinical_finding, created = PatientClinicalFinding.objects.get_or_create(clinical_finding=clinical_finding)
			if created: clinical_finding.save()
			clinical_finding_array.append(clinical_finding)

		consultation_form = PartialConsultationForm(request.POST)
		if consultation_form.is_valid():
			consultation_model = consultation_form.save(commit=False)
			consultation_model.patient = patient
			consultation_model.registered_on = datetime.datetime.now()
			consultation_model.registered_by = Employee.objects.get(user_profile=request.user)
			consultation_model.save()
			for tag in tag_array:
				consultation_model.tags.add(tag)            
			consultation_model.save()
			messages.success(request,'Successful!')
			return redirect('core:add_patient_consultation',patient_id)

		else:
			messages.error(request,str(consultation_form.errors))
			return redirect('core:add_patient_consultation',patient_id)


def PatientList(request,url_arg):
	small_letters = map(chr, range(ord('a'), ord('z')+1))

	patient_name = request.GET.get('search-patient',None)


	patient_list = Patient.objects.all()
	if patient_name == None:
		print('noneenennenenenenenennen333333333333555555','\n')
	else:
		print('patient id equals:',patient_name,'\n')
		patient_list = patient_list.filter(last_name__icontains=patient_name)

	context = {'patient_list':patient_list,
				'small_letters':small_letters,
				'url_arg':url_arg,

	}

	if request.htmx:
		gender_value = request.GET.get('ward_status')
		gender_value2 = request.GET.get('ward_status_outpatient')
		gender_value3 = request.GET.get('all_ward_status')
		letter_value = request.GET.get('alphabet')

		if gender_value == 'Inpatient':
			patient_list = Bed.objects.filter().first().return_ward_patients
		if gender_value2 == 'Outpatient':
			patient_list = Bed.objects.filter().first().return_outpatients
		if gender_value3 == 'All':
			patient_list = Patient.objects.all()

		print('HTMX')
		print("request id:",gender_value)
		print("request id2:",gender_value2)
		print("request id3:",letter_value)


		#filter_request = request.GET.get('patient_')
		#print("request id:",filter_request )
		alphabet_value = request.GET.getlist('alphabet')
		if alphabet_value == None:
			print('')
		else:	
			patient_list = patient_list.filter(last_name__startswith=alphabet_value[0])

		print(alphabet_value[0])

		#if filter_request == "PlanStatus":
		#    plan_status_value = request.GET.getlist('plan_status')
		#    print("request id:",plan_status_value )
		try_htmx = 'dd'
		for p in patient_list:
			print('\n',p,'\n')
		context2 = {'try_htmx':try_htmx,
					'patient_list':patient_list

		}
		return render(request,'core/htmx_partials/patient_list_htmx.html', context2)

	return render(request,'core/patient_list.html', context)

def DeletePatient(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	patient.active = False
	patient.save()
	messages.success(request,'Successfuly Deleted!')
	return redirect('core:patient_list', 'None')

def BedCalendar(request):
	thirty_days_ago = datetime.datetime.now() - datetime.timedelta(days=15)
	thirty_days_after = datetime.datetime.now() + datetime.timedelta(days=15)
	day_list = list(rrule(DAILY, thirty_days_ago,until=thirty_days_after))
	bed_list = Bed.objects.all()
	bed = Bed.objects.get(id=17)
	category_list = BedCategory.objects.all()
	patient_list = Patient.objects.all()

	#print(bed.is_admitted(thirty_days_ago,bed.id)) 
	#range1 = list(rrule(MONTHLY, dtstart=datetime(2020,1,2)))
	#for d in range1:
	#    print(d)

	#thirty_days_ago = datetime.datetime.now() - datetime.timedelta(days=30)
	calendar = True
	today = datetime.datetime.now().date()
	records_submenu = True	
	activities_tab = True
	context = {'day_list':day_list,
				'records_submenu':records_submenu,
				'activities_tab':activities_tab,

				'bed_list':bed_list,
				'thirty_days_ago':thirty_days_ago,
				'category_list':category_list,
				'patient_list':patient_list,
				'calendar':calendar,
				'initial_date': str(today),
				'today': today,

	}
	return render(request,'core/bed_calendar.html', context)


def BedsCalendar(request):

# The `chartConfig` dict contains key-value pairs of data for chart attribute
	chartConfig = OrderedDict()
	chartConfig["caption"] = "Demo Values"
	chartConfig["subCaption"] = ""
	chartConfig["xAxisName"] = "Date"
	chartConfig["yAxisName"] = "Value"
	chartConfig["numberSuffix"] = ""
	chartConfig["theme"] = "fusion"
	chartConfig["numVisiblePlot"] = "8",
	chartConfig["flatScrollBars"] = "1",
	chartConfig["scrollheight"] = "1",
	chartConfig["type"] = "pie2d",


	context = {'day_list':day_list,
				'bed_list':bed_list,

	}
	return render(request,'core/bed_calendar.html', context)

def LabRequests(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	order_list = Order.objects.all()[::-1]
	context = {'patient':patient,
				'order_list':order_list,
	}
	return render(request,'core/lab_requests.html', context)

def AddLabRequest(request,patient_id):
	section_list = LaboratorySection.objects.all()
	patient = Patient.objects.get(id=patient_id)

	context = {'section_list':section_list,
				'patient':patient,
	}
	return render(request,'core/add_lab_request.html', context)


def AddLabCase(request,order_id):
	order = Order.objects.get(id=order_id)
	results = LaboratoryTestResult.objects.filter(test__order=order)

	specimen_form = SpecimenForm()
	context = {'order':order,
				'test_type_set':order.test_set.all(),
				'specimen_form':SpecimenForm(),
				'results':results,

	}
	return render(request,'core/add_lab_case.html', context)
