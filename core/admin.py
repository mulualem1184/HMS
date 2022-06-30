from django.contrib import admin
from .models import Patient, TextMessage, PatientVitalSign


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