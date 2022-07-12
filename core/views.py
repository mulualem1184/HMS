from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth import authenticate, login, logout
from core.models import Patient


class IndexView(View):

    def get(self, *args, **kwargs):
        if self.request.user.is_anonymous:
            return redirect('core:login')
        return render(self.request, 'core/index.html')


class LoginView(View):
    
    def get(self, *args, **kwargs):
        return render(self.request, 'core/login.html')

    def post(self, *args, **kwargs):
        email = self.request.POST.get('email')
        password = self.request.POST.get('password')
        user = authenticate(email=email, password=password)
        if user:
            login(self.request, user)
            messages.success(self.request, f'Welcome, {user.full_name}')
            print(user.employee.designation,'\n')
            if user.employee.designation.name == 'Doctor':
                return redirect('patient_list_for_doctor')
            elif user.employee.designation.name == 'Nurse':
                return redirect('patient_list_for_nurse')
            elif user.employee.designation.name == 'Cashier':
                return redirect('visiting_card_list')
            elif user.employee.designation.name == 'Inpatient Triage':
                return redirect('patient_list')
            elif user.employee.designation.name == 'Outpatient Triage':
                return redirect('outpatient_triage_form')

            elif user.employee.designation.name == 'Nurse Head':
                return redirect('nurse_team_list')
            elif user.employee.designation.name == 'Doctor Head':
                return redirect('ward_team_list')

                #return redirect('core:index')
        messages.error(self.request, 'Wrong email or password')
        return render(self.request, 'core/login.html', {
            'login_error': True,
        })


class LogoutView(View):

    def get(self, *args, **kwargs):
        logout(self.request)
        return redirect('core:login')


class PatientHistory(View):

    def get(self, *args, **kwargs):
        return render(self.request, 'core/pinfo.html', {
            'patient': Patient.objects.first()
        })