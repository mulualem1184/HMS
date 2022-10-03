from django.urls import path

from core.views import IndexView, LoginView, LogoutView, PatientHistory, PatientVisitDetail, PatientHistory2

app_name = 'core'

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('history/<int:id>', PatientHistory.as_view(), name='patient_history'),
    path('patient_visit_detail/<int:id>', PatientVisitDetail.as_view(), name='patient_visit_detail'),
    path('pinfo', PatientHistory.as_view(), name='patient_info'),
    path('history2/<int:id>/', PatientHistory2.as_view(), name='patient_history2'),

    path('', IndexView.as_view(), name='index'),
]