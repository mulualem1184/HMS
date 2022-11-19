from django.shortcuts import render
from django.http import JsonResponse

from .models import *
from billing_app.models import * 
from pharmacy_app.models import *
from pharmacy_app.forms import PrescriptionForm,PrescriptionInfoForm

from staff_mgmt.models import (Attendance, AttendanceReport, Department, Designation,
					 Employee, EmployeeDocument, ShiftType, StaffLeave, WorkShift)
from staff_mgmt.forms import (ChangePasswordForm, DepartmentForm,
							  DesignationForm, EmployeeDocumentForm,
							  EmployeeForm, FilterScheduleForm, LeaveForm, ResetPasswordForm,
							  UpdateAttendanceForm, UserForm, WorkShiftForm)
from notification.models import notify

from staff_mgmt.utils import TimeOverlapError, generate_random_color, get_time_difference
from django.urls import reverse

from django.views import View

from django.contrib import messages
from .forms import *
from outpatient_app.forms import VitalSignForm,AppointmentForm
from django.shortcuts import redirect

from django.db.models import Sum

from datetime import datetime
from datetime import  timedelta
import itertools

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from collections import OrderedDict
from .fusioncharts import FusionCharts
from core.forms import PatientTreatmentForm,RecurrenceForm

# Create your views here.
def HospitalStructure(request):
	"""
	this allows users to create stocks by entering how much 
	shelf it has and how much slot each shelf has
	"""
	bed_form = BedForm()
	"""
	beds = Bed.objects.all()
	bed_array = []
	for bed in beds:
		bed_array.append(bed)
		print(bed)
	bed_form.fields["bed"].queryset = bed_array
	"""
	hospital_structure_form = HospitalStructureForm()
	category_form = BedCategoryForm()

	if request.method == 'POST':
		hospital_structure_form = HospitalStructureForm(request.POST)
		category_form = BedCategoryForm(request.POST)
		if hospital_structure_form.is_valid():
			category_model = category_form.save()
#			print(inventory_structure_form.data['stock'])
			unit_name = hospital_structure_form.data['building_name']
			ward_amount =int( hospital_structure_form.data['ward_amount'])
			bed_amount = int(hospital_structure_form.data['bed_amount'])
			hospital_unit_model = HospitalUnit()
			hospital_unit_model.unit_name = unit_name
			hospital_unit_model.save()				
			# below code generates amount of shelf as stated in form
			for i in range(1,ward_amount + 1):
				ward_model = Ward()
				ward_model.ward_number = i
				ward_model.hospital_unit = hospital_unit_model
				ward_model.save()
				# below code generates amount of slot for each shelf as stated in form
				for j in range(1, bed_amount + 1):
					bed_model = Bed()
					bed_model.bed_number = j
					bed_model.ward = ward_model
					bed_model.category = category_model
					
					bed_model.save()
			messages.success(request,'Successful!')
	context = {'hospital_structure_form': hospital_structure_form,
				'bed_form':bed_form,
				'category_form':category_form,
				}
	return render(request,'inpatient_app/hospital_structure.html',context)

def WholeWardView(request):
	start_date = datetime.strptime(request.GET.get('start_date') or '1970-10-01', '%Y-%m-%d')
	end_date = datetime.strptime(request.GET.get('end_date') or str(datetime.now().date()),  '%Y-%m-%d')
	end_date = end_date + timedelta(days=1)
	patient_list = Patient.objects.all()
	check_input = request.GET.get('check_input',None)
	print('Check',check_input)	
	plan_list = IPDTreatmentPlan.objects.filter(active=True,registered_on__range=[start_date,end_date])
	bed_list = Bed.objects.all()
	building_list = HospitalUnit.objects.filter(active=True)
	ward_list = Ward.objects.filter(active=True)
	category_list = BedCategory.objects.all()


	plan_text = request.GET.get('search-plan',None)
	filtered_status = request.GET.get('treatment_plan_status',None)
	filtered_patient_id = request.GET.get('patient',None)

	active_tab = None
	print(plan_text)
	if plan_text == None:
		print('')
	else:
		plan_list = plan_list.filter(patient__last_name__icontains=plan_text)
		active_tab = 'plan_tab'

	if filtered_status == None:
		print('none 1')
	elif filtered_status == '2':
		plan_list = plan_list.filter(status__isnull=True)
		active_tab = 'plan_tab'
	elif filtered_status == '3':
		plan_list = plan_list.filter(status='Completed')
		active_tab = 'plan_tab'
	elif filtered_status == '4':
		plan_list = plan_list.filter(status='Dismissed')
		active_tab = 'plan_tab'

	if filtered_patient_id == None:
		print('none 2')
	elif filtered_patient_id == '0':
		print('0000')
	else:
		print('patient is    : ',filtered_patient_id)
		plan_list = plan_list.filter(patient=Patient.objects.get(id=filtered_patient_id))
		active_tab = 'plan_tab'
	plan_list = plan_list[::-1]
	d = request.GET.get('d',None)
	c = request.GET.get('tagss',None)
	sb = request.GET.get('search-building',None)

	bed_list = Bed.objects.all()
	building_list = HospitalUnit.objects.filter(active=True)
	ward_list = Ward.objects.filter(active=True)

	category_list = BedCategory.objects.all()

	patient_array = []
	patient_form = PatientForm()
	patient_form2 = PatientForm()

	bed_list2= Bed.objects.filter(patient__isnull=False)
	for bed in bed_list2:
		patient_array.append(bed.patient.id)

	patient_form.fields['patient'].queryset = Patient.objects.exclude(id__in=patient_array)
	patient_form2.fields['patient'].queryset = Patient.objects.filter(id__in=patient_array)
	#prediction_form = StayDurationPredictionForm()
	care_plan_list = InpatientCarePlan.objects.filter(status='active')
	treatment_plan_form = IPDTreatmentPlanForm()
	treatment_plan_form.fields['patient'].queryset = Patient.objects.exclude(id__in=patient_array)
	treatment_actions = ['None','Add Prescription','Add Lab Test']

	by_gender = ['MALE','FEMALE','MIXED']
	gender_value = ['MALE','FEMALE','MIXED']

	prescription_form = PrescriptionForm()
	patient_list = Patient.objects.all()
	dynamic_treatment_form = DynamicTreatmentForm()
	manual_treatment_form = ManualTreatmentForm()
	info_form2 = PrescriptionInfoForm()
	appointment_form = AppointmentForm()
	patient_treatment_form = PatientTreatmentForm()
	recurrence_form = RecurrenceForm()


	if request.htmx:
		print('HTMX')
		filter_request = request.GET.get('id')
		print("request id:",filter_request )
		ward_value = request.GET.getlist('ward_category')
		bed_status_value = request.GET.getlist('bed_status')
		bed_list = list(bed_list)
		print("request id:",ward_value )

		plan_list = list(plan_list)
		is_dismissed = False
		is_complete = False

		if filter_request == "PlanStatus":
			plan_status_value = request.GET.getlist('plan_status')
			print("request id:",plan_status_value )

			for status in plan_status_value:
				if status == 'Completed':
					is_complete = True
				else:
					print()
				if status =='Dismissed':
					is_dismissed = True

			if is_complete == True:
				plans = IPDTreatmentPlan.objects.filter(status='Completed')
				for plan in plans:
					if plan in plan_list:
						print('plan already is')
					else:				
						plan_list.append(plan)
			else:
				for plan in plan_list:
					if plan.status == 'Completed':
						plan_list.remove(plan)

			if is_dismissed == True:
				plans = IPDTreatmentPlan.objects.filter(status='Dismissed')
				for plan in plans:
					if plan in plan_list:
						print('dplan already is')
					else:				
						plan_list.append(plan)
			else:
				for plan in plan_list:
					if plan.status == 'Dismissed':
						plan_list.remove(plan)
			if is_complete == False:
				for plan in plan_list:
					if plan.status == 'Completed':
						plan_list.remove(plan)
					print(plan.status)
			context2 = {'plan_list':plan_list}
			return render(request,'inpatient_app/partials/treatment_plan_list_partial.html', context2)

		if filter_request == "GENDER":
			gender_value = request.GET.getlist('gender')

			print('valud: ',gender_value)
			is_male = False
			is_female = False
			is_mixed = False


			for value in gender_value:
				if value == 'MALE':
					is_male = True
				else:
					print('')
				if value == 'FEMALE':
					is_female = True
				else:
					print('')
				if value == 'MIXED':
					is_mixed = True
				else:
					print('')
			if is_male == True:
				print('1')
				beds = Bed.objects.filter(ward__by_gender='MALE')
				for bed in beds:
					if bed in bed_list:
						print('male already is')
					else:
				
						bed_list.append(bed)
			else:
				for bed in bed_list:
					if bed.ward.by_gender == 'MALE':
						bed_list.remove(bed)
				#bed_list = bed_list.exclude(ward__by_gender='MALE')
			if is_female == True:
				print('2')
				beds = Bed.objects.filter(ward__by_gender='FEMALE')
				for bed in beds:
					if bed in bed_list:
						print('female already is')
					else:
						bed_list.append(bed)
			else:			
				for bed in bed_list:
					if bed.ward.by_gender == 'FEMALE':
						bed_list.remove(bed)
				#bed_list = bed_list.exclude(ward__by_gender='FEMALE')
			if is_mixed == True:
				print('3')
				beds = Bed.objects.filter(ward__by_gender='MIXED')
				for bed in beds:
					if bed in bed_list:
						print('mixed already is')
					else:
						bed_list.append(bed)

			else:
				for bed in bed_list:
					if bed.ward.by_gender == 'MIXED':
						bed_list.remove(bed)
				
				#bed_list = bed_list.exclude(ward__by_gender='MIXED')

		is_occupied = False
		is_free = False

		if filter_request == "BedStatus":
			bed_status_value = request.GET.getlist('bed_status')
			for value in bed_status_value:
				if value == 'FREE':
					is_free = True
				else:
					print('')
				if value == 'FEMALE':
					is_occupied = True
				else:
					print('')
			if is_free == True:
				print('1')
				beds = Bed.objects.filter(patient__isnull=True)
				for bed in beds:
					if bed in bed_list:
						print('free already is')
					else:				
						bed_list.append(bed)
			else:
				for bed in bed_list:
					if bed.patient ==None:
						bed_list.remove(bed)

			if is_occupied == True:
				print('1')
				beds = Bed.objects.filter(patient__isnull=False)
				for bed in beds:
					if bed in bed_list:
						print('occupied already is')
					else:				
						bed_list.append(bed)
			else:
				for bed in bed_list:
					if bed.patient:
						print('removivivi')
						bed_list.remove(bed)

		category_array = []
		for bed in bed_list:
			if bed.ward.category in category_array:
				print('')
			else:
				category_array.append(bed.ward.category)

		if filter_request == "Ward":
			print('it is ward')
			ward_value = request.GET.getlist('ward_category')

			category_list = category_array			
			for category in BedCategory.objects.all():
				if category.id in ward_value:
					print()
					pritn('WArd already there')
				else:
					if category in category_list:
						print('category remmoved:', category)
						category_list.remove(category)
			for value in ward_value:
				category = BedCategory.objects.get(id=value)
				if category in category_list:
					print('al')
				else:
					print('category added:', category)
					category_list.append(category)


		#bed_list2 = bed_list.filter(ward__by_gender='MIXED')
		ward_list2 = Ward.objects.filter(active=True,by_gender='MIXED')
		
		#for c in category_list2:
		#	print(c,'\n')		
		#dispensed_drugs2 = DrugDispensed.objects.filter(dispensary_id=dispensary_id)

		context2 = {'bed_list':bed_list,
					'ward_list2':ward_list2,
					'ward_list':ward_list,
					'category_list':category_list,
					'gender_value':gender_value
		}
		return render(request,'inpatient_app/partials/ward_view_partial.html', context2)
	context = {'patient_list':patient_list,
				'bed_list':bed_list,
				'ward_list':ward_list,

				'building_list':building_list,
				'category_list':category_list,
				'gender_value':gender_value,

				'patient_form':patient_form,
				'patient_form2':patient_form2,

				#'prediction_form':prediction_form,
				'appointment_form':appointment_form,
				'recurrence_form':recurrence_form,

				'care_plan_list':care_plan_list,
				'by_gender':by_gender,

				'treatment_plan_form':treatment_plan_form,
				'prescription_form':prescription_form,
				'info_form2':info_form2,

				'plan_list':plan_list,
				'active_tab':active_tab,

				'dynamic_treatment_form':dynamic_treatment_form,
				'manual_treatment_form':manual_treatment_form,
				'patient_treatment_form':patient_treatment_form,


	}
	return render(request,'inpatient_app/whole_ward_view.html', context)


def PatientList(request):
	beds = Bed.objects.filter(patient__isnull=False)
	patients = Patient.objects.filter(inpatient='yes')
	allocated_patients = []
	patient_list = []
	for bed in beds:
		allocated_patients.append(bed.patient)
#		patient_list = [allocated_patients,for bed in beds allocated_patients.append(bed.patient)]

	for patient in patients:
		if patient not in allocated_patients:
			patient_list.append(patient)
	priority_array = []
	for patient in patient_list:
		patient_priority = AdmissionPriorityLevel.objects.get(patient=patient, status='active')
		priority_array.append(patient_priority)
	bed_release_Date = BedReleaseDate.objects.filter(status='active')		

	inpatient_zip = zip(patient_list, priority_array)

	#patient_list = Patient.objects.all()
	
	bed_form = BedForm()
	context = {'patient_list':patient_list,
				'bed_release_Date':bed_release_Date,
				'inpatient_zip':inpatient_zip,
				}
	return render(request,'inpatient_app/patient_list.html',context)


# Create your views here.
def AdmitPatientToWard(request,bed_id,value):
	print('dxn value:',value,'\n')
	bed = Bed.objects.get(id=bed_id)	
	if request.method == 'POST':
		patient_name = request.POST.get('patient_input',None)
		patient = None
		found = False
		for patient1 in Patient.objects.all():
			if found == False:
				if patient1.full_name == patient_name:
					print(patient1.full_name," : ",patient_name,'\n')
					print('found it')
					found = True
					patient = patient1
		print(patient)	
		if patient==None:
			messages.error(request,'Invalid Patient Input!')
			return redirect('whole_ward_view')

		#prediction_form = StayDurationPredictionForm(request.POST)
		#patient_form = PatientForm(request.POST)
		#if patient_form.is_valid():
		start_date = datetime.strptime(request.POST.get('start_date') or '2022-11-04', '%Y-%m-%d')
		end_date = datetime.strptime(request.POST.get('end_date') or '2022-11-08',  '%Y-%m-%d')

		#patient_model = patient_form.save(commit=False)
		#patient = patient_model.patient
		#prediction_model = prediction_form.save(commit=False)
		patient_arary = []
		for bed in Bed.objects.all():
			if bed.patient:
				patient_arary.append(bed.patient)
		if patient in patient_arary:
			messages.error(request,'Already Assigned!')
			return redirect('core:bed_calendar')

		if bed.ward.by_gender == 'MIXED':
			bed.patient = patient

		elif patient.sex == bed.ward.by_gender:
			bed.patient = patient
		else:
			messages.error(request,'Cannot Assign To Wrong Gender!')
			if value == 'calendar':
				return redirect('core:bed_calendar')
			else:
				return redirect('whole_ward_view')
			

		prediction_model = PatientStayDurationPrediction()
		prediction_model.patient = patient
		prediction_model.start_date = start_date
		prediction_model.end_date = end_date
		prediction_model.bed = bed
		prediction_model.active =True
		stay_duration = WardStayDuration()
		stay_duration.patient = patient
		stay_duration.admission_date = datetime.now()
		stay_duration.room = bed
		admission_model = InpatientAdmissionAssessment()
		admission_model.patient = patient
		admission_model.admitted_from = 'Direct'
		admission_model.status = True
		admission_model.save()
		prediction_model.save()
		bed.save()
		stay_duration.save()				
		if value == 'calendar':
			messages.success(request,"Successful!")
			return redirect('core:bed_calendar')
		else:
			messages.success(request,"Successful!")
			return redirect('whole_ward_view')
		#else:
		#	messages.error(request,str(patient_form.errors))
		#	return redirect('whole_ward_view')


