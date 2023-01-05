from django.urls import path

from core.views import IndexView, LoginView, LogoutView, PatientHistory, PatientVisitDetail, PatientHistory2,PatientDashboard,AddAllergy,EditAllergy,DeleteAllergy,AddClinicalFinding,EditClinicalFinding,DeleteClinicalFinding,AddTreatment,EditTreatment,DeleteTreatment,RemoveTreatmentImage,AddPrescription,AddParaclinicalFinding,EditParaclinicalFinding,RemoveFile,AddSurgery,EditSurgery,DeleteSurgery,DeleteParaclinicalFinding,EditPatient,SaveEmergencyContact,EditPatientProcess,CreateOccupation,CreateCopayer,SavePersonInfo,AddPatientConsultation,BedCalendar,AddDemoValue,PatientList,SavePatientConsultation,PatientChartHistory,PatientTimeline,PatientActivities,Activities,AddMedicalCertificate,AddPatientMaterial,Consultations,Checkins,AddCheckin,Resources,EditPatientConsultation,ScheduleResource,EditResourceSchedule,CreateResource,EditMedicalCertificate,AddMedicalAttendance,EditMedicalAttendance,DeleteMedicalCertificate,DeleteMedicalAttendance,DeletePatientConsultation,AddPatientDocument,DeletePatientDocument,DeletePatientImage,Home,AddPatientDiagnosis,DeletePatientMaterial,DeletePrescription,DeletePatientDiagnosis,DeletePatient,LabRequests,AddLabRequest,AddLabCase,SaveTask

