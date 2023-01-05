from django.contrib import admin

from .models import *
# Register your models here.

admin.site.register(Ward)
admin.site.register(BedCategory)
admin.site.register(Bed)
#admin.site.register(Nurse)
admin.site.register(BedPatientAllocation)
#admin.site.register(NursePatient)
admin.site.register(HospitalUnit)
admin.site.register(RoomPrice)
admin.site.register(WardTeam)
admin.site.register(InpatientTeam)
admin.site.register(WardTeamBed)
admin.site.register(ServiceProviderBed)

admin.site.register(InpatientReason)
admin.site.register(InpatientCarePlan)
admin.site.register(InpatientAdmissionAssessment)

admin.site.register(WardNurseTeam)
admin.site.register(BedReleaseDate)
admin.site.register(AdmissionPriorityLevel)
admin.site.register(PatientStayDurationPrediction)
admin.site.register(WardStayDuration)
admin.site.register(WardDischargeSummary)
admin.site.register(IPDTreatmentPlan)
admin.site.register(PerformPlan)
admin.site.register(VitalSignPlan)