def EditWardAdmission(request, bed_id):
	bed = Bed.objects.get(id=bed_id)
	if request.method == 'POST':
		patient_name = request.POST.get('patient_input',None)
		patient = None
		found = False
		for patient1 in Patient.objects.all():
			if found == False:
				if patient1.full_name == patient_name:
					print(patient1.full_name," : ",patient_name,'\n')
					print('found it')
					found = True
					patient = patient1
		print(patient)	
		if patient==None:
			messages.error(request,'Invalid Patient Input!')
			return redirect('whole_ward_view')

		#prediction_form = StayDurationPredictionForm(request.POST)
		#patient_form = PatientForm(request.POST)
		#if patient_form.is_valid():
		start_date = datetime.strptime(request.GET.get('start_date') or '2022-10-18', '%Y-%m-%d')
		end_date = datetime.strptime(request.GET.get('end_date') or '2022-10-29',  '%Y-%m-%d')
		print('patient:',bed.patient)
		prediction_model = PatientStayDurationPrediction.objects.get(patient=bed.patient, active=True)
		prediction_model.patient = patient
		prediction_model.start_date = start_date
		prediction_model.end_date = end_date
		prediction_model.active =True
		stay_duration = PatientStayDuration.objects.get(patient=bed.patient, leave_date__isnull=True)
		stay_duration.patient = patient
		stay_duration.admission_date = start_date
		stay_duration.room = bed
		admission_model = InpatientAdmissionAssessment.objects.get(patient=bed.patient, status=True)
		"""
		count = 0
		for m in admission_model:
			if count == 0:
				m.delete()
				count=1
				return redirect('whole_ward_view')
		"""
		admission_model.patient = patient
		admission_model.admitted_from = 'Direct'
		admission_model.status = True
		bed.patient = patient
		admission_model.save()
		prediction_model.save()
		
		bed.save()
		stay_duration.save()				
		messages.success(request, 'Successful!')
		return redirect('whole_ward_view')

def DeleteWardAdmission(request, bed_id):
	bed = Bed.objects.get(id=bed_id)
	patient = bed.patient
	prediction_model = PatientStayDurationPrediction.objects.get(patient=bed.patient, active=True)
	prediction_model.active =False
	#stay_duration = PatientStayDuration.objects.get(patient=bed.patient, leave_date__isnull=True)
	admission_model = InpatientAdmissionAssessment.objects.get(patient=bed.patient, status=True)

	admission_model.status = False
	summary = WardDischargeSummary.objects.get(patient=bed.patient, active=True)
	summary.active=False

	bed.patient = None
	summary.save()
	admission_model.save()
	prediction_model.save()
	
	bed.save()
	#stay_duration.delete()				
	messages.success(request, 'Successful!')
	return redirect('inpatient_bill_detail',patient.id)

def SaveTreatmentPlan2(request):
	if request.method == 'POST':
		patient_name = request.POST.get('patient_input',None)
		patient = None
		found = False
		for patient in Patient.objects.all():
			if found == False:
				#print(patient.full_name," : ",patient_name,'\n')
				if patient.full_name == patient_name:
					#print('found it')
					found = True
					patient = patient
		#print(patient)	
		if patient==None:
			messages.error(request,'Invalid Patient Input!')
			return redirect('whole_ward_view')
		plan_form = IPDTreatmentPlanForm(request.POST)
		chosen_action = int(request.POST.get('action_select')) or 'None'
		chosen_recurrence = int(request.POST.get('recurrence')) or 'None'
		print('chosen: ',chosen_recurrence)
		if plan_form.is_valid():
			plan_model = plan_form.save(commit=False)
			plan_model.registered_on = datetime.now()
			plan_model.start_time = datetime.now()
			plan_model.active=True
			plan_model.patient=patient

			plan_model.name = 'nameesf'
			plan_model.description = 'descdksks'

			if chosen_recurrence == 1:
				print('chosen_recurrence1')
				recurrence_form = RecurrenceForm(request.POST)
				if recurrence_form.is_valid():
					recurrence_model = recurrence_form.save(commit=False)
					recurrence_model.daily = True
					recurrence_model.active=True
					plan_model.recurrence = recurrence_model
					recurrence_model.save()
					#plan_model.save()
					#messages.success(request,'Successful')
					#return redirect('whole_ward_view')

			elif chosen_recurrence == 2:
				print('chosen_recurrence2')
				recurrence_form = RecurrenceForm(request.POST)
				if recurrence_form.is_valid():
					recurrence_model = recurrence_form.save(commit=False)
					recurrence_model.weekly = True
					recurrence_model.active=True
					plan_model.recurrence = recurrence_model
					recurrence_model.save()

			elif chosen_recurrence == 3:
				print('chosen_recurrence3')
				recurrence_form = RecurrenceForm(request.POST)
				if recurrence_form.is_valid():
					recurrence_model = recurrence_form.save(commit=False)
					recurrence_model.monthly = True
					recurrence_model.active=True
					plan_model.recurrence = recurrence_model
					recurrence_model.save()

			elif chosen_recurrence == 4:
				print('chosen_recurrence4')
				recurrence_form = RecurrenceForm(request.POST)
				if recurrence_form.is_valid():
					recurrence_model = recurrence_form.save(commit=False)
					recurrence_model.yearly = True
					recurrence_model.active=True
					plan_model.recurrence = recurrence_model
					recurrence_model.save()

			if chosen_action == 'None':
				print('yes it',)
			else:
				print('jjjjjjkkkk',plan_model.name)
				print(chosen_action)
				if chosen_action == 0:
					plan_model.save()
				elif chosen_action == 1:
					prescription_form = PrescriptionForm(request.POST)
					if prescription_form.is_valid():
						prescription_model = prescription_form.save(commit=False)
						if prescription_model.info:
							prescription_model.department = 'Ward'
							prescription_model.registered_on = datetime.now()
							plan_model.prescription = prescription_model
							prescription_model.save()
							plan_model.save()
							messages.success(request,'Successful')
							return redirect('whole_ward_view')
					else:
						messages.error(request,str(prescription_form.errors))
						return redirect('whole_ward_view')

					prescription_form = PrescriptionForm(request.POST)
					info_form2 = PrescriptionInfoForm(request.POST)

					if prescription_form.is_valid():
						info_model = info_form2.save(commit=False)
						prescription_model = prescription_form.save(commit=False)

						prescription_model.department = 'Ward'
						prescription_model.registered_on = datetime.now()
						plan_model.prescription = prescription_model
						prescription_model.info = info_model
						info_model.save()
						prescription_model.save()
						plan_model.save()
						messages.success(request,'Successful')
						return redirect('whole_ward_view')
					else:
						messages.error(request,str(prescription_form.errors))
						return redirect('whole_ward_view')

				elif chosen_action==2:
					patient_treatment_form = PatientTreatmentForm(request.POST)
					print(patient_treatment_form)
					if patient_treatment_form:
						if patient_treatment_form.is_valid():
							
							treatment_model = patient_treatment_form.save(commit=False)
							treatment_model.patient=patient
							if treatment_model.treatment:
								print('do nothing')
							else:
								treatment_model.treatment = 'tresjdfk'
							treatment_model.active=True
							treatment_model.registered_on = datetime.now()
							plan_model.treatment = treatment_model	
							treatment_model.save()
							plan_model.save()
							messages.success(request,'Successful')
							return redirect('whole_ward_view')
							"""
							else:
								messages.error(request,'No t')
								return redirect('whole_ward_view')
							"""
						else:
							messages.error(request,str(treatment_plan_form.errors))
							return redirect('whole_ward_view')

					"""
					manual_treatment_form = ManualTreatmentForm(request.POST)
					if manual_treatment_form:
						if manual_treatment_form.is_valid():
							
							treatment_model = manual_treatment_form.save(commit=False)
							if treatment_model.name:
								treatment_model.active=True
								treatment_model.registered_on = datetime.now()
								plan_model.treatment = treatment_model	
								treatment_model.save()
								plan_model.save()
								messages.success(request,'Successful')
								return redirect('whole_ward_view')

						else:
							messages.error(request,str(manual_treatment_form.errors))
							return redirect('whole_ward_view')
				
					dynamic_treatment_form = DynamicTreatmentForm(request.POST)
					if dynamic_treatment_form.is_valid():
						treatment_model = dynamic_treatment_form.save(commit=False)
						treatment_model = treatment_model.treatment
						plan_model.treatment = treatment_model
						treatment_model.save()
						plan_model.save()
						messages.success(request,'Successfuld')
						return redirect('whole_ward_view')
					else:
						messages.error(request,str(dynamic_treatment_form.errors))
						return redirect('whole_ward_view')
					"""
				elif chosen_action == 3:
					appointment_date = datetime.strptime(request.POST.get('appointment_date') or str(datetime.now().date()),  '%Y-%m-%d')

					#if appointment_form.is_valid():
					#appointment_model = appointment_form.save(commit=False)
					appointment_model = PatientAppointment()
					appointment_model.patient = patient
					appointment_model.registered_on = datetime.now()
					appointment_model.appointment_time = appointment_date
					plan_model.appointment = appointment_model	
					appointment_model.save()
					plan_model.save()
					messages.success(request,'Successfuld')
					return redirect('whole_ward_view')
					#else:
					#messages.error(request,str(dynamic_treatment_form.errors))
					#return redirect('whole_ward_view')


		else:
			messages.error(request,str(plan_form.errors))
			return redirect('whole_ward_view')


def SaveTreatmentPlan(request):
	if request.method == 'POST':
		inpatient_reason_form = InpatientReasonForm(request.POST)
		inpatient_care_plan_form = InpatientCarePlanForm(request.POST)
		patient_form = PatientForm(request.POST)
		assessment_form = InpatientAssessmentForm(request.POST)
		if inpatient_reason_form.is_valid():
			if assessment_form.is_valid():
				inpatient_reason_model = inpatient_reason_form.save(commit=False)
				inpatient_care_plan_model = inpatient_care_plan_form.save(commit=False)
				patient_model = patient_form.save(commit=False)
				assessment_model = assessment_form.save(commit=False)
				patient = patient_model.patient
				employee = Employee.objects.get(user_profile=request.user, designation__name='Doctor')
				inpatient_reason_model.service_provider = employee
				inpatient_reason_model.status = 'active'
				inpatient_reason_model.patient = patient

				inpatient_care_plan_model.service_provider = employee
				inpatient_care_plan_model.status = 'active'
				inpatient_care_plan_model.patient = patient
				
				try:
					emergency_assessment_model = InpatientAdmissionAssessment.objects.get(patient=patient,status=True, general_appearance__isnull=True)
				except:
					messages.error(request,"Patient Must Be Admitted Before Treatment Plan Is Set")
					return redirect('whole_ward_view')
				employee = Employee.objects.get(user_profile=request.user, designation__name='Doctor')
				emergency_assessment_model.service_provider = employee
				emergency_assessment_model.patient = patient
				emergency_assessment_model.general_appearance = assessment_model.general_appearance
				emergency_assessment_model.other_assessment = assessment_model.other_assessment

				emergency_assessment_model.save()
				inpatient_care_plan_model.save()
				inpatient_reason_model.save()
				messages.success(request, 'Successful!')
				return redirect('whole_ward_view')
			else:
				messages.error(request,str(assessment_form.errors))
				return redirect('whole_ward_view')

		else:
			messages.error(request,str(inpatient_reason_form.errors))
			return redirect('whole_ward_view')

def EditTreatmentPlan(request, plan_id):
	if request.method == 'POST':
		patient_id = int(request.POST.get('patient_select')) or 'None'
		name = str(request.POST.get('plan_name')) or 'None'
		#start_date = #datetime.strptime(request.GET.get('start_date') or datetime.now())
		description = str(request.POST.get('description')) or 'None'
		action_value = int(request.POST.get('action_select')) or 'None'
		plan_model = IPDTreatmentPlan()
		plan = IPDTreatmentPlan.objects.get(id=plan_id)
		plan.active = False
		plan_model.patient =Patient.objects.get(id=patient_id) 
		plan_model.name = name
		plan_model.start_time = datetime.now()
		plan_model.status = plan.status
		plan_model.description = description
		plan_model.active = True
		plan_model.registered_on = datetime.now()
		plan_model.prescription = plan.prescription
		plan_model.save()
		plan.save()
		messages.success(request, 'Successful!')
		return redirect('whole_ward_view')

def DeleteTreatmentPlan(request, plan_id):
	plan = IPDTreatmentPlan.objects.get(id=plan_id)
	plan.active = False
	plan.save()
	messages.success(request, 'Successfuly Deleted!')
	return redirect('whole_ward_view')

def ChangePlanStatus(request, plan_id):
	
	plan = IPDTreatmentPlan.objects.get(id=plan_id)

	"""
	action_value = int(request.POST.get('status_select')) or 'None'
	print(action_value)
	
	if action_value == 0:
		plan.status = 'Completed'
	elif action_value == 1:
		plan.status = 'Dismissed'
	"""
	"""
	if plan.status == 'Dismissed':
		plan.status='Completed'
	elif plan.status =='Completed':
		plan.status='Dismissed'
	"""
	#plan.status='Completed'
	
	#plan.end_time = datetime.now()
	perform = PerformPlan()
	perform.plan = plan
	perform.registered_on = datetime.now()
	perform.registered_by = Employee.objects.get(user_profile=request.user)
	print('change it','\n','\n')
	plan.recurrence.recurrence_threshold = plan.recurrence.recurrence_threshold + 1
	perform.save()
	plan.recurrence.save()
	messages.success(request, 'Plan Applied Successfuly!')
	return redirect('whole_ward_view')


def TreatmentPlanPrescription(request, plan_id):
	
	plan = IPDTreatmentPlan.objects.get(id=plan_id)
	plan.prescription.prescribed = True
	plan.status='Completed'
	plan.end_time = datetime.now()
	plan.save()
	messages.success(request, 'Drug Prescribed Successfuly!')
	return redirect('whole_ward_view')

def IPDStructure(request):
	building_list = HospitalUnit.objects.all()
	bed_list = Bed.objects.all()
	ward_list = Ward.objects.all()
	ward_list2 = BedCategory.objects.all()

	building_text = request.GET.get('search-building',None)
	room_text = request.GET.get('search-room',None)
	bed_text = request.GET.get('search-bed',None)
	category_text = request.GET.get('search-ward-category',None)

	active_tab = 'building_tab'

	print(building_text)
	if building_text == None:
		print('')
	else:
		building_list = building_list.filter(unit_name__icontains=building_text)
		active_tab = 'building_tab'

	if room_text == None:
		print('')
	else:
		ward_list = ward_list.filter(name__icontains=room_text)
		active_tab = 'room_tab'

	if bed_text == None:
		print('')
	else:
		bed_list = bed_list.filter(name__icontains=bed_text)
		active_tab = 'bed_tab'

	if category_text == None:
		print('isisisis')
	else:
		ward_list2 = ward_list2.filter(category__icontains=category_text)
		active_tab = 'ward_tab'

	building_form = CreateBuildingForm()
	ward_form = CreateRoomForm()
	create_ward_form = CreateWardForm()

	bed_form = CreateBedForm()
	price_form = RoomPriceForm()	
	bed_form2 = RoomFieldForm()

	ward_value_list = BedCategory.objects.all()
	if request.htmx:
		ward_id = request.GET.get('id')
		room_id = request.GET.get('ward_id')

		print('categoryID:S:S: ',ward_id, 'roomIOD:',room_id,'\n')
		if ward_id == None:
			print('None')
		else:			
			ward5 = BedCategory.objects.get(id=ward_id)
			ward_list = Ward.objects.filter(category=ward5)
		yeah = 'yeah'
		context2 = {'bed_form2':bed_form2,
					'yeah':yeah,
					'ward_list':ward_list,
		
		}
		return render(request, 'inpatient_app/partials/ward_field_div_partial.html',context2)
	print('tab:',active_tab)
	context = { 'bed_list':bed_list,
				'ward_list':ward_list,
				'ward_list2':ward_list2,
				'building_list':building_list,

				'active_tab':active_tab,

				'building_form':building_form,
				'ward_form':ward_form,
				'bed_form':bed_form,
				'bed_form2':bed_form2,

				'create_ward_form':create_ward_form,

				'price_form':price_form,
				'ward_value_list':ward_value_list,

	}
	return render(request, 'inpatient_app/ipd_structure.html', context)

def CreateWard(request):
	if request.method == 'POST':
		ward_form = CreateWardForm(request.POST)
		if ward_form.is_valid():
			ward_model = ward_form.save(commit=False)
			ward_model.registered_on = datetime.now()
			ward_model.registered_by = Employee.objects.get(user_profile=request.user)
			ward_model.active=True
			ward_model.save()
			messages.success(request, 'Successful!')
			return redirect('ipd_structure')
		else:
			messages.error(request,str(ward_form.errors))
			return redirect('ipd_structure')


def EditWard(request, ward_id):
	if request.method == 'POST':
		name = str(request.POST.get('ward_category_name')) or 'None'
		print('name: ',name)
		ward = BedCategory.objects.get(id=ward_id)
		ward.category = name
		print(ward.category)
		ward.save()
		messages.success(request, 'Successful!')
		return redirect('ipd_structure')

def DeleteWard(request, ward_id):
	ward = BedCategory.objects.get(id=building_id)
	ward.active = False
	ward.save()
	messages.success(request, 'Successfuly Deleted!')
	return redirect('ipd_structure')

def CreateIPDBuilding(request):
	if request.method == 'POST':
		building_form = CreateBuildingForm(request.POST)
		if building_form.is_valid():
			building_model = building_form.save(commit=False)
			building_model.registered_on = datetime.now()
			building_model.registered_by = Employee.objects.get(user_profile=request.user)
			building_model.active=True
			building_model.save()
			messages.success(request, 'Successful!')
			return redirect('ipd_structure')
		else:
			messages.error(request,str(building_form.errors))
			return redirect('ipd_structure')


