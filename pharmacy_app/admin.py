from django.contrib import admin

from .models import *
# Register your models here.

admin.site.register(DrugProfile)
admin.site.register(DrugPrescriptionInfo)

admin.site.register(DiseaseDrugModel)

#admin.site.register(AllergyList)
#admin.site.register(InteractionList)

#admin.site.register(Doctor)

#admin.site.register(Patient)


admin.site.register(MedicalAdministrationRecord)
#admin.site.register(DrugProfile_history)
admin.site.register(DrugInventory)
#admin.site.register(DrugProfile)
admin.site.register(Symptom)
admin.site.register(PathologicalFindings)
admin.site.register(ContraIndication)
admin.site.register(DrugCorelation)
#admin.site.register(SimilarDrugs)
admin.site.register(DrugPrice)
admin.site.register(DrugPrescription)

admin.site.register(Bill)
admin.site.register(BillDetail)

#admin.site.register(MedicalAdministration)
admin.site.register(DrugSupply)
admin.site.register(DrugDispensed)
admin.site.register(ExpiredDrug)
admin.site.register(Route)
admin.site.register(IntakeMode)
admin.site.register(Dosage)
admin.site.register(Batch)
admin.site.register(DrugExpiration)
admin.site.register(SideEffect)
admin.site.register(AgeRange)
admin.site.register(WeightRange)

admin.site.register(RandomRecord)
admin.site.register(InStock)
admin.site.register(InStockShelf)
admin.site.register(InStockSlot)
admin.site.register(InStockSlotDrug)


admin.site.register(Dispensary)

admin.site.register(DispensaryShelf)
admin.site.register(DispensarySlot)
admin.site.register(DispensaryDrug)
admin.site.register(Procurement)
admin.site.register(ProcurementDetail)
admin.site.register(DrugImage)
#admin.site.register(InventoryThreshold)
admin.site.register(DrugAvailabilityStatus)

admin.site.register(DrugRelocationTemp)
admin.site.register(PatientCredit)
admin.site.register(DispensaryPharmacist)
admin.site.register(DispensaryProcurementRequest)
admin.site.register(DrugSupplyToDispensary)


"""
class RouteAndForm(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super(RouteAndForm, self).get_form(request, obj, **kwargs)
        if dosage
        form.base_fields['dosage_form'].queryset = RouteAndForm.objects.filter(dosage_form='Tablet')
        return form
"""
