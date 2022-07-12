from django.urls import path

from core.views import IndexView, LoginView, LogoutView, PatientHistory

app_name = 'core'

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('history/<int:id>', PatientHistory.as_view(), name='patient_history'),
    path('pinfo', PatientHistory.as_view(), name='patient_info'),
    path('', IndexView.as_view(), name='index'),
]