def EditIPDBuilding(request, building_id):
	if request.method == 'POST':
		name = str(request.POST.get('unit_name')) or 'None'
		building = HospitalUnit.objects.get(id=building_id)
		building.unit_name = name
		building.save()
		messages.success(request, 'Successful!')
		return redirect('ipd_structure')

def DeleteIPDBuilding(request, building_id):
	building = HospitalUnit.objects.get(id=building_id)
	building.active = False
	building.save()
	messages.success(request, 'Successfuly Deleted!')
	return redirect('ipd_structure')

def CreateIPDWard(request):
	if request.method == 'POST':
		ward_form = CreateRoomForm(request.POST)
		if ward_form.is_valid():
			ward_model = ward_form.save(commit=False)
			ward_model.registered_on = datetime.now()
			ward_model.registered_by = Employee.objects.get(user_profile=request.user)
			ward_model.save()
			messages.success(request, 'Successful!')
			return redirect('ipd_structure')
		else:
			messages.error(request,str(ward_form.errors))
			return redirect('ipd_structure')

def EditIPDWard(request, ward_id):
	if request.method == 'POST':
		name = str(request.POST.get('ward_name')) or 'None'
		ward = Ward.objects.get(id=ward_id)
		building_id = int(request.POST.get('building')) or 'None'
		gender = str(request.POST.get('gender_select')) or 'None'
		ward.name = name
		ward.hospital_unit = HospitalUnit.objects.get(id=building_id)
		ward.by_gender = gender
		ward.save()
		messages.success(request, 'Successful!')
		return redirect('ipd_structure')


def DeleteIPDRoom(request, ward_id):
	ward = Ward.objects.get(id=ward_id)
	ward.active = False
	ward.save()
	messages.success(request, 'Successfuly Deleted!')
	return redirect('ipd_structure')

def CreateIPDBed(request):
	if request.htmx:
		ward_id = request.GET.get('ward_id')
		print('ward id',ward_id)
		room = Ward.objects.get(id=ward_id)
		bed_form = CreateBedForm(request.POST)
		price_form = RoomPriceForm(request.POST)

		if bed_form.is_valid():
			if price_form.is_valid():
				bed_model = bed_form.save(commit=False)
				price_model = price_form.save(commit=False)
				bed_model.ward = room
				bed_model.registered_on = datetime.now()
				bed_model.registered_by = Employee.objects.get(user_profile=request.user)
				price_model.room = bed_model
				price_model.active = True
				print('sss')
				#bed_model.save()
				#price_model.save()

				messages.success(request, 'Successful!')
				return redirect('ipd_structure')

			else:
				messages.error(request,str(price_form.errors))
				return redirect('ipd_structure')

		else:
			messages.error(request,str(bed_form.errors) + "d")
			return redirect('ipd_structure')

	if request.method == 'POST':
		ward_id = request.POST.get('ward_id')
		print('ward id',ward_id)

		room = Ward.objects.get(id=ward_id)
		bed_form = CreateBedForm(request.POST)
		price_form = RoomPriceForm(request.POST)

		if bed_form.is_valid():
			if price_form.is_valid():
				bed_model = bed_form.save(commit=False)
				price_model = price_form.save(commit=False)
				bed_model.ward = room
				bed_model.registered_on = datetime.now()
				bed_model.registered_by = Employee.objects.get(user_profile=request.user)
				price_model.room = bed_model
				price_model.active = True

				#bed_model.save()
				#price_model.save()

				messages.success(request, 'Successful!')
				return redirect('ipd_structure')

			else:
				messages.error(request,str(price_form.errors))
				return redirect('ipd_structure')

		else:
			messages.error(request,str(bed_form.errors) + "d")
			return redirect('ipd_structure')


def EditIPDBed(request, bed_id):
	if request.method == 'POST':
		name = str(request.POST.get('name')) or 'None'
		bed = Bed.objects.get(id=bed_id)
		ward_id = int(request.POST.get('ward')) or 'None'
		bed.name = name
		bed.ward = Ward.objects.get(id=ward_id)
		bed.save()
		messages.success(request, 'Successful!')
		return redirect('ipd_structure')

def DeleteIPDBed(request, bed_id):
	bed = Bed.objects.get(id=bed_id)
	bed.active = False
	bed_price = RoomPrice.objects.get(room=bed,active=True)
	bed_price.active = False
	bed_price.save()
	bed.save()
	messages.success(request, 'Successfuly Deleted!')
	return redirect('ipd_structure')

def AllocatedPatientList(request):
	beds = Bed.objects.filter(patient__isnull=False)
	context = { 'beds':beds}
	return render(request, 'inpatient_app/allocated_patient_list.html', context)


def PatientListForNurse(request):
	print(request.user)
#	service_team = ServiceTeam.objects.get(service_provider__user_profile=request.user)
	ward_team_bed = WardTeamBed.objects.filter(nurse_team__nurse__user_profile=request.user, bed__patient__isnull=False)
	if not ward_team_bed :
		service_provider_bed = ServiceProviderBed.objects.filter(service_provider__user_profile=request.user, bed__patient__isnull=False)
		if not service_provider_bed:
			print('Its NONE!')
			context = {'ward_team_bed':ward_team_bed}
			return render(request,'inpatient_app/patient_list_for_nurse.html',context)

		else:
			print('its not NONE')
			for s in service_provider_bed:
				print('\n',s.bed.patient,'\n')
			context = {'ward_team_bed':service_provider_bed}
			return render(request,'inpatient_app/patient_list_for_nurse.html',context)
		#print('Its None!')
	else:
		service_provider_bed = ServiceProviderBed.objects.filter(service_provider__user_profile=request.user, bed__patient__isnull=False)
		if not service_provider_bed:
			print('Its NONE22!')
			context = {'ward_team_bed':ward_team_bed}
			return render(request,'inpatient_app/patient_list_for_nurse.html',context)

		else:
			print('its not NONE22')
			for s in service_provider_bed:
				print('\n',s.bed.patient,'\n')
			context = {'ward_team_bed':ward_team_bed, 'service_provider_bed':service_provider_bed}
			return render(request,'inpatient_app/patient_list_for_nurse.html',context)
#		print('Not None!')
	"""
	for w in ward_team_bed:
		print('\n','hererererererere' ,w, '\n')
	context = {'ward_team_bed':ward_team_bed}
	return render(request,'inpatient_app/patient_list_for_nurse.html',context)
	"""
def PatientListForDoctor(request):
	print(request.user)
#	service_team = ServiceTeam.objects.get(service_provider__user_profile=request.user)
	ward_team_bed = WardTeamBed.objects.filter(team__ward_service_provider__user_profile=request.user, bed__patient__isnull=False)
	for w in ward_team_bed:
		print('\n',w,'\n')
	context = {'ward_team_bed':ward_team_bed}
	return render(request,'inpatient_app/patient_list_for_doctor.html',context)


	"""
	form = OrganismForm()
	form.fields['organism'].choices = list()

	# Now loop the kingdoms, to get all organisms in each.
	for k in Kingdom.objects.all():
	    # Append the tuple of OptGroup Name, Organism.
	    form.fields['organism'].choices = form.fields['organism'].choices.append(
	        (
	            k.name, # First tuple part is the optgroup name/label
	            list( # Second tuple part is a list of tuples for each option.
	                (o.id, o.name) for o in Organism.objects.filter(kingdom=k).order_by('name')
	                # Each option itself is a tuple of id and name for the label.
	            )
	        )
	    )

	
	bed_form = BedForm()
	bed_form.fields['bed'].choices = list()


	for category in BedCategory.objects.all():
		bed_form.fields['bed'].choices = bed_form.fields['bed'].choices.append(
			(
				category.category,
				list(
					(bed.bed_number) for bed in Bed.objects.filter(category=category)#.order_by('category')
					)
			)		
			)
	"""

def AllocatePatient(request,pk):
	patient = Patient.objects.get(id=pk)
	filtered_category = int(request.GET.get('category','0')) or 'None'
	if filtered_category=='None':	
		unallocated_beds = Bed.objects.filter(patient__isnull=True).order_by('category')
	else:
		unallocated_beds = Bed.objects.filter(patient__isnull=True, category=BedCategory.objects.get(id=filtered_category))

	for b in unallocated_beds:
		print(b)
	bed_form = BedForm()

	bed_form.fields['bed'].queryset = unallocated_beds
	bed_release_date = BedReleaseDate.objects.filter(status='active')
	category_list = BedCategory.objects.all()
	if request.method == 'POST':
		bed_form = BedForm(request.POST)
		if bed_form.is_valid():
			bed_allocation_model = bed_form.save(commit=False)
			bed_model = Bed.objects.get(id = bed_allocation_model.bed.id)
			bed_allocation_model.patient = patient
			bed_allocation_model.save()
			bed_model.patient = patient
			bed_model.save()
#			patient.status = 'Undergoing Treatment'
			room_bill = InpatientRoomBillDetail.objects.get(patient=patient, active='active')
			room_bill.room =  bed_model
			stay_duration = PatientStayDuration.objects.get(patient = patient,leave_date__isnull=True)
			stay_duration.room = bed_model

			bed_release_date_model = BedReleaseDate()
			bed_release_date_model.bed = bed_model
			duration_prediction = PatientStayDurationPrediction.objects.get(patient=patient, status='active')
			bed_release_date_model.bed_release_date = datetime.now() + timedelta(duration_prediction.duration)
#			new_date = datetime.today() + timedelta(12)
			bed_release_date_model.status = 'active'
			
			bed_release_date_model.save()
			stay_duration.save()
			room_bill.save()
			messages.success(request,'Successfuly Allocated!')
			return redirect('patient_list')
		else:
			messages.error(request,'Fill Form!')


	context = {'bed_form':bed_form, 'unallocated_beds':unallocated_beds,
				'bed_release_date':bed_release_date,
				'category_list':category_list,

			}
	return render(request,'inpatient_app/allocate_patient.html',context)

def WardTeamList(request):
	"""
	beds = Bed.objects.all()
	for bed in beds:
		room_price = RoomPrice()
		room_price.room = bed
		room_price.room_price = 100
		room_price.save()
	"""


	"""
	ward_nurse_team = WardNurseTeam.objects.all()
	ward_doctor_team = WardTeam.objects.all()
	for team in ward_nurse_team:
		nurse_array = []	
		nurse_list = 
		nurse_array.append(team.nurse)
	"""
	trial_string = 'Some Notification! '
	notify(request.user,'info', ' Trial notification ', trial_string,link='/patient_list_for_doctor')
#	zero = 0
	ward_team = InpatientTeam.objects.all()
	nurse_count_array = []
	doctor_count_array = []
	doctor_team_array = []
	for team in ward_team:
		nurse_list_array = []
		nurse_list = WardNurseTeam.objects.filter(team=team)
		doctor_list_array = []
		doctor_list = WardTeam.objects.filter(team=team)
		for nurse in nurse_list:
			nurse_list_array.append(nurse.nurse)
		for doctor in doctor_list:
			doctor_list_array.append(doctor.ward_service_provider)
			print('\n',doctor.ward_service_provider," : " , len(doctor_list_array),'\n')
		if doctor_list:
			doctor_team_array.append(team)
			if len(doctor_list_array) > 0:
				doctor_count_array.append(len(doctor_list_array))
			else:
				doctor_count_array.append(0)
	doctor_team_zip = zip(doctor_team_array, doctor_count_array)
	doctor_team_zip2 = zip(doctor_team_array, doctor_count_array)


#	if nurse_count_array > 0:
	nurse_team_zip = zip(nurse_list, nurse_count_array)
#	for n,c in nurse_team_zip:
#		print('\n',n,c,'\n')
#	if doctor_count_array > 0:

	
#	for n,c in doctor_team_zip:
#		print('\n',n,c,'\n')
	
#	team_zip = zip()
	allocated_bed_id = []
	doctor_allocated_bed_id = []
	allocated_beds = WardTeamBed.objects.filter(nurse_team__isnull=False, bed__isnull=False)
	doctor_allocated_beds = WardTeamBed.objects.filter(team__isnull=False, bed__isnull=False)

	for bed in allocated_beds:
		allocated_bed_id.append(bed.bed.id)
	for bed in doctor_allocated_beds:
		doctor_allocated_bed_id.append(bed.bed.id)

	unallocated_beds = Bed.objects.exclude(id__in=allocated_bed_id)
	unallocated_beds_for_doctor = Bed.objects.exclude(id__in=doctor_allocated_bed_id)

#	for b in unallocated_beds:
#		print(b)
	assign_form = AssignNurseToBedForm()
	doctor_assign_form = AssignNurseToBedForm()
	doctor_assign_form.fields['bed'].queryset = unallocated_beds_for_doctor

	doctor_team_form = CreateDoctorTeamForm()
	assign_doctor_to_team_form = AssignDoctorToTeamForm()
	assign_form.fields['bed'].queryset = unallocated_beds

	doctor_team_list = WardTeam.objects.all()
	
	assign_form = AssignDoctorToTeamForm()
	assigned_doctors_array = []
	team_list = WardTeam.objects.filter(ward_service_provider__isnull=False)
	for team in team_list:
		assigned_doctors_array.append(team.ward_service_provider.id)
	unassigned_doctors = Employee.objects.filter(designation__name='Doctor').exclude(id__in=assigned_doctors_array)
	assign_form.fields['ward_service_provider'].queryset = unassigned_doctors
	
	context = {'nurse_team_zip':nurse_team_zip,
				'doctor_team_zip':doctor_team_zip,
				'doctor_team_zip2':doctor_team_zip2,

				'assign_form':assign_form,
				'doctor_assign_form':doctor_assign_form,
				'doctor_team_form':doctor_team_form,
				'assign_doctor_to_team_form':assign_doctor_to_team_form,
				}
	return render(request,'inpatient_app/ward_team_list.html',context)

def NurseTeamList(request):

	ward_team = InpatientTeam.objects.all()
	nurse_count_array = []
	nurse_team_array = []
	for team in ward_team:
		nurse_list_array = []
		nurse_list = WardNurseTeam.objects.filter(team=team)
		for nurse in nurse_list:
			nurse_list_array.append(nurse.nurse)
		if nurse_list:
			nurse_team_array.append(team)
			if len(nurse_list_array) > 0:
				nurse_count_array.append(len(nurse_list_array))
			else:
				nurse_count_array.append(0)
	nurse_team_zip = zip(nurse_team_array, nurse_count_array)
	nurse_team_zip2 = zip(nurse_team_array, nurse_count_array)


	allocated_bed_id = []
	allocated_beds = WardTeamBed.objects.filter(nurse_team__isnull=False, bed__isnull=False)

	for bed in allocated_beds:
		allocated_bed_id.append(bed.bed.id)

	unallocated_beds = Bed.objects.exclude(id__in=allocated_bed_id)

#	for b in unallocated_beds:
#		print(b)
	assign_form = AssignNurseToBedForm()
	team_assign_form = AssignNurseToTeamForm()

	assigned_nurses_array = []
	team_list = WardNurseTeam.objects.filter(nurse__isnull=False)
	for team in team_list:
		assigned_nurses_array.append(team.nurse.id)
	unassigned_nurses = Employee.objects.filter(designation__name='Nurse').exclude(id__in=assigned_nurses_array)
	team_assign_form.fields['nurse'].queryset = unassigned_nurses

	doctor_team_form = CreateDoctorTeamForm()
	
	assign_form.fields['bed'].queryset = unallocated_beds
	try:
		setting = TeamSetting.objects.get(active=True)		
	except :
		setting = None
	context = {'nurse_team_zip':nurse_team_zip,
				'nurse_team_zip2':nurse_team_zip2,
				'assign_form':assign_form,
				'doctor_team_form':doctor_team_form,
				'team_assign_form':team_assign_form,
				'setting':setting,
				}
	return render(request,'inpatient_app/nurse_team_list.html',context)

def CreateInpatientTeamFormPage(request):
	if request.method == 'POST':
		team_form = CreateDoctorTeamForm(request.POST)
		if team_form.is_valid():
			team_model = team_form.save()			
			messages.success(request, 'Successful!')
			return redirect('assign_doctor_to_team_form', team_model.id)
		else:
			messages.error(request, assign_form.errors)
			return redirect('ward_team_list')
			
def CreateNurseTeamFormPage(request):
	if request.method == 'POST':
		team_form = CreateDoctorTeamForm(request.POST)
		if team_form.is_valid():
			team_model = team_form.save()			
			messages.success(request, 'Successful!')
			return redirect('schedule_nurse', team_model.id)
		else:
			messages.error(request, assign_form.errors)
			return redirect('nurse_team_list')

