from django.contrib import admin
from .models import *
# Register your models here.
#admin.site.register(OutpatientTeam)
admin.site.register(PatientInsurance)
admin.site.register(InsuranceExcludedService)
admin.site.register(VisitBill)
admin.site.register(VisitBillDetail)
admin.site.register(ServiceBill)
admin.site.register(ServiceBillDetail)
admin.site.register(LabBillDetail)

admin.site.register(InpatientBill)
admin.site.register(InpatientDrugBillDetail)
admin.site.register(InpatientRoomBillDetail)
admin.site.register(InpatientServiceBillDetail)
admin.site.register(InpatientBillRelation)
admin.site.register(VisitingCardPrice)
admin.site.register(PatientStayDuration)
admin.site.register(InpatientObservation)
admin.site.register(NurseProgressChart)
admin.site.register(InpatientDoctorOrder)
admin.site.register(InpatientLabResult)
admin.site.register(InpatientAdministrationTime)
admin.site.register(InpatientMedication)

admin.site.register(InpatientMedicalAdministration)
admin.site.register(InpatientDoctorInstruction)

admin.site.register(NurseEvaluation)
admin.site.register(NurseInstructionCheck)
admin.site.register(NurseIndependentIntervention)

admin.site.register(InpatientDischargeSummary)
admin.site.register(CashierDebt)
admin.site.register(CashierReconcilation)







