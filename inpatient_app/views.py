from django.shortcuts import render
from .models import *
from billing_app.models import * 
from pharmacy_app.models import *
from staff_mgmt.models import Employee

from django.contrib import messages
from .forms import *
from django.shortcuts import redirect

from django.db.models import Sum

from datetime import datetime

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
	if request.method == 'POST':
		hospital_structure_form = HospitalStructureForm(request.POST)
		if hospital_structure_form.is_valid():
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
					bed_model.save()
			messages.success(request,'Successful!')
	context = {'hospital_structure_form': hospital_structure_form, 'bed_form':bed_form}
	return render(request,'inpatient_app/hospital_structure.html',context)


def PatientList(request):
	beds = Bed.objects.filter(patient__isnull=False)
	patients = Patient.objects.all()
	allocated_patients = []
	patient_list = []
	for bed in beds:
		allocated_patients.append(bed.patient)
#		patient_list = [allocated_patients,for bed in beds allocated_patients.append(bed.patient)]

	for patient in patients:
		if patient not in allocated_patients:
			patient_list.append(patient)


	#patient_list = Patient.objects.all()
	
	bed_form = BedForm()
	context = {'patient_list':patient_list}
	return render(request,'inpatient_app/patient_list.html',context)


def AllocatedPatientList(request):
	beds = Bed.objects.filter(patient__isnull=False)
	context = { 'beds':beds}
	return render(request, 'inpatient_app/allocated_patient_list.html', context)


def PatientListForNurse(request):
	print(request.user)
#	service_team = ServiceTeam.objects.get(service_provider__user_profile=request.user)
	ward_team_bed = WardTeamBed.objects.filter(nurse_team__nurse__user_profile=request.user)
	context = {'ward_team_bed':ward_team_bed}
	return render(request,'inpatient_app/patient_list_for_nurse.html',context)
	
def PatientListForDoctor(request):
	print(request.user)
#	service_team = ServiceTeam.objects.get(service_provider__user_profile=request.user)
	ward_team_bed = WardTeamBed.objects.filter(team__ward_service_provider__user_profile=request.user)
	
	context = {'ward_team_bed':ward_team_bed}
	return render(request,'inpatient_app/patient_list_for_doctor.html',context)

def AllocatePatient(request,pk):
	"""
	beds = Bed.objects.all()
	for bed in beds:
		room_price = RoomPrice()
		room_price.room = bed
		room_price.room_price = 100
		room_price.save()
	"""
	patient = Patient.objects.get(id=pk)
	
	unallocated_beds = Bed.objects.filter(patient__isnull=True)
	for b in unallocated_beds:
		print(b)
	bed_form = BedForm()
	bed_form.fields['bed'].queryset = unallocated_beds
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
			stay_duration.save()
			room_bill.save()
			messages.success(request,'Successfuly Allocated!')
			return redirect('patient_list')
		else:
			messages.error(request,'Fill Form!')
	context = {'bed_form':bed_form, 'unallocated_beds':unallocated_beds}
	return render(request,'inpatient_app/allocate_patient.html',context)

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
	stay_duration = PatientStayDuration.objects.get(patient=patient, leave_date__isnull=True)
	prescription_form = InpatientPrescriptionForm()
	if request.method == 'POST':
		prescription_form = InpatientPrescriptionForm(request.POST)
		if prescription_form.is_valid():
			prescription_model = prescription_form.save(commit=False)
			prescription_model.patient = Patient.objects.get(id=patient_id)
			prescription_model.inpatient = 'true'
			print(prescription_model.drug, '\n',prescription_model.patient)

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

	patient_visit = PatientVisit.objects.get(patient=patient, visit_status='Active', payment_status='paid')
	patient_visit.visit_status = 'Ended'

	patient_visit.save()
	patient.save()
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
	
	if request.method == 'POST':
		inpatient_reason_form = InpatientReasonForm(request.POST)
		inpatient_care_plan_form = InpatientCarePlanForm(request.POST)
		if inpatient_reason_form.is_valid():
			inpatient_reason_model = inpatient_reason_form.save(commit=False)
			inpatient_care_plan_model = inpatient_care_plan_form.save(commit=False)
			employee = Employee.objects.get(user_profile=request.user, designation__name='Doctor')
			inpatient_reason_model.service_provider = employee
			inpatient_reason_model.status = 'active'
			inpatient_reason_model.patient = patient

			inpatient_care_plan_model.service_provider = employee
			inpatient_care_plan_model.status = 'active'
			inpatient_care_plan_model.patient = patient
			
			inpatient_care_plan_model.save()
			inpatient_reason_model.save()
			messages.success(request, 'Successful!')
			return redirect('inpatient_admission_assessment_form', patient.id)
			
	context = {'inpatient_reason_form':inpatient_reason_form, 'patient':patient,
				'inpatient_care_plan_form':inpatient_care_plan_form}
	return render(request,'inpatient_app/inpatient_reason_form.html',context)

