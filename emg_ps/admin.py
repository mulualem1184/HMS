from django.contrib import admin

from .models import (ChiefComplaint, ContactPerson, EmergencyCase, Epidemic,
                     MedicalEmergencyCategory, MedicalEmergencyType,
                     MedicalSymptom, PatientReferralLocation)

admin.site.register([
    MedicalEmergencyType, MedicalEmergencyCategory, Epidemic,
    MedicalSymptom, EmergencyCase, ContactPerson, PatientReferralLocation,
    ChiefComplaint
])
