from django.contrib import admin
from .models import *


class LaboratoryTestResultTypeInline(admin.TabularInline):
    model = LaboratoryTestResultType
    extra = 0

class LaboratoryTestInline(admin.StackedInline):
    model = LaboratoryTest
    extra = 0

    inlines = [LaboratoryTestResultTypeInline,]


class LaboratoryTestTypeAdmin(admin.ModelAdmin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    inlines = [LaboratoryTestResultTypeInline]

class LaboratoryTestAdmin(admin.ModelAdmin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_display += ('price', 'paid', 'status')

class OrderAdminPage(admin.ModelAdmin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_display += ('progress', 'total_price', 'no_of_tests', 'is_paid')

    ordering = ['ordered_at']
    inlines = [LaboratoryTestInline]

class TestResultChoiceAdmin(admin.ModelAdmin):

    def init(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "test_result_type":
            kwargs['queryset'] = LaboratoryTestResultType.objects.filter(input_type='CHOICE')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class NormalRangeAdmin(admin.ModelAdmin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_display += ('age_range', 'value_range')


admin.site.site_header = "Laboratory Admin Page"
admin.site.register([LaboratorySection, Specimen, SampleType])
admin.site.register(LaboratoryTestType, LaboratoryTestTypeAdmin)
admin.site.register(LaboratoryTest, LaboratoryTestAdmin)
admin.site.register(Order, OrderAdminPage)
admin.site.register(NormalRange, NormalRangeAdmin)
admin.site.register(TestResultChoice, TestResultChoiceAdmin)
admin.site.register(LaboratoryTestResult)
admin.site.register(LaboratoryTestPrice)
admin.site.register(LaboratoryTestResultType)
admin.site.register(Laboratory)
admin.site.register(LabEmployee)