def InpatientAdmissionAssessmentFormPage(request, patient_id):
	patient = Patient.objects.get(id=patient_id)
	assessment_form = InpatientAssessmentForm()
	
	if request.method == 'POST':
		assessment_form = InpatientAssessmentForm(request.POST)
		if assessment_form.is_valid():
			assessment_model = assessment_form.save(commit=False)
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
	stay_duration = PatientStayDuration.objects.get(patient=patient, leave_date__isnull=True)
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

			chart_model.nurse = Employee.objects.get(user_profile=request.user, designation__name='Nurse')

			chart_model.ward_team_bed = WardTeamBed.objects.get(nurse_team__nurse=chart_model.nurse)
			chart_model.stay_duration = stay_duration
			chart_model.view_status = 'not_seen'
			chart_model.registered_on = datetime.now()
			chart_model.save()
			messages.success(request, ' Successfully Assigned!')
			return redirect('nurse_chart_view', patient.id)
	context = {'progress_chart_form':progress_chart_form, 'stay_duration':stay_duration}
	return render(request, 'inpatient_app/nurse_progress_note.html', context)


def DrugPrescriptionPharmacistFormPage(request, prescription_id):
#	patient = Patient.objects.get(id=patient_id)
#	stay_duration = PatientStayDuration.objects.get(patient=patient, leave_date__isnull=True)

#	patient_medication = InpatientMedication.objects.filter(patient=patient, stay_duration=stay_duration)
	prescription_model = DrugPrescription.objects.get(id=prescription_id)
	pharmacist_form = DrugPrescriptionPharmacistForm()
	if request.method == 'POST':
		pharmacist_form = DrugPrescriptionPharmacistForm(request.POST)
		if pharmacist_form.is_valid():
			prescription_form = pharmacist_form.save(commit=False)
			prescription_model.units_per_take = prescription_form.units_per_take
			prescription_model.frequency = prescription_form.frequency
			prescription_model.frequency_unit = prescription_form.frequency_unit
			prescription_model.duration_amount = prescription_form.duration_amount
			prescription_model.duration_unit = prescription_form.duration_unit

			drug_bill = InpatientDrugBillDetail()

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

			prescription_model.save()
			drug_bill.save()
			messages.success(request, ' Successfully Assigned!')
			return redirect('pharmacist_administration_time_form', prescription_model.id)
	context = {'pharmacist_form':pharmacist_form}
	return render(request, 'inpatient_app/drug_prescription_pharmacist_form.html', context)

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

	prescription_list = DrugPrescription.objects.filter(inpatient='true',frequency__isnull=True)
	context = {'prescription_list':prescription_list}
	return render(request, 'inpatient_app/inpatient_prescription_list.html', context)

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
	patient = Patient.objects.get(id=patient_id)
	progress_note_list = NurseProgressChart.objects.filter(ward_team_bed__bed__patient=patient)[:1]
	for p in progress_note_list:
		print('\n',p,'\n')
	inpatient_reason = InpatientReason.objects.get(patient=patient, status='active')

	care_plan = InpatientCarePlan.objects.get(patient=patient, status='active')
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

	vital_sign = PatientVitalSign.objects.get(patient=patient, active='active')

	doctor_team = WardTeam.objects.get(ward_service_provider__user_profile=request.user)
	instruction_list = InpatientDoctorInstruction.objects.filter(ward_team_bed__team=doctor_team, instruction_status = 'not_done', patient=patient)

#	chart.save()
	
	patient_medication = InpatientMedication.objects.filter(patient=patient)
	administration_time = []
	administration_times = []
	time_gap_array = []
	range_array = []
	for medication in patient_medication:
		print(medication.drug_prescription,'\n')
		medication_time = InpatientAdministrationTime.objects.get(drug_prescription=medication.drug_prescription)
		administration_time.append( medication_time)
		administration_times.append(medication_time.first_time)
		time_gap_array.append(medication_time)
		range_array.append(range(1,medication.drug_prescription.frequency))
		
	frequency = [1,2,3,4]
	for time in administration_times:
		print('yea yea','\n',time,'\n')
	try_zip = zip(patient_medication,time_gap_array,range_array)
	try_zip1 = zip(patient_medication,time_gap_array,range_array)

	medication_zip = zip(patient_medication,time_gap_array, range_array)	

	stay_duration = PatientStayDuration.objects.get(patient=patient, leave_date__isnull=True)
	progress_chart_form = NurseProgressChartForm()
	if request.method == 'POST':
		progress_chart_form = NurseProgressChartForm(request.POST)
		if progress_chart_form.is_valid():
			chart_model = progress_chart_form.save(commit=False)
			chart_model.patient = patient

			chart_model.nurse = Employee.objects.get(user_profile=request.user, designation__name='Doctor')
			chart_model.ward_team_bed = WardTeamBed.objects.get(team__ward_service_provider=chart_model.nurse)
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
	vital_sign = PatientVitalSign.objects.get(patient=patient, active='active')
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

	nurse_team = WardNurseTeam.objects.get(nurse__user_profile=request.user)
	instruction_list = InpatientDoctorInstruction.objects.filter(ward_team_bed__nurse_team=nurse_team, instruction_status = 'not_done', patient=patient)
	intervention_count_array = []
	for instruction in instruction_list:
		intervention_list_array = []
		intervention_list = NurseInstructionCheck.objects.filter(doctor_instruction=instruction)
		for intervention in intervention_list:
			intervention_list_array.append(intervention)
		intervention_count_array.append(len(intervention_list_array))
	instruction_zip = zip(instruction_list, intervention_count_array)

