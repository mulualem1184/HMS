from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(PatientAnthropometry)
admin.site.register(PatientHistory)
admin.site.register(MaternalPatient)
admin.site.register(Service)
admin.site.register(ServiceProvider)
admin.site.register(ServiceBuilding)
admin.site.register(ServiceRoom)
admin.site.register(PatientVisit)
admin.site.register(PatientAppointment)
admin.site.register(VisitQueue)
admin.site.register(PatientSymptom)
admin.site.register(ServiceRoomProvider)
admin.site.register(PatientMedicalCondition)
admin.site.register(PatientMedication)
admin.site.register(ServiceTeam)
admin.site.register(OutpatientTeam)
#admin.site.register(PatientVitalSign)
admin.site.register(PatientAllergy)
admin.site.register(PatientHabit)









