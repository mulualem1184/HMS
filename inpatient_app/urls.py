from django.urls import path
#from django.conf.urls import url
from django.conf.urls import *
from . import views
from .views import *

urlpatterns = [

 	path('hospital_structure/', views.HospitalStructure, name="hospital_structure"),
 	path('treatment_plan_progress/<int:plan_id>', views.TreatmentPlanProgress, name="treatment_plan_progress"),
 	path('temperature_plan_progress/<int:plan_id>', views.TemperaturePlanProgress, name="temperature_plan_progress"),
 	path('blood_pressure_plan_progress/<int:plan_id>', views.BloodPressurePlanProgress, name="blood_pressure_plan_progress"),
 	path('oxygen_saturation_plan_progress/<int:plan_id>', views.OxygenSaturationPlanProgress, name="oxygen_saturation_plan_progress"),
 	path('glucose_level_plan_progress/<int:plan_id>', views.GlucoseLevelPlanProgress, name="glucose_level_plan_progress"),

 	path('whole_ward_view/', views.WholeWardView, name="whole_ward_view"),
 	path('admit_patient_to_ward/<int:bed_id>/<str:value>/', views.AdmitPatientToWard, name="admit_patient_to_ward"),
 	path('edit_ward_admission/<int:bed_id>', views.EditWardAdmission, name="edit_ward_admission"),
 	path('delete_ward_admission/<int:bed_id>', views.DeleteWardAdmission, name="delete_ward_admission"),

 	path('save_treatment_plan/', views.SaveTreatmentPlan, name="save_treatment_plan"),
 	path('save_treatment_plan2/', views.SaveTreatmentPlan2, name="save_treatment_plan2"),
 	path('delete_treatment_plan/<int:plan_id>/', views.DeleteTreatmentPlan, name="delete_treatment_plan"),

 	path('add_patient_temperature/<int:plan_id>', views.AddPatientTemperature, name="add_patient_temperature"),
 	path('add_patient_blood_pressure/<int:plan_id>', views.AddPatientBloodPressure, name="add_patient_blood_pressure"),
 	path('add_patient_oxygen_saturation/<int:plan_id>', views.AddPatientOxygenSaturation, name="add_patient_oxygen_saturation"),
 	path('add_patient_glucose_level/<int:plan_id>', views.AddPatientGlucoseLevel, name="add_patient_glucose_level"),

 	path('edit_treatment_plan/<int:plan_id>', views.EditTreatmentPlan, name="edit_treatment_plan"),
 	path('change_plan_status/<int:plan_id>', views.ChangePlanStatus, name="change_plan_status"),
 	path('treatment_plan_prescription/<int:plan_id>', views.TreatmentPlanPrescription, name="treatment_plan_prescription"),

 	path('ipd_structure/', views.IPDStructure, name="ipd_structure"),
 	path('create_ward/', views.CreateWard, name="create_ward"),
 	path('edit_ward/<int:ward_id>', views.EditWard, name="edit_ward"),
 	path('delelte_ward/<int:ward_id>', views.DeleteWard, name="delete_ward"),

 	path('create_ipd_building/', views.CreateIPDBuilding, name="create_ipd_building"),
 	path('create_ipd_ward/', views.CreateIPDWard, name="create_ipd_ward"),
 	path('create_ipd_bed/', views.CreateIPDBed, name="create_ipd_bed"),
 	path('edit_ipd_building/<int:building_id>', views.EditIPDBuilding, name="edit_ipd_building"),
 	path('delete_ipd_building/<int:building_id>', views.DeleteIPDBuilding, name="delete_ipd_building"),

 	path('edit_ipd_ward/<int:ward_id>', views.EditIPDWard, name="edit_ipd_ward"),
 	path('delete_ipd_ward/<int:ward_id>', views.DeleteIPDRoom, name="delete_ipd_ward"),

 	path('edit_ipd_bed/<int:bed_id>', views.EditIPDBed, name="edit_ipd_bed"),
 	#path('delete_ipd_bed/<int:bed_id>', views.DeleteIPDBed, name="delete_ipd_ward"),

 	path('patient_list/', views.PatientList, name="patient_list"),
 	path('allocate_patient/<int:pk>/', views.AllocatePatient, name="allocate_patient"),
 	path('bed_release_date_form/<int:patient_id>/', views.BedReleaseDateFormPage, name="bed_release_date_form"),

	path('unallocated_patient/', views.UnallocatedPatient, name="unallocated_patient"),
	path('allocate_nurse/', views.AllocateNurse, name="allocate_nurse"),
	path('assign_inpatient/', views.AssignInpatient, name="assign_inpatient"),
	path('inpatient_prescription/<int:patient_id>', views.InpatientPrescription, name="inpatient_prescription"),
 	path('allocated_patient_list/', views.AllocatedPatientList, name="allocated_patient_list"),
 	path('give_inpatient_service/<int:patient_id>', views.GiveInpatientService, name="give_inpatient_service"),

 	path('ward_team_list/', views.WardTeamList, name="ward_team_list"),
 	path('nurse_team_list/', views.NurseTeamList, name="nurse_team_list"),

 	path('assign_nurse_team_to_bed_form/<int:inpatient_team_id>', views.AssignNurseTeamToBedFormPage, name="assign_nurse_team_to_bed_form"),
 	path('assign_doctor_to_bed_form/<int:inpatient_team_id>', views.AssignDoctorToBedFormPage, name="assign_doctor_to_bed_form"),
 	path('assign_doctor_to_team_modal/<int:team_id>', views.AssignDoctorToTeamModal, name="assign_doctor_to_team_modal"),

	path('create_inpatient_team_form/', views.CreateInpatientTeamFormPage, name="create_inpatient_team_form"),
	path('create_nurse_team_form/', views.CreateNurseTeamFormPage, name="create_nurse_team_form"),
	path('assign_nurse_to_team_form/<int:team_id>', views.AssignNurseToTeamFormPage, name="assign_nurse_to_team_form"),

	path('assign_doctor_to_team_form/<int:team_id>', views.AssignDoctorToTeamFormPage, name="assign_doctor_to_team_form"),


 	path('nurse_list/', views.NurseList, name="nurse_list"),
 	path('assign_nurse_to_bed_form/<int:employee_id>', views.AssignNurseToBedFormPage, name="assign_nurse_to_bed_form"),
 	path('assign_nurse_team_to_bed_form/<int:inpatient_id>', views.AssignNurseTeamToBedFormPage, name="assign_nurse_team_to_bed_form"),
 	path('assign_nurse_to_team_modal/<int:team_id>', views.AssignNurseToTeamModal, name="assign_nurse_to_team_modal"),
    path('schedule_nurse/<int:team_id>', ScheduleNurse.as_view(), name='schedule_nurse'),

 	path('doctor_list/', views.DoctorList, name="doctor_list"),
 	path('assign_doctor_to_bed_form2/<int:employee_id>', views.AssignDoctorToBedFormPage2, name="assign_doctor_to_bed_form2"),


 	path('inpatient_assignment/<int:patient_id>', views.InpatientAssignment, name="inpatient_assignment"),
 	path('inpatient_assignment_from_emergency/<int:patient_id>', views.InpatientAssignmentFromEmergency, name="inpatient_assignment_from_emergency"),


#	path('inpatient_prescription/<int:bill_id>', views.GenerateServiceBill, name="generate_service_bill"),
 	path('inpatient_bill_detail/<int:patient_id>', views.InpatientBillDetailPage, name="inpatient_bill_detail"),

 	path('discharge_summary_form/<int:patient_id>', views.DischargeSummaryFormPage, name="discharge_summary_form"),
 
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
 	path('vital_sign_form_modal/<int:patient_id>/<int:role_id>', views.VitalSignFormModalPage, name="vital_sign_form_modal"),

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

	path('inpatient_report/', InpatientReport, name = 'inpatient_report'),

	path('inpatient_report_chart/', InpatientReportChart, name = 'inpatient_report_chart'),
	path('api/inpatient_report_chart_data/data', InpatientReportChartData.as_view(), name='inpatient_report_chart_data'),

	path('inpatient_report_chart_two/', InpatientReportChartTwo, name = 'inpatient_report_chart_two'),
	path('api/inpatient_report_chart_data_two/data', InpatientReportChartDataTwo.as_view()),

]
#https://github.com/mulualem1184/HMS