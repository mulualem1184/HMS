from django.contrib import admin

from .models import (EmergencyCase, Epidemic, MedicalEmergencyCategory,
                     MedicalEmergencyType, MedicalSymptom, ContactPerson)

admin.site.register([
    MedicalEmergencyType, MedicalEmergencyCategory, Epidemic,
    MedicalSymptom, EmergencyCase, ContactPerson
])
