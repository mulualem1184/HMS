from django.urls import path
#from django.conf.urls import url
from django.conf.urls import *
from . import views
from .views import *

urlpatterns = [

 	path('patient_registration/', views.PatientRegistration, name="patient_registration"),
 	path('hospital_structure_form/', views.HospitalStructure, name="hospital_structure_form"),
 	path('building_list/', views.BuildingList, name="building_list"),
 	path('room_list/<int:pk>/', views.RoomList, name="room_list"),
 	path('edit_room/<int:pk>/', views.EditRoom, name="edit_room"),
 	path('assign_patient/', views.AssignPatient, name="assign_patient"),
 	path('room_queue/<int:pk>/', views.RoomQueue, name="room_queue"),
	path('room_availibility/', views.DisplayRoomAvailibility, name="room_availibility"),
	path('change_queue_order/<int:pk>/<int:room_pk>',ChangeQueueOrder , name="change_queue_order"),
	path('doctor_queue/',DoctorQueue , name="doctor_queue"),
	path('patient_anthropometry/',PatientAnthropometry , name="patient_anthropometry"),
	path('patient_symptom/<int:patient_id>',FillPatientSymptom , name="patient_symptom"),
	path('reassign_room/<int:pk>/<int:room_pk>/',ReassignRoom , name="reassign_room"),
	path('view_patient_symptom/<int:patient_id>/', ViewPatientSymptom , name="view_patient_symptom"),
	path('patient_prescription/<int:patient_id>/<int:patient_visit_id>/<int:room_id>/<int:visit_queue_id>/',PatientPrescription , name="patient_prescription"),
	path('assign_service_provider/',AssignServiceProvider , name="assign_service_provider"),
	path('outpatient_list/', PatientList, name="outpatient_list"),
	path('patient_record/<int:patient_id>/', PatientRecord, name="patient_record"),
	path('patient_medical_condition/<int:patient_id>/', PatientMedicalConditionPage, name="patient_medical_condition"),
	path('patient_medical_condition_form/<int:patient_id>/', PatientMedicalConditionFormPage, name="patient_medical_condition_form"),
	path('vital_sign_form/<int:patient_id>/', VitalSignFormPage, name="vital_sign_form"),

	path('assign_service_team', AssignServiceTeam, name="assign_service_team"),

	path('patient_surgery_history_form/<int:patient_id>/', PatientSurgeryHistoryFormPage, name="patient_surgery_history_form"),
	path('patient_allergy_form/<int:patient_id>/', PatientAllergyFormPage, name="patient_allergy_form"),
	path('patient_habit_form/<int:patient_id>/', PatientHabitFormPage, name="patient_habit_form"),

#	path('/', , name=""),

  
]