#	chart.save()
	
	patient_medication = InpatientMedication.objects.filter(patient=patient)
	administration_time = []
	administration_times = []
	time_gap_array = []
	range_array = []
	for medication in patient_medication:
#		print(medication.drug_prescription,'\n')
		"""
		#try:
		""" 
		medication_time = InpatientAdministrationTime.objects.get(drug_prescription=medication.drug_prescription)
		administration_time.append( medication_time)
		administration_times.append(medication_time.first_time)
		time_gap_array.append(medication_time)
		range_array.append(range(1,medication.drug_prescription.frequency))
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

	progress_chart_form = NurseProgressChartForm()
	if request.method == 'POST':
		progress_chart_form = NurseProgressChartForm(request.POST)
		if progress_chart_form.is_valid():
			chart_model = progress_chart_form.save(commit=False)
			chart_model.patient = patient

			chart_model.nurse = Employee.objects.get(user_profile=request.user, designation__name='Nurse')
			chart_model.ward_team_bed = WardTeamBed.objects.get(team__ward_service_provider=chart_model.nurse)
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
	patient_medication = InpatientMedication.objects.filter(patient=patient)
	administration_time = []
	administration_times = []
	time_gap_array = []
	range_array = []
	for medication in patient_medication:
		medication_time = InpatientAdministrationTime.objects.get(drug_prescription=medication.drug_prescription)
		administration_time.append( medication_time)
		administration_times.append(medication_time.first_time)
		time_gap_array.append(medication_time)
		range_array.append(range(1,medication.drug_prescription.frequency))

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
	stay_duration = PatientStayDuration.objects.get(patient=patient, leave_date__isnull=True)

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
			instruction_model.ward_team_bed = WardTeamBed.objects.get(team__ward_service_provider=instruction_model.doctor)
			instruction_model.stay_duration = stay_duration
			instruction_model.view_status = 'not_seen'
			instruction_model.instruction_status = 'not_done'
			instruction_model.registered_on = datetime.now()
			instruction_model.save()
			messages.success(request, 'Successful!')
			return redirect('doctor_chart_view', patient.id)

	context = {'instruction_form':instruction_form}	
	return render(request, 'inpatient_app/doctor_instruction_form.html', context)


def DischargeInpatient(request, patient_id):
	patient = Patient.objects.get(id=patient_id)
	patient_bill = InpatientBillRelation.objects.get(patient=patient, is_active='active')	
#	patient_bill.is_active = 'not_active'

	stay_duration = PatientStayDuration.objects.get(patient=patient, leave_date__isnull=True)
	stay_duration.leave_date = datetime.now()

	duration_amount = int(stay_duration.leave_date.day) - int( stay_duration.admission_date.day)
	room_price = RoomPrice.objects.get(room = stay_duration.room)

	room_bill = InpatientRoomBillDetail.objects.get(patient=patient, active='active')
#	room_bill.active = 'not_active'
	room_bill.room_price = room_price.room_price * duration_amount
	try:
		inpatient_reason = InpatientReason.objects.get(patient=patient, status='active')
		inpatient_reason.status ='not_active'	
		inpatient_care_plan = InpatientCarePlan.objects.filter(patient=patient, status='active')
		for care_plan in inpatient_care_plan:
			care_plan.status = 'not_active'
		print('one done','\n')
	except Exception as e:
		print(e) 

	try:
		inpatient_care_plan.save()	
		inpatient_reason.save()
		print('two done')
	except Exception as e:
		print(e)

	patient_bill.save()
	stay_duration.save()
	room_bill.save()
	messages.success(request, 'Successful!')
	return redirect('inpatient_bill_detail', patient.id)

def InstructionListForNurse(request):
	instruction_list = InpatientDoctorInstruction.objects.filter(ward_team_bed__nurse_team__nurse__user_profile=request.user)
	context = {'instruction_list':instruction_list}
	return render(request,'inpatient_app/instruction_list_for_nurse.html',context)


def InpatientBillDetailPage(request, patient_id):
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
	return redirect('allocated_patient_list')


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
