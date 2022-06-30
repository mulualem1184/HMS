from core.views import IndexView, LoginView
from django.urls import path


app_name = 'core'

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('', IndexView.as_view(), name='index'),
]