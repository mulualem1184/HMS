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
admin.site.register(VisitingCardPrice)
admin.site.register(PatientStayDuration)

admin.site.register(CashierDebt)
admin.site.register(CashierReconcilation)
admin.site.register(Treatment)
admin.site.register(RoomBillDetail)
admin.site.register(DrugBill)