def AssignDoctorToTeamFormPage(request,team_id):


	assign_form = AssignDoctorToTeamForm()
	assigned_doctors_array = []
	team_list = WardTeam.objects.filter(ward_service_provider__isnull=False)
	for team in team_list:
		assigned_doctors_array.append(team.ward_service_provider.id)
	unassigned_doctors = Employee.objects.filter(designation__name='Doctor').exclude(id__in=assigned_doctors_array)
	assign_form.fields['ward_service_provider'].queryset = unassigned_doctors

	team = InpatientTeam.objects.get(id=team_id)
	if request.method == 'POST':
		assign_form = AssignDoctorToTeamForm(request.POST)
		if assign_form.is_valid():
			doctor_team_model = assign_form.save(commit=False)
			doctor_team_model.team = team
			doctor_team_model.save()
			messages.success(request, 'Success!')
			return redirect('assign_doctor_to_team_form',team.id)
		else:
			messages.error(request, str(assign_form.errors))
	context = {'assign_form':assign_form,

	}
	return render(request,'inpatient_app/assign_doctor_to_team_form.html',context)

def AssignDoctorToTeamModal(request,team_id):


	team = InpatientTeam.objects.get(id=team_id)
	if request.method == 'POST':
		assign_form = AssignDoctorToTeamForm(request.POST)
		if assign_form.is_valid():
			doctor_team_model = assign_form.save(commit=False)
			doctor_team_model.team = team
			doctor_team_model.save()
			messages.success(request, 'Success!')
			return redirect('ward_team_list')
		else:
			messages.error(request, str(assign_form.errors))
			return redirect('ward_team_list')
	else:
		messages.error(request, "Not POST")
		return redirect('ward_team_list')


def AssignNurseToTeamModal(request,team_id):

	team = InpatientTeam.objects.get(id=team_id)
	if request.method == 'POST':
		assign_form = AssignNurseToTeamForm(request.POST)
		if assign_form.is_valid():
			nurse_team_model = assign_form.save(commit=False)
			nurse_team_model.team = team
			nurse_team_model.save()
			messages.success(request, 'Success!')
			return redirect('nurse_team_list')
		else:
			messages.error(request, str(assign_form.errors))
			return redirect('nurse_team_list')
	else:
		messages.error(request, "Not POST")
		return redirect('nurse_team_list')


	"""
	return render(self.request, 'schedule.html', {
		'events': str(events),
		'filter_form': filter_form,
		'initial_date': str(today),
	})
	"""
def AssignNurseToTeamFormPage(request,team_id):
	assign_form = AssignNurseToTeamForm()

	assigned_nurses_array = []
	team_list = WardNurseTeam.objects.filter(nurse__isnull=False)
	for team in team_list:
		assigned_nurses_array.append(team.nurse.id)
	unassigned_nurses = Employee.objects.filter(designation__name='Nurse').exclude(id__in=assigned_nurses_array)
	assign_form.fields['nurse'].queryset = unassigned_nurses

	team = InpatientTeam.objects.get(id=team_id)
	if request.method == 'POST':
		assign_form = AssignNurseToTeamForm(request.POST)
		if assign_form.is_valid():
			nurse_team_model = assign_form.save(commit=False)
			nurse_team_model.team = team
			nurse_team_model.save()
			messages.success(request, 'Success!')
			return redirect('assign_nurse_to_team_form',team.id)
		else:
			messages.error(request, str(assign_form.errors))
	context = {'assign_form':assign_form}
	return render(request,'inpatient_app/assign_nurse_to_team_form.html',context)

class ScheduleNurse(View):

	def get(self, *args, **kwargs):
		assign_form = AssignNurseToTeamForm()

		assigned_nurses_array = []
		team_list = WardNurseTeam.objects.filter(nurse__isnull=False)
		for team in team_list:
			assigned_nurses_array.append(team.nurse.id)
		unassigned_nurses = Employee.objects.filter(designation__name='Nurse').exclude(id__in=assigned_nurses_array)
		assign_form.fields['nurse'].queryset = unassigned_nurses
		team_id = kwargs['team_id']
		team = InpatientTeam.objects.get(id=team_id)

		filter_form = FilterScheduleForm(self.request.GET)
		today = timezone.now().date()
		shift_type = None
		events = []
		dept_id = int(self.request.GET.get('department', 0) or 0)
		try:
			if dept_id:
				department = Department.objects.get(id=dept_id)
				shift_type = ShiftType.objects.get(department=department)
		except: pass
		month = int(self.request.GET.get('month', 0))
		if month and month > 0 and month <= 12:
			 today = datetime.date(today.year, int(month), 1) # construct date with the new month
		shifts = WorkShift.objects.all()
		if shift_type:
			shifts = shifts.filter(shift_type=shift_type)
		for i in range(40):
			d = today + timedelta(days=i)
			day_shifts:Sequence[WorkShift] = shifts.filter(day=d.weekday())
			for shift in day_shifts:
				shift_workers = shift.employee_set.all()
				for e in shift_workers:
					color = generate_random_color()
					if StaffLeave.check_leave(e, d):
						color = 'red'
						events.append({
							'title': e.full_name,
							'url': reverse('staff:view_employee', args=[e.id]),
							'start': str(d),
							'end': str(d + timedelta(days=1)),
							'backgroundColor': color,
						})
						events.append({
							'title': "On leave",
							'start': str(d),
							'end': str(d + timedelta(days=1)),
							'backgroundColor': color,
						})
						continue
					events.append({
						'title': e.full_name,
						'url': reverse('staff:view_employee', args=[e.id]),
						'start': str(d),
						'end': str(d + timedelta(days=1)),
						'backgroundColor': color,
						'groupId': f'{e.id}'
					})
					events.append({
						'title': f'{shift.start_time}-{shift.end_time}',
						'start': str(d),
						'end': str(d + timedelta(days=1)),
						'backgroundColor': color,
						'groupId': f'{shift.id}'
					})
		return render(self.request, 'inpatient_app/schedule_nurse.html', {
			'events': str(events),
			'filter_form': filter_form,
			'initial_date': str(today),
			'assign_form':assign_form,
			'team_id':team.id,
		})

	def post(self, *args, **kwargs):
		team_id = kwargs['team_id']
		team = InpatientTeam.objects.get(id=team_id)
		assign_form = AssignNurseToTeamForm(POST)
		if assign_form.is_valid():
			nurse_team_model = assign_form.save(commit=False)
			nurse_team_model.team = team
			nurse_team_model.save()
			messages.success(request, 'Success!')
			return redirect('schedule_nurse',team.id)
		else:
			messages.error(request, str(assign_form.errors))
			return redirect('schedule_nurse')

def AssignNurseTeamToBedFormPage(request,inpatient_team_id):
	inpatient_team = InpatientTeam.objects.get(id=inpatient_team_id)
	nurse_team_list = WardNurseTeam.objects.filter(team=inpatient_team)
	if request.method == 'POST':
		assign_form = AssignNurseToBedForm(request.POST)
		if assign_form.is_valid():
			ward_team_bed_model = assign_form.save(commit=False)
			"""
			try:
				nurse_assigned_bed = WardTeamBed.objects.get(bed= ward_team_bed_model.bed, nurse_team__isnull=False)
				for team in doctor_team_list:
					nurse_assigned_bed.team = team
					nurse_assigned_bed.save()
				messages.success(request,'Successfuly Assigned!')
			except:
			"""
			for team in nurse_team_list:
				new_ward_bed_model = WardTeamBed()
				new_ward_bed_model.nurse_team = team
				new_ward_bed_model.bed = ward_team_bed_model.bed
				new_ward_bed_model.save()
			messages.success(request,'Nurse Successfuly Assigned!')
			return redirect('nurse_team_list')
		else:
			messages.error(request, str(assign_form.error))
			return redirect('nurse_team_list')
	

def AssignNurseToBedFormPage(request,employee_id):
	
	nurse = Employee.objects.get(id=employee_id)
	if request.method == 'POST':
		assign_form = AllocateNurseToBedForm(request.POST)
		if assign_form.is_valid():
			service_provider_bed_model = assign_form.save(commit=False)
			service_provider_bed_model.service_provider = nurse
			service_provider_bed_model.save()
			messages.success(request, 'Successful!')
			return redirect('nurse_list')
		else:
			messages.error(request, assign_form.errors)
			return redirect('nurse_list')

def AssignDoctorToBedFormPage2(request,employee_id):
	
	doctor = Employee.objects.get(id=employee_id)
	if request.method == 'POST':
		assign_form = AllocateNurseToBedForm(request.POST)
		if assign_form.is_valid():
			service_provider_bed_model = assign_form.save(commit=False)
			service_provider_bed_model.service_provider = doctor
			service_provider_bed_model.save()
			messages.success(request, 'Successful!')
			return redirect('doctor_list')
		else:
			messages.error(request, assign_form.errors)
			return redirect('doctor_list')

def BedReleaseDateFormPage(request,bed_id):
	
	bed = Bed.objects.get(id=bed_id)
	bed_release_form = BedReleaseDateForm()
	if request.method == 'POST':
		bed_release_form = BedReleaseDateForm(request.POST)
		if bed_release_form.is_valid():
			bed_release_model = bed_release_form.save(commit=False)
			bed_release_model.bed = bed
			bed_release_model.status = 'active'
			bed_release_model.save()
			return redirect('patient_list')
	context = {'bed_release_form':bed_release_form,
				}
	return render(request,'inpatient_app/bed_release_date_form.html',context)

def NurseList(request):
	bed_release_form = BedReleaseDateForm()

	nurse_list = Employee.objects.filter(designation__name='Nurse')
#	nurse = Employee.objects.get(id=employee_id)
	bed_count_array = []
	bed_array = []
	nurse_array = []
#	for ward in WardTeamBed.objects.all():
	for nurse in nurse_list:
		team_bed_count = WardTeamBed.objects.filter(nurse_team__nurse = nurse).count()
		individual_bed_count = ServiceProviderBed.objects.filter(service_provider=nurse).count()
		print('Nurse: ', nurse, ' ', 'Bed count: ', team_bed_count)
		#print('Nurse: ',nurse,' bed count: ', bed_count,'\n')
		bed_count_array.append(team_bed_count + individual_bed_count)
		nurse_array.append(nurse)
		for ward in WardTeamBed.objects.filter(nurse_team__nurse = nurse):
			bed_array.append(ward.bed)

	nurse_zip = zip(nurse_list, bed_count_array)
	nurse_zip2 = zip(nurse_list, bed_count_array)

	nurse_bed_zip = list(zip(nurse_array, bed_array))
	try_zip = itertools.zip_longest(nurse_list, bed_array)

	allocated_bed_id = []
	for provider_bed in ServiceProviderBed.objects.all():
		allocated_bed_id.append(provider_bed.bed.id)
	unallocated_beds = Bed.objects.exclude(id__in=allocated_bed_id)

	assign_nurse_form = AllocateNurseToBedForm()
	assign_nurse_form.fields['bed'].queryset = unallocated_beds
	try:
		setting = TeamSetting.objects.get(active=True)		
	except :
		setting = None

	context = {'nurse_zip':nurse_zip,
				'nurse_zip2':nurse_zip2,
				'assign_nurse_form':assign_nurse_form,
				'nurse_bed_zip':nurse_bed_zip,
				'bed_release_form':bed_release_form,
				'nurse_list':nurse_list,
				'setting':setting,
				}
	return render(request,'inpatient_app/nurse_list.html',context)

def DoctorList(request):

	doctor_list = Employee.objects.filter(designation__name='Doctor')

	bed_count_array = []
	bed_array = []
	doctor_array = []

	for doctor in doctor_list:
		team_bed_count = WardTeamBed.objects.filter(team__ward_service_provider = doctor).count()
		individual_bed_count = ServiceProviderBed.objects.filter(service_provider=doctor).count()
		print('Nurse: ', doctor, ' ', 'Bed count: ', team_bed_count)
		#print('Nurse: ',nurse,' bed count: ', bed_count,'\n')
		bed_count_array.append(team_bed_count + individual_bed_count)
		doctor_array.append(doctor)
		for ward in WardTeamBed.objects.filter(team__ward_service_provider = doctor):
			bed_array.append(ward.bed)

	doctor_zip = zip(doctor_list, bed_count_array)
	doctor_zip2 = zip(doctor_list, bed_count_array)

#	nurse_bed_zip = list(zip(nurse_array, bed_array))
#	try_zip = itertools.zip_longest(nurse_list, bed_array)

	allocated_bed_id = []
	for provider_bed in ServiceProviderBed.objects.all():
		allocated_bed_id.append(provider_bed.bed.id)
	unallocated_beds = Bed.objects.exclude(id__in=allocated_bed_id)

	assign_nurse_form = AllocateNurseToBedForm()
	assign_nurse_form.fields['bed'].queryset = unallocated_beds
	context = {'doctor_zip':doctor_zip,
				'doctor_zip2':doctor_zip2,
				'assign_nurse_form':assign_nurse_form,
				'doctor_list':doctor_list,
				}
	return render(request,'inpatient_app/doctor_list.html',context)

def AssignDoctorToBedFormPage(request,inpatient_team_id):
	
	inpatient_team = InpatientTeam.objects.get(id=inpatient_team_id)
	doctor_team_list = WardTeam.objects.filter(team=inpatient_team)
	if request.method == 'POST':
		assign_form = AssignNurseToBedForm(request.POST)
		if assign_form.is_valid():
			ward_team_bed_model = assign_form.save(commit=False)
			"""
			try:
				nurse_assigned_bed = WardTeamBed.objects.get(bed= ward_team_bed_model.bed, nurse_team__isnull=False)
				for team in doctor_team_list:
					nurse_assigned_bed.team = team
					nurse_assigned_bed.save()
				messages.success(request,'Successfuly Assigned!')
			except:
			"""
			for team in doctor_team_list:
				new_ward_bed_model = WardTeamBed()
				new_ward_bed_model.team = team
				new_ward_bed_model.bed = ward_team_bed_model.bed
				new_ward_bed_model.save()
			messages.success(request,'Doctor Successfuly Assigned!')
			return redirect('ward_team_list')
		else:
			messages.error(request, str(assign_form.error))
			return redirect('ward_team_list')

def UnallocatedPatient(request):
#	patient_list = Patient.objects.filter(status="Undergoing Treatment")
	patient_list = Patient.objects.exclude(ward=None)

	for p in patient_list:
		print(p)
	bed_array = []
	for patient in patient_list:
		try:
			bed = Bed.objects.get(patient=patient)
		except:
			bed = None
		bed_array.append(bed)
#	bed = Bed.objects.filter(patient__isnull=False)
	patient_zip = zip(patient_list, bed_array)
	context = {'patient_zip':patient_zip}
	return render(request,'inpatient_app/unallocated_patient.html',context)

def AllocateNurse(request):
	patient = Patient.objects.all()
	for p in patient:
		print('\n', p.treatment_status)
	nurse_patient_form = NursePatientForm()
	if request.method == 'POST':
		nurse_patient_form = NursePatientForm(request.POST)
		if nurse_patient_form.is_valid():
			nurse_patient_model = nurse_patient_form.save(commit=False)
			nurse_patient_model.save()
			messages.success(request,'Successfuly Allocated')
		else:
			print(nurse_patient_form.error)
	context = {'nurse_patient_form':nurse_patient_form}
	return render(request,'inpatient_app/allocate_nurse.html',context)


def AssignInpatient(request):
	assign_form = AssignInpatientForm()
	patient_form = PatientForm()
	if request.method == 'POST':
		assign_form = AssignInpatientForm(request.POST)
		patient_form = PatientForm(request.POST)
		if all([assign_form.is_valid(), patient_form.is_valid()]):
			assign_form_result = assign_form.save(commit=False)
			patient_model = patient_form.save(commit=False)
			if assign_form_result.treatment_status == 'Drug administration':
				patient = Patient.objects.get(id=patient_model.patient.id)
				patient.treatment_status = 'Drug administration'
				patient.save()
				print('1    ','\n', patient.treatment_status)
				return redirect('inpatient_prescription', pk= patient.id)
			else:
				patient = Patient.objects.get(id=patient_model.patient.id)
				patient.treatment_status = 'Surgery'
				patient.save()
				print('2    ','\n', patient.treatment_status)
				#return redirect('')
				messages.success(request,'Successfuly Assigned!')
	context = {'assign_form':assign_form,'patient_form':patient_form}
	return render(request,'inpatient_app/assign_inpatient.html',context)

def InpatientPrescription(request,patient_id):
	patient = Patient.objects.get(id=patient_id)
	stay_duration = PatientStayDuration.objects.filter(patient=patient, leave_date__isnull=True).last()
	prescription_form = InpatientPrescriptionForm()
	if request.method == 'POST':
		prescription_form = InpatientPrescriptionForm(request.POST)
		info_form = PrescriptionInfoForm(request.POST)
		if prescription_form.is_valid():
			prescription_model = prescription_form.save(commit=False)
			prescription_model.patient = Patient.objects.get(id=patient_id)
			prescription_model.department = 1
			true_string = 'true'
			prescription_model.dispensed = true_string
			prescription_model.registered_on = datetime.now()


			"""			
			drug_bill = InpatientDrugBillDetail()
			last_bill = InpatientBill.objects.last()
			#drug_bill.bill = InpatientBill()
#			drug_bill.bill.bill_no = last_bill.bill_no + 1

			inpatient_bill = InpatientBillRelation.objects.get(patient=prescription_model.patient, is_active='active')
			drug_bill.bill = inpatient_bill.bill
			drug_bill.drug = prescription_model.drug
			drug_bill.patient = prescription_model.patient
			drug_price = DrugPrice.objects.get(drug=prescription_model.drug, active='active')
			drug_bill.registered_on = datetime.now()
			
			da = prescription_model.duration_amount
			fq = int(prescription_model.frequency)
			drug_bill.quantity = da * fq * 30 
			drug_bill.quantity = drug_bill.quantity / int(prescription_model.drug.unit)
			drug_bill.drug_price = drug_price.selling_price * drug_bill.quantity
			"""
			inpatient_medication = InpatientMedication()
			inpatient_medication.patient = prescription_model.patient
			inpatient_medication.stay_duration = stay_duration
			inpatient_medication.drug_prescription = prescription_model
			inpatient_medication.registered_on = datetime.now()
			inpatient_medication.doctor = Employee.objects.get(user_profile=request.user, designation__name='Doctor')
			inpatient_medication.diagnosis = prescription_model.diagnosis

