from django.urls import path
#from django.conf.urls import url
from django.conf.urls import *
from . import views
from .views import *

urlpatterns = [

 	path('hospital_structure/', views.HospitalStructure, name="hospital_structure"),
 	path('patient_list/', views.PatientList, name="patient_list"),
 	path('allocate_patient/<int:pk>/', views.AllocatePatient, name="allocate_patient"),
	path('unallocated_patient/', views.UnallocatedPatient, name="unallocated_patient"),
	path('allocate_nurse/', views.AllocateNurse, name="allocate_nurse"),
	path('assign_inpatient/', views.AssignInpatient, name="assign_inpatient"),
	path('inpatient_prescription/<int:patient_id>', views.InpatientPrescription, name="inpatient_prescription"),
 	path('allocated_patient_list/', views.AllocatedPatientList, name="allocated_patient_list"),
 	path('give_inpatient_service/<int:patient_id>', views.GiveInpatientService, name="give_inpatient_service"),

 	path('inpatient_assignment/<int:patient_id>', views.InpatientAssignment, name="inpatient_assignment"),
#	path('inpatient_prescription/<int:bill_id>', views.GenerateServiceBill, name="generate_service_bill"),
 	path('inpatient_bill_detail/<int:patient_id>', views.InpatientBillDetailPage, name="inpatient_bill_detail"),
 	path('discharge_inpatient/<int:patient_id>', views.DischargeInpatient, name="discharge_inpatient"),
 	path('really_discharge_inpatient/<int:patient_id>', views.ReallyDischargeInpatient, name="really_discharge_inpatient"),
 	path('room_bill_list/<int:patient_id>', views.RoomBillList, name="room_bill_list"),
 	path('room_price_form/', views.RoomPriceFormPage, name="room_price_form"),
 	path('inpatient_room_list/', views.InpatientRoomList, name="inpatient_room_list"),
 	path('change_room_price_form/<int:room_price_id>', views.ChangeRoomPriceFormPage, name="change_room_price_form"),
 	path('bed_stay_duration/<int:bed_id>', views.BedStayDuration, name="bed_stay_duration"),
 	path('duration_bill_detail/<int:duration_id>', views.DurationBillDetail, name="duration_bill_detail"),
 	path('check_current_patient/<int:bed_id>', views.CheckCurrentPatient, name="check_current_patient"),
 	path('change_patient_bed/<int:bed_id>', views.ChangePatientBed, name="change_patient_bed"),
 	path('inpatient_observation_form/<int:patient_id>', views.InpatientObservationFormPage, name="inpatient_observation_form"),
 	path('patient_stay_duration_list/<int:patient_id>', views.PatientStayDurationList, name="patient_stay_duration_list"),
 	path('duration_medication/<int:stay_duration_id>', views.DurationMedication, name="duration_medication"),

 	path('inpatient_reason_form/<int:patient_id>', views.InpatientReasonFormPage, name="inpatient_reason_form"),
 	path('inpatient_admission_assessment_form/<int:patient_id>', views.InpatientAdmissionAssessmentFormPage, name="inpatient_admission_assessment_form"),

 	path('assign_inpatient_to_team/', views.AssignInpatientToTeam, name="assign_inpatient_to_team"),
 	path('assign_nurse_to_team/', views.AssignNurseToTeam, name="assign_nurse_to_team"),
 	path('patient_list_for_nurse/', views.PatientListForNurse, name="patient_list_for_nurse"),
 	path('patient_list_for_doctor/', views.PatientListForDoctor, name="patient_list_for_doctor"),

 	path('nurse_progress_note/<int:patient_id>', views.NurseProgressNote, name="nurse_progress_note"),
 	path('mark_drug_as_administered/<int:prescription_id>', views.MarkDrugAsAdministered, name="mark_drug_as_administered"),

 	path('doctor_instruction_form/<int:patient_id>', views.DoctorInstructionFormPage, name="doctor_instruction_form"),
 	path('doctor_chart_view/<int:patient_id>', views.DoctorChartView, name="doctor_chart_view"),
 	path('last_nurse_progress_note_list/<int:patient_id>', views.LastNurseProgressNoteList, name="last_nurse_progress_note_list"),
 	path('all_progress_note_list/<int:patient_id>', views.AllProgressNoteList, name="all_progress_note_list"),

 	path('nurse_chart_view/<int:patient_id>', views.NurseChartView, name="nurse_chart_view"),

 	path('instruction_list_for_nurse/', views.InstructionListForNurse, name="instruction_list_for_nurse"),
 	path('intervention_list_for_nurse/', views.InterventionListForNurse, name="intervention_list_for_nurse"),

 	path('nurse_instruction_response_form/<int:instruction_id>', views.NurseInstructionResponseFormPage, name="nurse_instruction_response_form"),
 	path('nurse_independent_intervention_form/<int:patient_id>', views.NurseIndependentInterventionFormPage, name="nurse_independent_intervention_form"),
 	path('nurse_evaluation_form/<int:intervention_id>', views.NurseEvaluationFormPage, name="nurse_evaluation_form"),
 	path('nurse_independent_intervention_evaluation_form/<int:intervention_id>', views.NurseIndependentInterventionEvaluationFormPage, name="nurse_independent_intervention_evaluation_form"),

 	path('intervention_detail/<int:intervention_id>', views.InterventionDetail, name="intervention_detail"),
 	path('independent_intervention_detail/<int:intervention_id>', views.IndependentInterventionDetail, name="independent_intervention_detail"),

 	path('mark_intervention_as_done/<int:intervention_id>', views.MarkInterventionAsDone, name="mark_intervention_as_done"),
 	path('mark_instruction_as_done/<int:instruction_id>', views.MarkInstructionAsDone, name="mark_instruction_as_done"),
 	path('mark_instruction_as_done_for_doctor/<int:instruction_id>', views.MarkInstructionAsDoneForDoctor, name="mark_instruction_as_done_for_doctor"),

 	path('intervention_list_for_doctor/<int:instruction_id>', views.InstructionDetail, name="intervention_list_for_doctor"),
 	
 	path('nurse_dashboard', views.NurseDashboard, name="nurse_dashboard"),
 	path('medicine_to_be_administered_list_for_nurse', views.MedicationToBeAdministeredListForNurse, name="medicine_to_be_administered_list_for_nurse"),
 	path('medical_administration_detail/<int:patient_id>', views.MedicalAdministrationDetail, name="medical_administration_detail"),

 	path('drug_prescription_pharmacist_form/<int:prescription_id>', views.DrugPrescriptionPharmacistFormPage, name="drug_prescription_pharmacist_form"),

 	path('pharmacist_administration_time_form/<int:prescription_id>', views.PharmacistAdministrationTimeFormPage, name="pharmacist_administration_time_form"),

 	path('inpatient_prescription_list', views.InpatientPrescriptionList, name="inpatient_prescription_list"),

]