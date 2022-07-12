from django.urls import path

from .views import (DeleteEmergencyCase, DeleteEpidemic,
                    DeleteMedicalEmergencyType, EditEmergencyCase,
                    EditEpidemic, EditMedicalEmergencyType,
                    MedicalEmergencyTypes, NewCase, NotificationToContactPerson,
                    RegisterEpidemic, RegisterMedicalEmergencyType,
                    ViewEmergencyCaseList, ViewEpidemicList, FilterCases)

app_name = 'emergency'
urlpatterns = [
    path('epidemic/register', RegisterEpidemic.as_view(), name='register_epidemic'),
    path('epidemic/edit/<int:id>', EditEpidemic.as_view(), name='edit_epidemic'),
    path('epidemic/list', ViewEpidemicList.as_view(), name='epidemic_list'),
    path('epidemic/remove/<int:id>', DeleteEpidemic.as_view(), name='delete_epidemic'),
    path('add-new-type', RegisterMedicalEmergencyType.as_view(), name='add_emg_type'),
    path('edit-emg-type/<int:id>', EditMedicalEmergencyType.as_view(), name='edit_emg_type'),
    path('delete-emg-type/<int:id>', DeleteMedicalEmergencyType.as_view(), name='delete_emg_type'),
    path('list-types', MedicalEmergencyTypes.as_view(), name='list_emg_types'),
    #path('new-case', RegisterNewCase.as_view(), name='new_case'),
    path('new', NewCase.as_view(), name='new_emg_case'),
    path('edit-case/<int:id>', EditEmergencyCase.as_view(), name='edit_case'),
    path('case/remove/<int:id>', DeleteEmergencyCase.as_view(), name='delete_case'),
    path('case-list', ViewEmergencyCaseList.as_view(), name='case_list'),
    path('notify-user/<int:id>', NotificationToContactPerson.as_view(), name='notify_user'),
    path('filter', FilterCases.as_view(), name='filter_cases'),
]