#			drug_bill.bill.save()
			
			prescription_model.save()
			inpatient_medication.save()
#			drug_bill.save()
			messages.success(request, 'Successfuly Prescribed!')
			return redirect('inpatient_prescription_list')
	context = {'prescription_form':prescription_form}
	return render(request,'inpatient_app/inpatient_prescription.html',context)

def GiveInpatientService(request, patient_id):
	patient = Patient.objects.get(id=patient_id)
	service_form = InpatientServiceForm()
	if request.method == 'POST':
		service_form = InpatientServiceForm(request.POST)
		if service_form.is_valid():
			service_bill = service_form.save(commit=False)
			inpatient_bill = InpatientBillRelation.objects.get(patient=patient, is_active='active')

			service_bill.bill = inpatient_bill.bill
			service_bill.service_price = service_bill.service.service_price
			service_bill.patient = patient
			service_bill.registered_on = datetime.now()
			service_bill.save()
			messages.success(request, 'Successful!')
	context = {'service_form':service_form}
	return render(request,'inpatient_app/give_inpatient_service.html',context)


def InpatientAssignment(request, patient_id):
	patient = Patient.objects.get(id=patient_id)
	patient.inpatient = 'yes'
	
	patient_bill = InpatientBillRelation()
	patient_bill.bill = InpatientBill()
	patient_bill.patient = patient
	patient_bill.is_active = 'active'

	stay_duration = PatientStayDuration()
	stay_duration.patient = patient
	stay_duration.admission_date = datetime.now()
	stay_duration.bill = patient_bill.bill

	room_bill = InpatientRoomBillDetail()
	room_bill.bill = patient_bill.bill
	room_bill.patient = patient
	room_bill.active = 'active'

	patient_visit = PatientVisit.objects.filter(patient=patient, visit_status='Active', payment_status='paid')
	for visit in patient_visit:
		visit.visit_status = 'Ended'
		visit.save()
#	patient_visit.visit_status = 'Ended'

#	patient_visit.save()
	patient.save()
	patient_bill.bill.save()
	patient_bill.save()
	stay_duration.save()
	room_bill.save()
	messages.success(request, 'Successful!')
	return redirect('patient_list')


def InpatientAssignmentFromEmergency(request, patient_id):
	patient = Patient.objects.get(id=patient_id)
	patient.inpatient = 'yes'
	
	patient_bill = InpatientBillRelation()
	patient_bill.bill = InpatientBill()
	patient_bill.patient = patient
	patient_bill.is_active = 'active'

	stay_duration = PatientStayDuration()
	stay_duration.patient = patient
	stay_duration.admission_date = datetime.now()
	stay_duration.bill = patient_bill.bill

	room_bill = InpatientRoomBillDetail()
	room_bill.bill = patient_bill.bill
	room_bill.patient = patient
	room_bill.active = 'active'

	admission_assessment = InpatientAdmissionAssessment()
	admission_assessment.patient = patient
	admission_assessment.admitted_from = 'Emergency Department'
	admission_assessment.status = 'active'

	"""
	patient_visit = PatientVisit.objects.get(patient=patient, visit_status='Active', payment_status='paid')
	patient_visit.visit_status = 'Ended'

	patient_visit.save()
	"""
	patient.save()
	admission_assessment.save()
	patient_bill.bill.save()
	patient_bill.save()
	stay_duration.save()
	room_bill.save()
	messages.success(request, 'Successful!')
	return redirect('inpatient_reason_form', patient.id)


def InpatientReasonFormPage(request, patient_id):
	patient = Patient.objects.get(id=patient_id)
	inpatient_reason_form = InpatientReasonForm()
	inpatient_care_plan_form = InpatientCarePlanForm()
	prediction_form = StayDurationPredictionForm()
	priority_form = WardAdmissionPriorityForm()
	assessment_form = InpatientAssessmentForm()

	if request.method == 'POST':
		inpatient_reason_form = InpatientReasonForm(request.POST)
		inpatient_care_plan_form = InpatientCarePlanForm(request.POST)
		prediction_form = StayDurationPredictionForm(request.POST)
		priority_form = WardAdmissionPriorityForm(request.POST)
		assessment_form = InpatientAssessmentForm(request.POST)

		if inpatient_reason_form.is_valid():
			inpatient_reason_model = inpatient_reason_form.save(commit=False)
			inpatient_care_plan_model = inpatient_care_plan_form.save(commit=False)
			prediction_model = prediction_form.save(commit=False)
			priority_model = priority_form.save(commit=False)
			assessment_model = assessment_form.save(commit=False)

			employee = Employee.objects.get(user_profile=request.user, designation__name='Doctor')
			inpatient_reason_model.service_provider = employee
			inpatient_reason_model.status = 'active'
			inpatient_reason_model.patient = patient

			inpatient_care_plan_model.service_provider = employee
			inpatient_care_plan_model.status = 'active'
			inpatient_care_plan_model.patient = patient
			
			prediction_model.patient = patient
			prediction_model.status = 'active'

			priority_model.patient = patient
			priority_model.status = 'active'

			try:
				emergency_assessment_model = InpatientAdmissionAssessment.objects.get(patient=patient,status='active', admitted_from='Emergency Department')
				employee = Employee.objects.get(user_profile=request.user, designation__name='Doctor')
				emergency_assessment_model.service_provider = employee
				emergency_assessment_model.status = 'active'
				emergency_assessment_model.patient = patient
				emergency_assessment_model.general_appearance = assessment_model.general_appearance
				emergency_assessment_model.other_assessment = assessment_model.other_assessment
				emergency_assessment_model.save()
				messages.success(request, 'Successful!')
				return redirect('patient_list')

			except:
				employee = Employee.objects.get(user_profile=request.user, designation__name='Doctor')
				assessment_model.service_provider = employee
				assessment_model.status = 'active'
				assessment_model.patient = patient

				assessment_model.save()
				messages.success(request, 'Successful!')

			priority_model.save()
			prediction_model.save()
			inpatient_care_plan_model.save()
			inpatient_reason_model.save()
			messages.success(request, 'Successful!')
			return redirect('inpatient_assignment', patient.id)
			
	context = {'inpatient_reason_form':inpatient_reason_form, 'patient':patient,
				'inpatient_care_plan_form':inpatient_care_plan_form,
				'priority_form':priority_form,
				'prediction_form':prediction_form,
				'assessment_form':assessment_form,
				}
	return render(request,'inpatient_app/inpatient_reason_form.html',context)

def InpatientAdmissionAssessmentFormPage(request, patient_id):
	patient = Patient.objects.get(id=patient_id)
	assessment_form = InpatientAssessmentForm()
	
	if request.method == 'POST':
		assessment_form = InpatientAssessmentForm(request.POST)
		if assessment_form.is_valid():
			assessment_model = assessment_form.save(commit=False)
			try:
				emergency_assessment_model = InpatientAdmissionAssessment.objects.get(patient=patient,status='active', admitted_from='Emergency Department')
				employee = Employee.objects.get(user_profile=request.user, designation__name='Doctor')
				emergency_assessment_model.service_provider = employee
				emergency_assessment_model.status = 'active'
				emergency_assessment_model.patient = patient
				emergency_assessment_model.general_appearance = assessment_model.general_appearance
				emergency_assessment_model.other_assessment = assessment_model.other_assessment
				emergency_assessment_model.save()
				messages.success(request, 'Successful!')
				return redirect('patient_list')

			except:
				employee = Employee.objects.get(user_profile=request.user, designation__name='Doctor')
				assessment_model.service_provider = employee
				assessment_model.status = 'active'
				assessment_model.patient = patient

				assessment_model.save()
				messages.success(request, 'Successful!')
				return redirect('patient_list')
			
	context = {'assessment_form':assessment_form, 'patient':patient}
	return render(request,'inpatient_app/inpatient_admission_assessment_form.html',context)

def AssignInpatientToTeam(request):

	assign_form = AssignInpatientToTeamForm()

	if request.method == 'POST':
		assign_form = AssignInpatientToTeamForm(request.POST)
		if assign_form.is_valid():
			ward_team = assign_form.save()
			messages.success(request, ' Successfully Assigned!')
	context = {'assign_form':assign_form}
	return render(request, 'inpatient_app/assign_inpatient_to_team.html', context)


def AssignInpatientToTeam(request):
	assign_form = AssignInpatientToTeamForm()

	assigned_providers = []
	nurses = []
	ward_teams = WardTeamBed.objects.all()
	for team in ward_teams:
		if team.team:
			assigned_providers.append(team.team.ward_service_provider.id)
		if team.nurse_team:
			nurses.append(team.nurse_team.nurse.id)
	unassigned_providers = Employee.objects.exclude(id__in=assigned_providers)
	assign_form.fields["ward_service_provider"].queryset = Employee.objects.exclude(id__in=assigned_providers)

	if request.method == 'POST':
		assign_form = AssignInpatientToTeamForm(request.POST)
		if assign_form.is_valid():
			ward_team = assign_form.save()
			messages.success(request, ' Successfully Assigned!')
	context = {'assign_form':assign_form}
	return render(request, 'inpatient_app/assign_inpatient_to_team.html', context)

def AssignNurseToTeam(request):
	assign_form = AssignNurseToTeamForm()

	assigned_providers = []
	ward_teams = WardNurseTeam.objects.all()
	for team in ward_teams:
		assigned_providers.append(team.nurse.id)
#	unassigned_providers = Employee.objects.exclude(id__in=assigned_providers)
	assign_form.fields["nurse"].queryset = Employee.objects.exclude(id__in=assigned_providers)

	if request.method == 'POST':
		assign_form = AssignNurseToTeamForm(request.POST)
		if assign_form.is_valid():
			ward_team = assign_form.save()
			messages.success(request, ' Successfully Assigned!')
	context = {'assign_form':assign_form}
	return render(request, 'inpatient_app/assign_nurse_to_team.html', context)


def NurseProgressNote(request, patient_id):
	patient = Patient.objects.get(id=patient_id)
	stay_duration = PatientStayDuration.objects.filter(patient=patient, leave_date__isnull=True).last()
	try:
		instruction = InpatientDoctorOrder.objects.get(patient=patient, view_status='not_seen')
		instruction.view_status = 'seen'
		instruction.save()
	except Exception as e:
		instruction = None
	patient_medication = InpatientMedication.objects.filter(patient=patient, stay_duration=stay_duration)
	progress_chart_form = NurseProgressChartForm()
	if request.method == 'POST':
		progress_chart_form = NurseProgressChartForm(request.POST)
		if progress_chart_form.is_valid():
			chart_model = progress_chart_form.save(commit=False)
			chart_model.patient = patient
			chart_model.stay_duration = stay_duration
			chart_model.view_status = 'not_seen'
			chart_model.registered_on = datetime.now()

			try:
				chart_model.nurse = Employee.objects.get(user_profile=request.user, designation__name='Nurse')
				chart_model.ward_team_bed = WardTeamBed.objects.get(nurse_team__nurse=chart_model.nurse, bed__patient=patient)			
				messages.success(request, ' Successfully Assigned!')
				return redirect('nurse_chart_view', patient.id)

			except:
				chart_model.nurse = Employee.objects.get(user_profile=request.user, designation__name='Doctor')
				chart_model.ward_team_bed = WardTeamBed.objects.get(team__ward_service_provider=chart_model.nurse, bed__patient=patient)
				chart_model.save()				
				messages.success(request, ' Successfully Assigned!')
				return redirect('doctor_chart_view', patient.id)
	context = {'progress_chart_form':progress_chart_form, 'stay_duration':stay_duration}
	return render(request, 'inpatient_app/nurse_progress_note.html', context)




def DrugPrescriptionPharmacistFormPage(request, prescription_id):
#	patient = Patient.objects.get(id=patient_id)
#	stay_duration = PatientStayDuration.objects.get(patient=patient, leave_date__isnull=True)

#	patient_medication = InpatientMedication.objects.filter(patient=patient, stay_duration=stay_duration)
	prescription = DrugPrescription.objects.get(id=prescription_id)


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


	bill_detail = BillDetail()

	inpatient_bill = InpatientBillRelation.objects.filter(patient=prescription.patient, is_active='active').last()
	#drug_bill.bill = inpatient_bill.bill
	bill_detail.drug = prescription.info.drug
	bill_detail.patient = prescription.patient
	bill_detail.registered_on = datetime.now()
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
	bill_detail.department = 'Inpatient'
	bill_detail.registered_on = datetime.now()
	bill_detail.patient = prescription.patient
	bill_detail.quantity = prescribed_drug_quantity

	true_string = 'true'
	prescription.dispensed = true_string
	prescription.save()
	bill_detail.save()
	messages.success(request, ' Successful!')
	return redirect('pharmacist_administration_time_form', prescription.id)
#	context = {'pharmacist_form':pharmacist_form}
#	return render(request, 'inpatient_app/drug_prescription_pharmacist_form.html', context)

def PharmacistAdministrationTimeFormPage(request, prescription_id):
	prescription_model = DrugPrescription.objects.get(id=prescription_id)
	administration_form = DrugAdministrationTimeForm()
	if request.method == 'POST':
		administration_form = DrugAdministrationTimeForm(request.POST)
		if administration_form.is_valid():
			administration_model = administration_form.save(commit=False)
			administration_model.drug_prescription = prescription_model
			administration_model.registered_on = datetime.now()
			administration_model.save()
			messages.success(request, ' Successful!')
			return redirect('inpatient_prescription_list')

	context = {'administration_form':administration_form}
	return render(request, 'inpatient_app/pharmacist_administration_form.html', context)


def InpatientPrescriptionList(request):

	prescriptions = DrugPrescription.objects.filter(department=1,frequency__isnull=True)
	prescription_list = []
	for p in prescriptions:
		if InpatientAdministrationTime.objects.filter(drug_prescription__id =p.id).exists():
			print('Do Nothing')
		else:
			prescription_list.append(p)
	context = {'prescription_list':prescription_list}
	return render(request, 'inpatient_app/inpatient_prescription_list.html', context)

def VitalSignFormModalPage(request,patient_id, role_id):
	patient = Patient.objects.get(id=patient_id)
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
			if role_id == 1:
				return redirect('doctor_chart_view', patient_id)
			else:
				return redirect('nurse_chart_view',patient_id)
		else:
			messages.error(request, str(vital_form.errors))
			return redirect('doctor_chart_view', patient_id)

def DoctorChartView(request, patient_id):
	"""
	try:
		chart = NurseProgressChart.objects.get(ward_team_bed__id=ward_team_bed_id, view_status='not_seen')
		chart.view_status = 'seen'
		print('\n','try:::::::','\n')
	except:
		chart = NurseProgressChart.objects.filter(ward_team_bed__id=ward_team_bed_id)
		chart = chart.last()
		print('\n','except,,,,,,','\n')
#	chart.view_status = 'seen'
	"""
	print('\n',request.user.employee.designation.staff_code,'\n')

	patient = Patient.objects.get(id=patient_id)
	progress_note_list = NurseProgressChart.objects.filter(ward_team_bed__bed__patient=patient)[:1]
#	for p in progress_note_list:
#		print('\n',p,'\n')
	inpatient_reason = InpatientReason.objects.filter(patient=patient, status='active').last()

	care_plan = InpatientCarePlan.objects.filter(patient=patient, status='active').last()
	patient_allergy = PatientAllergy.objects.filter(patient=patient)
	patient_habit = PatientHabit.objects.filter(patient=patient)

	independent_intervention_list = NurseIndependentIntervention.objects.filter(patient=patient)[:1]
	evaluation_count_array = []
	for intervention in independent_intervention_list:
		evaluation_list_array = []
		evaluation_list = NurseEvaluation.objects.filter(independent_intervention=intervention)
		for evaluation in evaluation_list:
			evaluation_list_array.append(evaluation)
		evaluation_count_array.append(len(evaluation_list_array))
	intervention_zip = zip(independent_intervention_list, evaluation_count_array)

	vital_sign = PatientVitalSign.objects.filter(patient=patient, active='active').last()

	doctor_team = WardTeam.objects.get(ward_service_provider__user_profile=request.user)
	instruction_list = InpatientDoctorInstruction.objects.filter(ward_team_bed__team=doctor_team, instruction_status = 'not_done', patient=patient)

