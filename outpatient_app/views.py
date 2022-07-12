from django.shortcuts import render
from .models import *
from core.models import *
from pharmacy_app.models import *
from inpatient_app.models import *
from billing_app.models import *
from django.contrib import messages
from .forms import *
from django.shortcuts import redirect
from django.contrib import messages
from datetime import datetime
# Create your views here.

def PatientRegistration(request):
	"""
	count = 0
	visits = VisitQueue.objects.all()
	for visit in visits:
		if count == 0:
			visit.delete()
			count = count + 1
	"""

	patient_form = PatientRegistrationForm()
	if request.method == 'POST':
		patient_form = PatientRegistrationForm(request.POST)
		if patient_form.is_valid():
			patient_model = patient_form.save()
			messages.success(request, patient_model.first_name + " " + patient_model.last_name + " has been successfully registered!")


	context = {'patient_form':patient_form}
	return render(request,'outpatient_app/patient_registration.html',context)

def OutpatientTriageForm(request):
	allocated_patient_array = []
	patient_list = Patient.objects.exclude(inpatient='yes')
	patient_compliant = OutpatientChiefComplaint.objects.filter(active=True)
	for patient in patient_compliant:
		allocated_patient_array.append(patient.id)
	arrival_form = PatientArrivalForm()
	complaint_form = ChiefComplaintForm()
	vital_sign_form = VitalSignForm()
	complaint_form.fields['patient'].queryset = Patient.objects.exclude(inpatient='yes', id__in=allocated_patient_array)

	if request.method == 'POST':
		arrival_form = PatientArrivalForm(request.POST)
		complaint_form = ChiefComplaintForm(request.POST)
		vital_sign_form = VitalSignForm(request.POST)
		if all([arrival_form.is_valid(), complaint_form.is_valid(), vital_sign_form.is_valid()]):
			arrival_model = arrival_form.save(commit=False)
			complaint_model = complaint_form.save(commit=False)
			vital_sign_model = vital_sign_form.save(commit=False)

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

			vital_sign_model.save()
			complaint_model.save()
			arrival_model.save()

			messages.success(request, 'Success')
			return redirect('assign_visiting_card_form')
	context = {'arrival_form':arrival_form,
				'vital_form':vital_sign_form,
				'complaint_form':complaint_form,
	}
	return render(request,'outpatient_app/outpatient_triage_form.html',context)


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

def DoctorQueue(request):

	try:	
		print(request.user)
		service_team = ServiceTeam.objects.get(service_provider__user_profile=request.user)
		#service_provider = ServiceProvider.objects.get(service_provider__user_profile=request.user)
		room = ServiceRoomProvider.objects.get(service_team=service_team.team)
		print(room.room)
		visit_queue = VisitQueue.objects.filter(visit__service_room=room.room, visit__visit_status='Active').order_by('queue_number')
		for visit in visit_queue:
			print(visit.queue_number,'s')

		context = {'visit_queue':visit_queue, 'room':room}
		return render(request,'outpatient_app/doctor_queue.html',context)
	
	except:
		print('nothih')
		return render(request,'outpatient_app/doctor_queue.html')

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

			patient_queue = VisitQueue.objects.get(id=visit_queue_id)
			queue = VisitQueue.objects.filter(visit__service_room_id=room_id, visit__visit_status='Pending')
			queue_range_array = []
			for  queue in range(patient_queue.queue_number + 1, queue.last().queue_number + 1 ):
				print('\n',queue)
				queue_range_array.append(queue)
			queue_patients = VisitQueue.objects.filter(queue_number__in=queue_range_array, visit__service_room=room)
			for queue in queue_patients:
				queue.queue_number = queue.queue_number - 1
				queue.save()
				print('success 3 ','\n')	
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
	return render(request, 'outpatient_app/patient_prescription.html', context)

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