app_name = 'core'

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('history/<int:id>', PatientHistory.as_view(), name='patient_history'),
    path('patient_visit_detail/<int:id>', PatientVisitDetail.as_view(), name='patient_visit_detail'),
    path('pinfo', PatientHistory.as_view(), name='patient_info'),
    path('history2/<int:id>/', PatientHistory2.as_view(), name='patient_history2'),
    path('patient_dashboard/<int:patient_id>', PatientDashboard, name='patient_dashboard'),
    path('add_allergy/<int:patient_id>', AddAllergy, name='add_allergy'),
    path('edit_allergy/<int:allergy_id>', EditAllergy, name='edit_allergy'),
    path('delete_allergy/<int:allergy_id>', DeleteAllergy, name='delete_allergy'),

    path('add_clinical_finding/<int:patient_id>', AddClinicalFinding, name='add_clinical_finding'),
    path('edit_clinical_finding/<int:finding_id>', EditClinicalFinding, name='edit_clinical_finding'),
    path('delete_clinical_finding/<int:finding_id>', DeleteClinicalFinding, name='delete_clinical_finding'),

    path('add_treatment/<int:patient_id>', AddTreatment, name='add_treatment'),
    path('edit_treatment/<int:treatment_id>', EditTreatment, name='edit_treatment'),
    path('remove_treatment_image/<int:image_id>/<int:patient_id>', RemoveTreatmentImage, name='remove_treatment_image'),
    path('delete_treatment/<int:treatment_id>', DeleteTreatment, name='delete_treatment'),

    path('add_prescription/<int:patient_id>', AddPrescription, name='add_prescription'),

    path('add_paraclinical_finding/<int:patient_id>', AddParaclinicalFinding, name='add_paraclinical_finding'),
    path('edit_paraclinical_finding/<int:finding_id>', EditParaclinicalFinding, name='edit_paraclinical_finding'),
    path('delete_paraclinical_finding/<int:finding_id>', DeleteParaclinicalFinding, name='delete_paraclinical_finding'),

    path('remove_file/<int:file_id>/<int:patient_id>', RemoveFile, name='remove_file'),

    path('add_surgery/<int:patient_id>', AddSurgery, name='add_surgery'),
    path('edit_surgery/<int:surgery_id>', EditSurgery, name='edit_surgery'),
    path('delete_surgery/<int:surgery_id>', DeleteSurgery, name='delete_surgery'),

    path('edit_patient/<int:patient_id>', EditPatient, name='edit_patient'),
    path('edit_patient_process/<int:patient_id>', EditPatientProcess, name='edit_patient_process'),
 
    path('save_emergency_contact/<int:patient_id>', SaveEmergencyContact, name='save_emergency_contact'),
    path('save_person_info/<int:patient_id>', SavePersonInfo, name='save_person_info'),

    path('create_occupation/<int:patient_id>', CreateOccupation, name='create_occupation'),
    path('create_copayer/<int:patient_id>', CreateCopayer, name='create_copayer'),

    path('add_patient_consultation/<int:patient_id>', AddPatientConsultation, name='add_patient_consultation'),
    path('save_consultation/<int:patient_id>', SavePatientConsultation, name='save_consultation'),
    path('edit_patient_consultation/<int:consultation_id>', EditPatientConsultation, name='edit_patient_consultation'),
    path('delete_patient_consultation/<int:consultation_id>/<str:url_arg>', DeletePatientConsultation, name='delete_patient_consultation'),

    path('add_demo_value/<int:patient_id>', AddDemoValue, name='add_demo_value'),

    path('add_patient_diagnosis/<int:patient_id>', AddPatientDiagnosis, name='add_patient_diagnosis'),

    path('patient_chart_history/<int:patient_id>', PatientChartHistory, name='patient_chart_history'),
    path('patient_timeline/<int:patient_id>', PatientTimeline, name='patient_timeline'),
    path('patient_activites/<int:patient_id>', PatientActivities, name='patient_activites'),
    path('activities/<int:patient_id>', Activities, name='activities'),
    path('home/', Home, name='home'),
    path('save_task/', SaveTask, name='save_task'),
 
    path('checkins/<int:patient_id>', Checkins, name='checkins'),
    path('add_checkin/<int:patient_id>', AddCheckin, name='add_checkin'),

    path('resources/<int:patient_id>', Resources, name='resources'),
    path('schedule_resource/<int:patient_id>', ScheduleResource, name='schedule_resource'),
    path('edit_resource_schedule/<int:schedule_id>', EditResourceSchedule, name='edit_resource_schedule'),

    path('create_resource/', CreateResource, name='create_resource'),

    path('add_patient_document/<int:patient_id>/<str:file_type>/<str:url_arg>', AddPatientDocument, name='add_patient_document'),
    path('delete_patient_document/<int:file_id>', DeletePatientDocument, name='delete_patient_document'),
    path('delete_patient_image/<int:image_id>', DeletePatientImage, name='delete_patient_image'),
 
    path('add_medical_certificate/<int:patient_id>', AddMedicalCertificate, name='add_medical_certificate'),
    path('edit_medical_certificate/<int:certificate_id>', EditMedicalCertificate, name='edit_medical_certificate'),
    path('delete_medical_certificate/<int:certificate_id>', DeleteMedicalCertificate, name='delete_medical_certificate'),

    path('delete_patient/<int:patient_id>', DeletePatient, name='delete_patient'),

    path('add_medical_attendance/<int:patient_id>', AddMedicalAttendance, name='add_medical_attendance'),
    path('edit_medical_attendance/<int:attendance_id>', EditMedicalAttendance, name='edit_medical_attendance'),
    path('delete_medical_attendance/<int:attendance_id>', DeleteMedicalAttendance, name='delete_medical_attendance'),

    path('add_patient_material/<int:patient_id>', AddPatientMaterial, name='add_patient_material'),
    path('delete_patient_material/<int:material_id>', DeletePatientMaterial, name='delete_patient_material'),
    path('delete_prescription/<int:prescription_id>', DeletePrescription, name='delete_prescription'),
    path('delete_patient_diagnosis/<int:diagnosis_id>', DeletePatientDiagnosis, name='delete_patient_diagnosis'),

    path('consultations/<int:patient_id>', Consultations, name='consultations'),
    path('bed_calendar/', BedCalendar, name='bed_calendar'),
    path('patient_list/<str:url_arg>', PatientList, name='patient_list'),

    path('lab_requests/<int:patient_id>', LabRequests, name='lab_requests'),
    path('add_lab_request/<int:patient_id>', AddLabRequest, name='add_lab_request'),
    path('add_lab_case/<int:order_id>', AddLabCase, name='add_lab_case'),

    path('', IndexView.as_view(), name='index'),
]