#	chart.save()
	
	patient_medication = InpatientMedication.objects.filter(patient=patient, drug_prescription__isnull=False)
	administration_time = []
	administration_times = []
	time_gap_array = []
	range_array = []
	for medication in patient_medication:
		print(medication.drug_prescription,'\n')
		medication_time = InpatientAdministrationTime.objects.filter(drug_prescription=medication.drug_prescription).last()
		if medication_time:
			administration_time.append( medication_time)
			administration_times.append(medication_time.first_time)
			time_gap_array.append(medication_time)
			if medication.drug_prescription.info:
				range_array.append(range(1,medication.drug_prescription.info.frequency))
			else:
				range_array.append(range(1,medication.drug_prescription.frequency))

	frequency = [1,2,3,4]
	for time in administration_times:
		print('yea yea','\n',time,'\n')
	try_zip = zip(patient_medication,time_gap_array,range_array)
	try_zip1 = zip(patient_medication,time_gap_array,range_array)

	medication_zip = zip(patient_medication,time_gap_array, range_array)	

	stay_duration = PatientStayDuration.objects.filter(patient=patient, leave_date__isnull=True).last()

	vital_form = VitalSignForm()
	progress_chart_form = NurseProgressChartForm()
	if request.method == 'POST':
		progress_chart_form = NurseProgressChartForm(request.POST)
		if progress_chart_form.is_valid():
			chart_model = progress_chart_form.save(commit=False)
			chart_model.patient = patient

			chart_model.nurse = Employee.objects.get(user_profile=request.user, designation__name='Doctor')
			chart_model.ward_team_bed = WardTeamBed.objects.filter(team__ward_service_provider=chart_model.nurse).last()
			chart_model.stay_duration = stay_duration
			chart_model.view_status = 'not_seen'
			chart_model.registered_on = datetime.now()
			chart_model.save()
			messages.success(request, 'Successful!')
	context = {'inpatient_reason':inpatient_reason, 'vital_sign':vital_sign, 'frequency':frequency,
				'instruction_list':instruction_list,
				'progress_note_list':progress_note_list,
				'patient':patient,
				'patient_medication':patient_medication,
				'medication_zip':medication_zip,
				'try_zip':try_zip,
				'try_zip1':try_zip1,
				'intervention_zip':intervention_zip,
				'care_plan':care_plan,
				'patient_habit':patient_habit,
				'patient_allergy':patient_allergy,
				'progress_chart_form':progress_chart_form,
				'vital_form':vital_form,
				}
	return render(request, 'inpatient_app/new_doctor_chart_view.html', context)
#nurse_instruction_view.html

def LastNurseProgressNoteList(request, patient_id):
	patient = Patient.objects.get(id=patient_id)
	progress_note_list = NurseProgressChart.objects.filter(ward_team_bed__bed__patient=patient)[:10][::-1]

	context = {'progress_note_list':progress_note_list}
	return render(request, 'inpatient_app/last_nurse_progress_list.html', context)

def AllProgressNoteList(request, patient_id):
	patient = Patient.objects.get(id=patient_id)
	progress_note_list = NurseProgressChart.objects.filter(ward_team_bed__bed__patient=patient)

	context = {'progress_note_list':progress_note_list}
	return render(request, 'inpatient_app/all_progress_note_list.html', context)

def NurseChartView(request, patient_id):
	"""
	try:
		chart = NurseProgressChart.objects.get(ward_team_bed__id=ward_team_bed_id, view_status='not_seen')
		chart.view_status = 'seen'
		print('\n','try:::::::','\n')
	except:
		chart = NurseProgressChart.objects.filter(ward_team_bed__id=ward_team_bed_id)
		chart = chart.last()
		print('\n','except,,,,,,','\n')
#	chart.view_status = 'seen'
	"""

	patient = Patient.objects.get(id=patient_id)
	
	progress_note_list = NurseProgressChart.objects.filter(ward_team_bed__bed__patient=patient)[:1] 
	inpatient_reason = InpatientReason.objects.get(patient=patient, status='active')
	care_plan = InpatientCarePlan.objects.get(patient=patient, status='active')
	try:
		vital_sign = PatientVitalSign.objects.get(patient=patient, active='active')	
	except :
		vital_sign = None
	patient_allergy = PatientAllergy.objects.filter(patient=patient)
	patient_habit = PatientHabit.objects.filter(patient=patient)

	independent_intervention_list = NurseIndependentIntervention.objects.filter(patient=patient)[:1][::-1]
	evaluation_count_array = []
	for intervention in independent_intervention_list:
		evaluation_list_array = []
		evaluation_list = NurseEvaluation.objects.filter(independent_intervention=intervention)
		for evaluation in evaluation_list:
			evaluation_list_array.append(evaluation)
		evaluation_count_array.append(len(evaluation_list_array))
	intervention_zip = zip(independent_intervention_list, evaluation_count_array)

	nurse_team = WardNurseTeam.objects.get(nurse__user_profile=request.user)
	instruction_list = InpatientDoctorInstruction.objects.all()
	intervention_count_array = []
	for instruction in instruction_list:
		intervention_list_array = []
		intervention_list = NurseInstructionCheck.objects.filter(doctor_instruction=instruction)
		for intervention in intervention_list:
			intervention_list_array.append(intervention)
		intervention_count_array.append(len(intervention_list_array))
	instruction_zip = zip(instruction_list, intervention_count_array)

#	chart.save()
	
	patient_medication = InpatientMedication.objects.filter(patient=patient, drug_prescription__isnull=False)
	administration_time = []
	administration_times = []
	time_gap_array = []
	range_array = []
	"""
	for medication in patient_medication:
#		print(medication.drug_prescription,'\n')
 
		medication_time = InpatientAdministrationTime.objects.get(drug_prescription=medication.drug_prescription)
		administration_time.append( medication_time)
		administration_times.append(medication_time.first_time)
		time_gap_array.append(medication_time)
		range_array.append(range(1,medication.drug_prescription.frequency))
	"""
	for medication in patient_medication:
		print(medication.drug_prescription,'\n')
		medication_time = InpatientAdministrationTime.objects.filter(drug_prescription=medication.drug_prescription, drug_prescription__info__isnull=False).last()
		if medication_time:
			administration_time.append( medication_time)
			administration_times.append(medication_time.first_time)
			time_gap_array.append(medication_time)
			range_array.append(range(1,medication.drug_prescription.info.frequency))

		"""
		if medication.drug_prescription.frequency > 1:
			for i in range(1,medication.drug_prescription.frequency):
				if medication_time.first_time:
					hour = medication_time.first_time.hour
					gap = i * medication_time.time_gap 
					next_time = medication_time.first_time
					next_time = hour + gap
					administration_times.append(next_time)
					print('\n', "tried")
				else:
					print('\n', "nottried")
					administration_times.append(None)
		"""
		"""
		except:
			administration_time.append(None)
			administration_times.append(None)
			print('\n','excepted')
		"""
	frequency = [1,2,3,4]
	for time in administration_times:
		print('yea yea','\n',time,'\n')
	try_zip = zip(patient_medication,time_gap_array,range_array)
	try_zip1 = zip(patient_medication,time_gap_array,range_array)

	medication_zip = zip(patient_medication,time_gap_array, range_array)	

	stay_duration = PatientStayDuration.objects.filter(patient=patient, leave_date__isnull=True).last()
	vital_form = VitalSignForm()

	progress_chart_form = NurseProgressChartForm()
	if request.method == 'POST':
		progress_chart_form = NurseProgressChartForm(request.POST)
		if progress_chart_form.is_valid():
			chart_model = progress_chart_form.save(commit=False)
			chart_model.patient = patient

			chart_model.nurse = Employee.objects.filter(user_profile=request.user, designation__name='Nurse').last()
			chart_model.ward_team_bed = WardTeamBed.objects.get(nurse_team__nurse=chart_model.nurse, bed__patient=patient)
			chart_model.stay_duration = stay_duration
			chart_model.view_status = 'not_seen'
			chart_model.registered_on = datetime.now()
			chart_model.save()
			messages.success(request, 'Successful!')


	context = {'inpatient_reason':inpatient_reason, 'vital_sign':vital_sign, 'frequency':frequency,
				'instruction_zip':instruction_zip,
				'progress_note_list':progress_note_list,
				'patient':patient,
				'patient_medication':patient_medication,
				'medication_zip':medication_zip,
				'try_zip':try_zip,
				'try_zip1':try_zip1,
				'care_plan':care_plan,
				'patient_allergy':patient_allergy,
				'patient_habit':patient_habit,
				'intervention_zip':intervention_zip,
				'progress_chart_form':progress_chart_form,
				'vital_form':vital_form,
				}
	return render(request, 'inpatient_app/nurse_instruction_view.html', context)
#nurse_instruction_view.html

def InstructionDetail(request, instruction_id):
	instruction = InpatientDoctorInstruction.objects.get(id=instruction_id)

	intervention_list = NurseInstructionCheck.objects.filter(doctor_instruction=instruction)
	context = {'intervention_list':intervention_list, 'instruction':instruction}
	return render(request, 'inpatient_app/intervention_list_for_doctor.html', context)


def NurseInstructionResponseFormPage(request, instruction_id):
	instruction = InpatientDoctorInstruction.objects.get(id=instruction_id)
	intervention_list = NurseInstructionCheck.objects.filter(doctor_instruction=instruction)
	
	evaluation_count_array = []
	for intervention in intervention_list:
		evaluation_list_array = []
		evaluation_list = NurseEvaluation.objects.filter(intervention=intervention)
		for evaluation in evaluation_list:
			evaluation_list_array.append(evaluation)
		evaluation_count_array.append(len(evaluation_list_array))
	intervention_zip = zip(intervention_list, evaluation_count_array)
	response_form = NurseInstructionResponseForm()
	if request.method == 'POST':
		response_form = NurseInstructionResponseForm(request.POST)
		if response_form.is_valid():
			instruction_check_model = response_form.save(commit=False)
			instruction_check_model.doctor_instruction = instruction
			#instruction_check_model.check_status = 'checked'
			instruction_check_model.nurse = Employee.objects.get(user_profile=request.user, designation__name='Nurse')
			instruction_check_model.registered_on = datetime.now()
			
			instruction_check_model.save()
			return redirect('nurse_evaluation_form', instruction_check_model.id)
			messages.success(request, 'Successful! ')
	context = {'response_form':response_form,
				'instruction':instruction,
				'intervention_zip':intervention_zip,
	}

	return render(request, 'inpatient_app/nurse_instruction_response_form.html', context)


def NurseIndependentInterventionFormPage(request, patient_id):
	patient = Patient.objects.get(id=patient_id)
	intervention_form = NurseIndependentInterventionForm()
	if request.method == 'POST':
		intervention_form = NurseIndependentInterventionForm(request.POST)
		if intervention_form.is_valid():
			intervention_model = intervention_form.save(commit=False)
			intervention_model.patient = patient
			intervention_model.nurse = Employee.objects.get(user_profile=request.user, designation__name='Nurse')
			intervention_model.evaluation_status = 'not_evaluated'
			intervention_model.registered_on = datetime.now()
			intervention_model.save()
			messages.success(request, 'Successful! ')
			return redirect('nurse_chart_view', patient.id)
	context = {'intervention_form':intervention_form}
	return render(request, 'inpatient_app/nurse_independent_intervention_form.html', context)

def InterventionListForNurse(request):
	intervention_list = NurseInstructionCheck.objects.exclude(evaluation_status='evaluated', doctor_instruction__ward_team_bed__nurse_team__nurse__user_profile=request.user)

	context = {'intervention_list':intervention_list}	
	return render(request, 'inpatient_app/intervention_list_for_nurse.html', context)
def InterventionDetail(request, intervention_id):
	intervention = NurseInstructionCheck.objects.get(id=intervention_id)
	evaluation_list = NurseEvaluation.objects.filter(intervention=intervention)
	for evaluation in evaluation_list:
		print('\n',evaluation.evaluation,'\n')
	context = {'intervention':intervention, 'evaluation_list':evaluation_list}
	return render(request, 'inpatient_app/intervention_detail.html', context)

def IndependentInterventionDetail(request, intervention_id):
	intervention = NurseIndependentIntervention.objects.get(id=intervention_id)
	evaluation_list = NurseEvaluation.objects.filter(independent_intervention=intervention)
	for evaluation in evaluation_list:
		print('\n',evaluation.evaluation,'\n')
	context = {'intervention':intervention, 'evaluation_list':evaluation_list}
	return render(request, 'inpatient_app/independent_intervention_detail.html', context)

def NurseEvaluationFormPage(request, intervention_id):
	intervention = NurseInstructionCheck.objects.get(id=intervention_id)
	evaluation_form = NurseEvaluationForm()
	if request.method == 'POST':
		evaluation_form = NurseEvaluationForm(request.POST)
		if evaluation_form.is_valid():
			evaluation_model = evaluation_form.save(commit=False)
			evaluation_model.intervention = intervention
			#instruction_check_model.check_status = 'checked'
			evaluation_model.registered_on = datetime.now()
			evaluation_model.nurse = Employee.objects.get(user_profile=request.user, designation__name='Nurse')			
			evaluation_model.save()
			messages.success(request, 'Successful!')
			return redirect('nurse_chart_view', intervention.doctor_instruction.patient.id)
	context = {'evaluation_form':evaluation_form,
				'intervention':intervention
				}
	return render(request, 'inpatient_app/nurse_evaluation_form.html', context)

def NurseIndependentInterventionEvaluationFormPage(request, intervention_id):
	intervention = NurseIndependentIntervention.objects.get(id=intervention_id)
	evaluation_form = NurseEvaluationForm()
	if request.method == 'POST':
		evaluation_form = NurseEvaluationForm(request.POST)
		if evaluation_form.is_valid():
			evaluation_model = evaluation_form.save(commit=False)
			evaluation_model.independent_intervention = intervention
			#instruction_check_model.check_status = 'checked'
			evaluation_model.registered_on = datetime.now()
			evaluation_model.nurse = Employee.objects.get(user_profile=request.user, designation__name='Nurse')			
			evaluation_model.save()
			messages.success(request, 'Successful!')
			return redirect('nurse_chart_view', intervention.patient.id)
	context = {'evaluation_form':evaluation_form,
				'intervention':intervention
				}
	return render(request, 'inpatient_app/nurse_independent_intervention_evaluation_form.html', context)

def NurseDashboard(request):
	nurse_team = WardNurseTeam.objects.get(nurse__user_profile=request.user)
	instruction_list = InpatientDoctorInstruction.objects.filter(ward_team_bed__nurse_team=nurse_team)
	instruction_count = instruction_list.count()
	nurse_patient_list = WardTeamBed.objects.filter(nurse_team=nurse_team)
	nurse_patient_list_array = []
	for ward in nurse_patient_list:
		nurse_patient_list_array.append(ward.bed.patient)

	medication_list = InpatientMedication.objects.filter(patient__in=nurse_patient_list_array)	
	medication_count = medication_list.count()

	intervention_list = NurseInstructionCheck.objects.filter(doctor_instruction__ward_team_bed__nurse_team=nurse_team)	
	intervention_count = intervention_list.count()

	context = {'intervention_count':intervention_count,
				'instruction_count':instruction_count,
				'medication_count':medication_count
					}
	return render(request, 'inpatient_app/nurse_dashboard.html', context)

#Lists all patients under nurse that are being administered drugs
def MedicationToBeAdministeredListForNurse(request):
	nurse_team = WardNurseTeam.objects.get(nurse__user_profile=request.user)

	nurse_patient_list = WardTeamBed.objects.filter(nurse_team=nurse_team)
	nurse_patient_list_array = []
	for ward in nurse_patient_list:
		nurse_patient_list_array.append(ward.bed.patient.id)

	patient_list = Patient.objects.all()

	medication_list = InpatientMedication.objects.filter(patient__id__in=nurse_patient_list_array)
	drug_patient_list = Patient.objects.filter(id__in=nurse_patient_list_array)
	medication_zip = zip(medication_list, drug_patient_list)
	medication_patient = []
	bed_array = []
	
	for patient in patient_list:
		for medication in medication_list:
			if medication.patient == patient:
				if medication.patient in medication_patient:
					print('mothing')
				else:
					medication_patient.append(medication)
	"""
#					bed = Bed.objects.get(patient=medication.patient)
#					bed_array.append(bed)
					print('\n', 'dddddd',medication , bed ,'\n')				

	medication_zip = zip(bed_array, medication_patient)
	print('heeeeee')
	for m,b in medication_zip:
		print('\n', 'dddddd',m , b ,'\n')
	"""	
	context = {'medication_zip':medication_zip}
	return render(request, 'inpatient_app/medicine_to_be_administered_list_for_nurse.html', context)
