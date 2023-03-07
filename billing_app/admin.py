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
admin.site.register(Item)
admin.site.register(ItemSaleInfo)
admin.site.register(Invoice)
admin.site.register(Payment)
admin.site.register(ItemPrice)
admin.site.register(ItemCategory)
admin.site.register(InvoiceReconcilation)
admin.site.register(BillableItem)
admin.site.register(ShelfItem)
admin.site.register(TransferRequest)
admin.site.register(ItemTransferInfo)
admin.site.register(ItemRelocationInfo)
admin.site.register(ItemRelocationTemp)
admin.site.register(InventoryThreshold)









