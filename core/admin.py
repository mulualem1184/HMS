from django.contrib import admin
from .models import Patient, TextMessage, PatientVitalSign, InsuranceDetail,PatientPaymentStatus,PatientTreatment,Image,File,PatientParaclinicalFinding,PersonInfo,PatientNote,PatientFamilyMedic,PatientBarcode,PatientDemoValues,PatientConsultation,ReviewOfSystems,Compliant,Treatment,Material,Recommendation,ParaclinicalFinding,ClinicalFinding,Diagnoses,PhysicalExam,PatientMaterial,PatientClinicalFinding,PatientCheckin,Resource,PatientResource,Recurrence,Day,PatientImage,PatientFile



class PatientAdmin(admin.ModelAdmin):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_display += ('age', 'sex')


class TextMessageAdmin(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_display += ('time', 'to', 'delivered')

admin.site.register(Patient, PatientAdmin)
admin.site.register(TextMessage, TextMessageAdmin)
admin.site.register([PatientVitalSign, ])
admin.site.register(InsuranceDetail)
admin.site.register(PatientPaymentStatus)
admin.site.register(PatientTreatment)
admin.site.register(Image)
admin.site.register(File)
admin.site.register(PatientParaclinicalFinding)
admin.site.register(PersonInfo)
admin.site.register(PatientNote)
admin.site.register(PatientFamilyMedic)
admin.site.register(PatientBarcode)
admin.site.register(PatientDemoValues)
admin.site.register(PatientConsultation)
admin.site.register(Recommendation)
admin.site.register(Treatment)
admin.site.register(Compliant)
admin.site.register(Material)
admin.site.register(ReviewOfSystems)
admin.site.register(ParaclinicalFinding)
admin.site.register(ClinicalFinding)
admin.site.register(Diagnoses)
admin.site.register(PhysicalExam)
admin.site.register(PatientMaterial)
admin.site.register(PatientClinicalFinding)
admin.site.register(PatientCheckin)
admin.site.register(Resource)
admin.site.register(PatientResource)
admin.site.register(Recurrence)
admin.site.register(Day)
admin.site.register(PatientFile)
admin.site.register(PatientImage)