def MedicalAdministrationDetail(request, patient_id):
	patient = Patient.objects.get(id=patient_id)
	"""
	medication_list = InpatientMedication.objects.filter(patient=patient)
	administration_time_array = []
	for medication in medication_list:
		administration_time_array.append(InpatientAdministrationTime.objects.get(drug_prescription=medication.drug_prescription))
	"""
	patient_medication = InpatientMedication.objects.filter(patient=patient, drug_prescription__info__isnull=False)
	administration_time = []
	administration_times = []
	time_gap_array = []
	range_array = []
	for medication in patient_medication:
		medication_time = InpatientAdministrationTime.objects.get(drug_prescription=medication.drug_prescription, drug_prescription__info__isnull=False)
		administration_time.append( medication_time)
		administration_times.append(medication_time.first_time)
		time_gap_array.append(medication_time)
		range_array.append(range(1,medication.drug_prescription.info.frequency))

	frequency = [1,2,3,4]
	for time in administration_times:
		print('yea yea','\n',time,'\n')
	medication_zip = zip(patient_medication,time_gap_array,range_array)

	context = {'medication_zip':medication_zip}
	return render(request, 'inpatient_app/medical_administration_detail.html', context)

def MarkDrugAsAdministered(request, prescription_id):
	prescription = DrugPrescription.objects.get(id=prescription_id)
	new_administration_model = InpatientMedicalAdministration()
	new_administration_model.drug_prescription = prescription
	new_administration_model.administered_by =  Employee.objects.get(user_profile=request.user, designation__name='Nurse')
	new_administration_model.administration_on = datetime.now()
	new_administration_model.save()
	messages.success(request,'Drug Administration Successful!')
	return redirect('medical_administration_detail', prescription.patient.id)

def MarkInterventionAsDone(request, intervention_id):
	intervention = NurseInstructionCheck.objects.get(id=intervention_id)
	intervention.evaluation_status = 'evaluated'
	intervention.save()
	return redirect('intervention_list_for_nurse')

def MarkInstructionAsDone(request, instruction_id):
	instruction = InpatientDoctorInstruction.objects.get(id=instruction_id)
	instruction.nurse_check_status = 'checked'
	instruction.save()
	return redirect('doctor_chart_view', instruction.patient.id)

def MarkInstructionAsDoneForDoctor(request, instruction_id):
	instruction = InpatientDoctorInstruction.objects.get(id=instruction_id)
	instruction.instruction_status = 'Done'
	instruction.save()
	return redirect('doctor_chart_view', instruction.patient.id)

def DoctorInstructionFormPage(request, patient_id):
	patient = Patient.objects.get(id=patient_id)
	stay_duration = PatientStayDuration.objects.filter(patient=patient, leave_date__isnull=True).last()

	try:
		progress_chart = NurseProgressChart.objects.get(patient=patient, view_status='not_seen')
		progress_chart.view_status ='seen'
	except Exception as e:
		progress_chart = None
	instruction_form = InpatientDoctorInstructionForm()
	if request.method == 'POST':
		instruction_form = InpatientDoctorInstructionForm(request.POST)
		if instruction_form.is_valid():
			instruction_model = instruction_form.save(commit=False)
			instruction_model.patient = patient
			instruction_model.doctor = Employee.objects.get(user_profile=request.user, designation__name='Doctor')
			#instruction_model.ward_team_bed = WardTeamBed.objects.get(team__ward_service_provider=instruction_model.doctor, bed__patient=patient)#bed=
			instruction_model.stay_duration = stay_duration
			instruction_model.view_status = 'not_seen'
			instruction_model.instruction_status = 'not_done'
			instruction_model.registered_on = datetime.now()
			instruction_model.save()
			messages.success(request, 'Successful!')
			return redirect('doctor_chart_view', patient.id)

	context = {'instruction_form':instruction_form}	
	return render(request, 'inpatient_app/doctor_instruction_form.html', context)

def DischargeSummaryFormPage(request, patient_id):
	patient = Patient.objects.get(id=patient_id)
	#stay_duration = WardStayDuration.objects.get(patient=patient, leave_date__isnull=True)
	print(patient)
	discharge_form = DischargeSummaryForm()
	if request.method == 'POST':
		discharge_form = DischargeSummaryForm(request.POST)
		if discharge_form.is_valid():
			discharge_model = discharge_form.save(commit=False)
			discharge_model.patient = patient
			#discharge_model.discharged_by = Employee.objects.get(user_profile=request.user, designation__name='Doctor')
			#discharge_model.stay_duration = stay_duration
			discharge_model.registered_on = datetime.now()
			discharge_model.active = True

			discharge_model.save()
			messages.success(request, 'Successful!')
			return redirect('discharge_inpatient', patient.id)

	context = {'discharge_form':discharge_form,'patient_id': patient_id}
	return render(request, 'inpatient_app/discharge_summary_form.html', context)

def DischargeInpatient(request, patient_id):
	patient = Patient.objects.get(id=patient_id)

	stay_duration = WardStayDuration.objects.get(patient=patient, leave_date__isnull=True)
	stay_duration.leave_date = datetime.now()

	duration_amount = int(stay_duration.leave_date.day) - int( stay_duration.admission_date.day)
	"""
	room_price = RoomPrice.objects.get(room = stay_duration.room)

	room_bill = InpatientRoomBillDetail.objects.get(patient=patient, active='active')
#	room_bill.active = 'not_active'
	room_bill.room_price = room_price.room_price * duration_amount
	"""
	room_bill = RoomBillDetail()
	room_bill.room = stay_duration.bed
	room_bill.patient = stay_duration.patient
	room_bill.registered_on = datetime.now()
	payment_status = PatientPaymentStatus.objects.get(patient=patient,active=True)
	try:
		price = RoomPrice.objects.get(room=stay_duration.room,active=True)
	except:
		price = RoomPrice.objects.filter().last()
		#room_price.room = stay_duration.bed
		#room_price.room_price = 100
		#room_price.discounted_price = 50
		#room_price.active=True
		#room_price.save()
		#messages.error(request,'Room Price Has Not Been Assigned')
		#return redirect('core:patient_dashboard', patient.id)
	room_bill.room_price = price
	if payment_status.payment_status=='Free':
		room_bill.free = True
		room_bill.discount = False
		room_bill.insurance = False
		room_bill.credit = False
		room_bill.price = None

	elif payment_status.payment_status == 'Insurance':
		room_bill.free = False
		room_bill.discount = False
		room_bill.insurance = True
		room_bill.credit = False

	elif payment_status.payment_status == 'discount':
		room_bill.free = False
		room_bill.discount = True
		room_bill.insurance = False
		room_bill.credit = False

	else:
		room_bill.free = False
		room_bill.discount = False
		room_bill.insurance = False
		room_bill.credit = False

	#inpatient_reason = InpatientReason.objects.get(patient=patient, status='active')
	#inpatient_reason.status ='not_active'	

	bed = Bed.objects.get(patient=patient)
	#bed_release_date = BedReleaseDate.objects.get(bed=bed, status = 'active')
	#bed_release_date.status = 'not_active'

	#priority_level = AdmissionPriorityLevel.objects.get(patient=patient, status='active')	
	#priority_level.status = 'not_active'

	#priority_level.save()
	#bed_release_date.save()
	print('\n', 'Successful 111','\n')
	#stay_duration_prediction = PatientStayDurationPrediction.objects.get(patient=patient,active=True)
	#stay_duration_prediction.active = False
	#stay_duration_prediction.save()
	print('\n', 'Successful 222','\n')
#	notify(request.user,'info', ' Trial notification ', trial_string,link='/patient_list_for_doctor')

	#inpatient_care_plan = InpatientCarePlan.objects.filter(patient=patient, status='active')
	#for care_plan in inpatient_care_plan:
	#	care_plan.status = 'not_active'
	#	care_plan.save()

	#print('one done','\n')
		
#	inpatient_care_plan.save()	
	
	#inpatient_reason.save()	

	#patient_bill.save()

	stay_duration.save()
	room_bill.save()


	string = str(bed) + " Released!"
	notify(request.user,'info', ' Trial notification ', string,link='/patient_list')
	messages.success(request, 'Successful!')
	return redirect('core:patient_dashboard', patient.id)

def InstructionListForNurse(request):
	instruction_list = InpatientDoctorInstruction.objects.filter(ward_team_bed__nurse_team__nurse__user_profile=request.user)
	context = {'instruction_list':instruction_list}
	return render(request,'inpatient_app/instruction_list_for_nurse.html',context)


def InpatientBillDetailPage(request, patient_id):
	"""
	for price in RoomPrice.objects.all():
		price.delete()
	for bed in Bed.objects.all()
	"""
	patient = Patient.objects.get(id=patient_id)	
	#patient_bill = InpatientBillRelation.objects.get(patient=patient, is_active='active')	
	stay_duration = WardStayDuration.objects.filter(patient=patient).last()
	room_price = RoomPrice.objects.filter().last()
	duration_amount = int(stay_duration.leave_date.day) - int( stay_duration.admission_date.day)

	room_bill = RoomBillDetail.objects.filter(patient=patient, stay_duration=stay_duration).last()

	drug_bill = DrugBill.objects.filter(patient=patient, stay_duration=stay_duration)
	lab_bill = LabBillDetail.objects.filter(patient=patient, stay_duration=stay_duration)

#	single_drug_price = drug_price / 
	drug_price_dict = drug_bill.aggregate(Sum('selling_price__selling_price'))
	print(drug_price_dict)
	drug_price = drug_price_dict['selling_price__selling_price__sum']

	#lab_price_dict = lab_bill.aggregate(Sum('service_price'))
	#service_price = service_price_dict['service_price__sum']
	"""
	if drug_price  is not None:
		if service_price is not None:
			total_price = room_bill.room_price + drug_price + service_price
		else:
			total_price = room_bill.room_price + drug_price
	else:
		if service_price is not None: 
			total_price = room_bill.room_price + service_price
		else:
			total_price = room_bill.room_price
	"""

	if drug_price:
		total_price = room_price.room_price + int(drug_price)
	else:
		total_price = room_price.room_price
	context = {'room_bill':room_bill, 
				'stay_duration':duration_amount,
				'room_price':room_price,
				'drug_bill':drug_bill, 
				'total_price':total_price,
				'patient':patient,

#				'single_drug_price':single_drug_price
	}
	return render(request,'inpatient_app/inpatient_bill_detail.html',context)

def StayDurationBillDetailPage(request, patient_id):
	patient = Patient.objects.get(id=patient_id)	
	patient_bill = InpatientBillRelation.objects.get(patient=patient, is_active='active')	
	stay_duration = PatientStayDuration.objects.filter(patient=patient)
	stay_duration = stay_duration.last()
	room_price = RoomPrice.objects.get(room = stay_duration.room)

	duration_amount = int(stay_duration.leave_date.day) - int( stay_duration.admission_date.day)

	room_bill = InpatientRoomBillDetail.objects.get(patient=patient, bill=patient_bill.bill, active='active')
	drug_bill = InpatientDrugBillDetail.objects.filter(patient=patient, bill=patient_bill.bill)
	service_bill = InpatientServiceBillDetail.objects.filter(patient=patient, bill=patient_bill.bill)

#	single_drug_price = drug_price / 
	drug_price_dict = drug_bill.aggregate(Sum('drug_price'))
	drug_price = drug_price_dict['drug_price__sum']

	service_price_dict = service_bill.aggregate(Sum('service_price'))
	service_price = service_price_dict['service_price__sum']

	if drug_price  is not None:
		if service_price is not None:
			total_price = room_bill.room_price + drug_price + service_price
		else:
			total_price = room_bill.room_price + drug_price
	else:
		if service_price is not None: 
			total_price = room_bill.room_price + service_price
		else:
			total_price = room_bill.room_price
	context = {'room_bill':room_bill, 'stay_duration':duration_amount, 'room_price':room_price,
				'drug_bill':drug_bill, 'service_bill':service_bill, 'total_price':total_price,
#				'single_drug_price':single_drug_price
	}
	return render(request,'inpatient_app/inpatient_bill_detail.html',context)


def ReallyDischargeInpatient(request, patient_id):
	patient = Patient.objects.get(id=patient_id)
	patient_bill = InpatientBillRelation.objects.get(patient=patient, is_active='active')	
	patient_bill.is_active = 'not_active'


	room_bill = InpatientRoomBillDetail.objects.get(patient=patient, active='active')
	room_bill.active = 'not_active'

	patient.inpatient = 'no'

	bed = Bed.objects.get(patient=patient)
	bed.patient = None
	bed.save()

	patient.save()
	patient_bill.save()
	room_bill.save()
	messages.success(request, 'Successful!')
	return redirect('patient_list_for_doctor')


def RoomBillList(request, patient_id):
	patient = Patient.objects.get(id=patient_id)
	stay_duration = PatientStayDuration.objects.filter(patient=patient)
	for duration in stay_duration:
		room_bill = InpatientRoomBillDetail.objects.filter(registered_on__day=duration.admission_date.day)
#		if room_bill.registered_on.day == duration.admission_date.day:
#			if room_bill.registered_on.hour == duration.admission_date.hour:
#				if room_bill.registered_on.minute == duration.admission_date.minute:
#					print('nothing happens!')
		for room_bill in room_bill:
			print('\n', '11 : ',room_bill.bill)
	context = {'stay_duration':stay_duration, 'patient':patient}
	return render(request,'inpatient_app/room_bill_list.html',context)

def BedStayDuration(request, bed_id):

	stay_duration = PatientStayDuration.objects.filter(room__id=bed_id)

#	room_bill = InpatientRoomBillDetail.objects.filter(bill=stay_duration.bill)

	context = {'stay_duration':stay_duration}
	return render(request,'inpatient_app/bed_stay_duration.html',context)


def DurationBillDetail(request, duration_id):
	stay_duration = PatientStayDuration.objects.get(id=duration_id)
	patient = stay_duration.patient
	room_bill = InpatientRoomBillDetail.objects.get(bill=stay_duration.bill)

	room_price = RoomPrice.objects.get(room = stay_duration.room)

	duration_amount = int(stay_duration.leave_date.day) - int( stay_duration.admission_date.day)

#	room_bill = InpatientRoomBillDetail.objects.get(patient=patient, bill=patient_bill.bill, active='active')
	drug_bill = InpatientDrugBillDetail.objects.filter(patient=patient, bill=stay_duration.bill)
	service_bill = InpatientServiceBillDetail.objects.filter(patient=patient, bill=stay_duration.bill)

#	single_drug_price = drug_price / 
	drug_price_dict = drug_bill.aggregate(Sum('drug_price'))
	drug_price = drug_price_dict['drug_price__sum']

	service_price_dict = service_bill.aggregate(Sum('service_price'))
	service_price = service_price_dict['service_price__sum']

	if drug_price  is not None:
		if service_price is not None:
			total_price = room_bill.room_price + drug_price + service_price
		else:
			total_price = room_bill.room_price + drug_price
	else:
		if service_price is not None: 
			total_price = room_bill.room_price + service_price
		else:
			total_price = room_bill.room_price
	context = {'room_bill':room_bill, 'stay_duration':duration_amount, 'room_price':room_price,
				'drug_bill':drug_bill, 'service_bill':service_bill, 'total_price':total_price,
#				'single_drug_price':single_drug_price
	}


#	context = {'duration_bill':duration_bill}
	return render(request,'inpatient_app/duration_bill_detail.html',context)

def RoomPriceFormPage(request):
	
	room_price_form = RoomPriceForm()
	
	if request.method == 'POST':
		room_price_form = RoomPriceForm(request.POST)
		if room_price_form.is_valid():
			room_price_model = room_price_form.save(commit=False)
			room_prices = RoomPrice.objects.all()
			for room in room_prices:
				room.room_price = room_price_model.room_price
				room.save()
			messages.success(request, ' Successfully Assigned!')
	context = {'room_price_form':room_price_form}
	return render(request, 'inpatient_app/room_price_form.html', context)

def InpatientRoomList(request):
#	stay_duration_list = PatientStayDuration.objects.all()
#	print('\n','time: ', stay_duration_list.last().admission_date)
	room_prices = RoomPrice.objects.all()
	
	context = {'room_prices':room_prices}
	return render(request,'inpatient_app/inpatient_room_list.html',context)


def ChangeRoomPriceFormPage(request, room_price_id):	


	room_price_form = RoomPriceForm()
	
	if request.method == 'POST':
		room_price_form = RoomPriceForm(request.POST)
		if room_price_form.is_valid():
			room_price_model = room_price_form.save(commit=False)
			room_price = RoomPrice.objects.get(id=room_price_id)
			room_price.room_price = room_price_model.room_price
			room_price.save()			
			messages.success(request, ' Successfully Assigned!')
			return redirect('inpatient_room_list')
	context = {'room_price_form':room_price_form}
	return render(request, 'inpatient_app/room_price_form.html', context)

def CheckCurrentPatient(request, bed_id):
	bed = Bed.objects.get(id=bed_id)
	patient = bed.patient
	stay_duration = PatientStayDuration.objects.get(room=bed, patient =patient, leave_date__isnull=True)
	today = datetime.now()
	duration =  today.day - stay_duration.admission_date.day
#	print('\n',stay_duration.bed.id,'\n')
	context = {'stay_duration':stay_duration, 'patient':patient, 'duration':duration}
	return render(request, 'inpatient_app/check_current_patient.html', context)

def ChangePatientBed(request, bed_id):
	bed = Bed.objects.get(id=bed_id)
	bed_form = ChangePatientBedForm()
	if request.method =='POST':
		bed_form = ChangePatientBedForm(request.POST)
		if bed_form.is_valid():
			bed_model = bed_form.save(commit=False)
			
			new_bed = Bed.objects.get(id=bed_model.bed.id)
			new_bed.patient = bed.patient
			bed.patient = None
			bed.save()
			new_bed.save()
			messages.success(request, 'Bed Successfully Changed!')
			return redirect('inpatient_room_list')
	context = {'bed_form':bed_form, 'bed':bed}
	return render(request, 'inpatient_app/change_patient_bed.html', context)


def InpatientObservationFormPage(request, patient_id):
	patient = Patient.objects.get(id=patient_id)
	observation_form = InpatientObservationForm()
	bed = Bed.objects.get(patient=patient)
	stay_duration = PatientStayDuration.objects.get(room=bed,patient=patient, leave_date__isnull=True)
	if request.method=='POST':
		observation_form = InpatientObservationForm(request.POST)
		if observation_form.is_valid():
			observation_model = observation_form.save(commit=False)
			observation_model.patient = patient
			observation_model.stay_duration = stay_duration
			observation_model.registered_on = datetime.now()
			observation_model.save()
			messages.success(request, 'Successful!')
			
	context = {'observation_form':observation_form}
	return render(request, 'inpatient_app/inpatient_observation_form.html', context)

def PatientStayDurationList(request, patient_id):
	patient = Patient.objects.get(id=patient_id)
	stay_duration = PatientStayDuration.objects.filter(patient=patient)
	context = {'stay_duration':stay_duration}
	return render(request, 'inpatient_app/patient_stay_duration_list.html', context)

	 
def DurationMedication(request, stay_duration_id):
	stay_duration = PatientStayDuration.objects.get(id=stay_duration_id)
	medications = InpatientMedication.objects.filter(patient=stay_duration.patient)
	medication = []

	for m in medications:
		if m.registered_on > stay_duration.admission_date:
			if stay_duration.leave_date:
				if m.registered_on < stay_duration.leave_date:
					medication.append(m)
			else:
				medication.append(m)
	context = {'medication':medication}
	return render(request, 'inpatient_app/duration_medication.html', context)



#def 
def InpatientReport(request):
# Chart data is passed to the `dataSource` parameter, like a dictionary in the form of key-value pairs.
	dataSource = OrderedDict()
	admission_chart = OrderedDict()
	used_service_chart = OrderedDict()
	payment_status_chart = OrderedDict()
	discharge_chart = OrderedDict()

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

	admission_chart["chart"] = chartConfig
	admission_chart["chart"] = {
		"caption":'Patients Admitted From',
		"subCaption":'In Unit',
		"numberSuffix":'Patients',
		'theme':'fusion',
	}

	used_service_chart["chart"] = chartConfig
	used_service_chart["chart"] = {
		"caption":'Total Used Resource By Patient',
		"subCaption":'In Unit',
		"numberSuffix":'Patients',
		'theme':'fusion',
		'yAxisName':'Number Of Patients',
	}
	used_service_chart["data"] = []


	payment_status_chart["chart"] = chartConfig
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
		"subCaption":'In Unit',
		"numberSuffix":'Patients',
		'theme':'fusion',
		'yAxisName':'Number Of Patients',
	}
	discharge_chart["data"] = []

	admission_chart["data"] = []
	
	start_date = datetime.strptime(request.GET.get('start_date') or '1970-01-01', '%Y-%m-%d')
	end_date = datetime.strptime(request.GET.get('end_date') or str(datetime.now().date()),  '%Y-%m-%d')

	admission_amount = PatientStayDuration.objects.filter(admission_date__range=['2020-01-01','2024-01-01'],patient__isnull=False)

	allocated_beds = Bed.objects.filter(patient__isnull=False).count()
	unallocated_beds = Bed.objects.filter(patient__isnull=True).count()
	bed_usage = []
	bed_array = []
	for bed in Bed.objects.all():
		bed_duration = PatientStayDuration.objects.filter(room=bed)
		if bed_duration:
			if bed_duration.count()>1:
				bed_usage.append(bed_duration.count())
				bed_array.append(bed)
	bed_zip = zip(bed_usage,bed_array)
	patients = []
	for duration in admission_amount:
		patients.append(duration.patient)

	count1= 0
	total_stay = 0
	for patient in patients:
		durations = PatientStayDuration.objects.filter(patient=patient,admission_date__range=['2020-01-01','2024-01-01'], leave_date__isnull=False)
		if durations:
			count = 0
			total_stay_length = 0
			for d in durations:
				count = count + 1
				stay_length = d.admission_date.day - d.leave_date.day
				total_stay_length = stay_length + total_stay_length
			patient_stay = total_stay_length / count
			total_stay = total_stay + patient_stay
			count1 = count1 + 1
	average_stay_length = total_stay/count1

	medications = InpatientMedication.objects.filter(patient__isnull=False)
	average_medication = medications.count()/admission_amount.count()

	lab_tests = InpatientLabOrder.objects.filter(patient__isnull=False)
	average_lab_test = lab_tests.count() / admission_amount.count()
	print(average_lab_test,'ll')
	#xray_tests = InpatientLabOrder.objects.filter(patient__isnull=False)
	average_xray_test = average_lab_test

	emergency_admitted = InpatientAdmissionAssessment.objects.filter(admitted_from='Emergency Department').count()
	admission_chart["data"].append({"label": 'Admitted From Emergency ', "value": emergency_admitted})

	opd_admitted = admission_amount.count() - emergency_admitted
	admission_chart["data"].append({"label": 'Admitted From OPD', "value": opd_admitted})

	total_discharge = InpatientDischargeSummary.objects.filter(patient__isnull=False, discharge_condition__isnull=False).count()
	completed_discharge = InpatientDischargeSummary.objects.filter(patient__isnull=False, discharge_condition='Completed Treatment').count()
	discharge_chart["data"].append({"label": "Completed Treatment", "value": completed_discharge})
	incomplete_discharge = InpatientDischargeSummary.objects.filter(patient__isnull=False, discharge_condition='Treatment Not Completed').count()
	discharge_chart["data"].append({"label": "Not Completed Treatment", "value": incomplete_discharge})
	dead_discharge = InpatientDischargeSummary.objects.filter(patient__isnull=False, discharge_condition='Died').count()
	discharge_chart["data"].append({"label": "Died", "value": dead_discharge})

	taken_medication = InpatientMedication.objects.filter(stay_duration__isnull=False).values('stay_duration__id').distinct().count()
	used_service_chart["data"].append({"label": "Taken Medication", "value": taken_medication})

	taken_lab_test = InpatientLabOrder.objects.filter(stay_duration__isnull=False).values('stay_duration__id').distinct().count()
	used_service_chart["data"].append({"label": "Taken Lab Test", "value": taken_lab_test})

	#rad_test = OutpatientRadiologyResult.objects.filter(visit__isnull=False).values('visit__id').distinct().count()
	taken_rad_test = 2
	used_service_chart["data"].append({"label": "Taken Rad Test", "value": taken_rad_test})

	ps = PatientPaymentStatus.objects.first()

	payment_statuses = ['Insurance','Free','Discount','Default']

	payment_status_chart["data"].append({"label": 'Insurance', "value": ps.insurancePatientAmount})
	payment_status_chart["data"].append({"label": 'Free', "value": ps.freePatientAmount})
	payment_status_chart["data"].append({"label": 'Discount', "value": ps.discountPatientAmount})
	payment_status_chart["data"].append({"label": 'Default', "value": ps.defaultPatientAmount})
	print('dksksksssssssssssss:  sss: ', ps.insurancePatientAmount)
	building_list = HospitalUnit.objects.all()
	ward_list = Ward.objects.all()

	service_labels = []
	service_numbers = []
	for service in Service.objects.all():
		service_bill = ServiceBillDetail.objects.filter(service=service)
		service_labels.append(str(service))

		if service_bill:
			service_numbers.append(service_bill.count())
			used_service_chart["data"].append({"label": str(service), "value": str(service_bill.count())})
		else:
			service_numbers.append(0)
			used_service_chart["data"].append({"label": str(service), "value": 0})

	service_zip =zip(service_labels,service_numbers)

	age = []
	for i in range(1,120):
		age.append(i)
	#for age in age:
	#	print(age,'\n')

	age_array = age

	bed_list = Bed.objects.all()
	sex = ['MALE','FEMALE']

	"""
	building_list = []
	building_revenue = []
	for b in HospitalUnit.objects.all():
		building_drugs = InpatientMedication.objects.filter(stay_duration__room__ward__hospital_unit=b)
		drug_sum = 0
		if building_drugs:
			for d in building_drugs:
				price = DrugPrice.objects.get(drug=d.drug_prescription.drug,active='active')
				drug_sum = drug_sum + price.selling_price
		room_sum = 0
		room_stays = InpatientRoomBillDetail.objects.filter(room__ward__hospital_unit=b)
		if room_stays:
			for d in room_stays:
				price = RoomPrice.objects.filter(room=d.room).last()
				room_sum = room_sum + price.room_price

		building_list.append(b)
		building_revenue.append(drug_sum + room_sum)

	building_revenue_zip = zip(building_list,building_revenue)

	drug_list3 = []
	drug_revenue = []
	for d in Dosage.objects.all():
		building_drugs = InpatientMedication.objects.filter(drug_prescription__drug=d)
		drug_sum = 0
		if building_drugs:
			for b in building_drugs:
				price = DrugPrice.objects.get(drug=b.drug_prescription.drug,active='active')
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

	admission_chart = FusionCharts("pie2d", "admission_chart", "500", "300", "admission_pie_container", "json", admission_chart)
	used_service_chart = FusionCharts("column2d", "used_service_chart", "500", "300", "used_service_bar_container", "json", used_service_chart)
	payment_status_chart = FusionCharts("doughnut2d", "payment_status_chart", "500", "300", "payment_status_pie_container", "json", payment_status_chart)
	discharge_chart = FusionCharts("doughnut2d", "discharge_chart", "1000", "500", "discharge_doughnut_container", "json", discharge_chart)

	context = {'allocated_beds':allocated_beds,
				'unallocated_beds':unallocated_beds,
				'total_beds':Bed.objects.all().count(),
				
				'emergency_admitted':emergency_admitted,
				'opd_admitted':opd_admitted,
				'total_admitted':opd_admitted + 2,
				'admission_chart':admission_chart.render(),

				'average_stay_length':average_stay_length,
				'average_medication':average_medication,
				'average_lab_test':average_lab_test,
				'average_xray_test':average_xray_test,

				'total_discharge':total_discharge,
				'completed_discharge':completed_discharge,
				'incomplete_discharge':incomplete_discharge,
				'dead_discharge':dead_discharge,
				'discharge_chart':discharge_chart.render(),
				
				'taken_medication':taken_medication,
				'taken_lab_test':taken_lab_test,
				'taken_rad_test':taken_rad_test,
				'used_service_chart':used_service_chart.render(),

				'payment_statuses':payment_statuses,
				'ipa':ps.insurancePatientAmount,
				'dpa':ps.discountPatientAmount,
				'fpa':ps.freePatientAmount,
				'dfpa':ps.defaultPatientAmount,
				'payment_status_chart':payment_status_chart.render(),

				'building_list':building_list,
				'ward_list':ward_list,

				'service_zip':service_zip,

				'age_array':age_array,
				'bed_list':bed_list,
				'sex':sex,
				'bed_list':bed_list,
				'bed_zip':bed_zip,

				'total_revenue':total_revenue,
				'drug_revenue_zip':drug_revenue_zip,
				'test_revenue_zip':test_revenue_zip,
				'service_revenue_zip':service_revenue_zip,
	}	
	return render(request, 'inpatient_app/inpatient_report.html',context)

def InpatientReportChart(request):
	return render(request, 'inpatient_app/inpatient_report_chart.html')

class InpatientReportChartData(APIView):
	authentication_classes = []
	permission_classes = []

	def get(self, request, format=None, *args, **kwargs):

		filtered_date = request.GET.get('date','0') or None
		print(filtered_date)
		admission_date = []
		admission = []
		a= []
		b=[]
		stay_duration = PatientStayDuration.objects.filter(patient__isnull=False)
		for duration in stay_duration:
			if duration.admission_date.day in a:
				print('dd')
			else:
				a.append(duration.admission_date.day)
		for a in a:
			s_dur = PatientStayDuration.objects.filter(patient__isnull=False,admission_date__day=a)
			s_dur_date = s_dur.last()
			admission_date.append(s_dur_date.admission_date.date())
			print(s_dur_date.admission_date.date,'ssss')
			admission.append(s_dur.count())
			ward_admission_zip = zip(admission,admission_date)

		emergency_admitted = InpatientAdmissionAssessment.objects.filter(admitted_from='Emergency Department')
		total_admitted = []
		admitted_labels = ["OPD","Emergency"]	
		total_admitted.append(stay_duration.count()- emergency_admitted.count())
		total_admitted.append(emergency_admitted.count())


		count1= 0
		total_stay = 0
		for patient in Patient.objects.all():
			durations = PatientStayDuration.objects.filter(patient=patient,admission_date__range=['2020-01-01','2024-01-01'], leave_date__isnull=False)
			if durations:
				count = 0
				total_stay_length = 0
				for d in durations:
					count = count + 1
					stay_length = d.admission_date.day - d.leave_date.day
					total_stay_length = stay_length + total_stay_length
				patient_stay = total_stay_length / count
				total_stay = total_stay + patient_stay
				count1 = count1 + 1
		average_stay_length = total_stay/count1

		medications = InpatientMedication.objects.filter(patient__isnull=False)
		average_medication = medications.count()/stay_duration.count()

		lab_tests = InpatientLabOrder.objects.filter(patient__isnull=False)
		average_lab_test = lab_tests.count() / stay_duration.count()
		print(average_lab_test,'ll')
		#xray_tests = InpatientLabOrder.objects.filter(patient__isnull=False)
		average_xray_test = average_lab_test

		average_usage_labels = ['Stay Length','Medication Rate','Lab Test Rate','Rad Test Rate']
		average_usage_numbers = []
		average_usage_numbers.append(average_stay_length)
		average_usage_numbers.append(average_medication)
		average_usage_numbers.append(average_lab_test)
		average_usage_numbers.append(average_xray_test)

		taken_medication = InpatientMedication.objects.filter(stay_duration__isnull=False).values('stay_duration__id').distinct().count()
		taken_lab_test = InpatientLabOrder.objects.filter(stay_duration__isnull=False).values('stay_duration__id').distinct().count()
		#rad_test = OutpatientRadiologyResult.objects.filter(visit__isnull=False).values('visit__id').distinct().count()
		taken_rad_test = 2
		service_labels = []
		service_numbers = []
		for service in Service.objects.all():
			service_bill = ServiceBillDetail.objects.filter(service=service)
			service_labels.append(str(service))
			if service_bill:
				service_numbers.append(service_bill.count())
			else:
				service_numbers.append(1)


		total_usage_labels = ['Taken Medication','Taken Lab Test','Taken Rad Test']
		total_usage_numbers = []
		total_usage_numbers.append(taken_medication)
		total_usage_numbers.append(taken_lab_test)
		total_usage_numbers.append(taken_rad_test)
		for label in service_labels:
			total_usage_labels.append(label)
		for number in service_numbers:
			total_usage_numbers.append(number)

		payment_status_labels = ['Insurance','Free','Credit','Default']
		payment_status_numbers = [2,3,1,8]

		data = {'labels':admission_date,
				'numbers':admission,
				'admitted_from_labels':admitted_labels,
				'admitted_from_numbers':total_admitted,

				'average_usage_labels':average_usage_labels,
				'average_usage_numbers':average_usage_numbers,

				'total_usage_labels':total_usage_labels,
				'total_usage_numbers':total_usage_numbers,

				'payment_status_labels':payment_status_labels,
				'payment_status_numbers':payment_status_numbers,

				}
		return Response(data)
		return redirect('inpatient_report_chart')



def InpatientReportChartTwo(request):
	return render(request, 'inpatient_app/inpatient_report_chart_two.html')

class InpatientReportChartDataTwo(APIView):
	authentication_classes = []
	permission_classes = []

	def get(self, request, format=None, *args, **kwargs):

		allocated_beds = Bed.objects.filter(patient__isnull=False).count()
		unallocated_beds = Bed.objects.filter(patient__isnull=True).count()
		all_beds = Bed.objects.all().count()
		room_occupancy_labels = ['Current Patients','Free Beds']
		room_occupancy_numbers = []
		room_occupancy_numbers.append(allocated_beds)
		room_occupancy_numbers.append(unallocated_beds)
		data = {'room_occupancy_labels':room_occupancy_labels,
				'room_occupancy_numbers':room_occupancy_numbers,
				}
		return Response(data)

