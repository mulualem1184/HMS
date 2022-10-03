from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_list_or_404, get_object_or_404
from core.models import * 
from outpatient_app.models import TeamSetting
from billing_app.models import PatientStayDuration, InpatientDischargeSummary
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
        try:
            setting = TeamSetting.objects.get(active=True)
        except :
            setting = None
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
                if setting.setting == 'Team':
                    return redirect('nurse_team_list')
                else:
                    return redirect('nurse_list')
            elif user.employee.designation.name == 'Doctor Head':
                return redirect('ward_team_list')
            elif user.employee.designation.name == 'Card Room':
                return redirect('patient_registration')
            elif user.employee.designation.name == 'Radiology':
                return redirect('radiology:order_list')
            elif user.employee.designation.name == 'Pharmacy':
                return redirect('inpatient_prescription_list')
            elif user.employee.designation.name == 'Laboratory':
                return redirect('view-orders')
            elif user.employee.designation.name == 'Admin':
                return redirect('admin_dashboard')
            elif user.employee.designation.name == 'Pharmacy Head':
                return redirect('pharmacy_dashboard')
            elif user.employee.designation.name == 'Laboratory Head':
                return redirect('pharmacy_dashboard')
            elif user.employee.designation.name == 'Medical Director':
                return redirect('drug_request_second_approval')
            elif user.employee.designation.name == 'Stock Management':
                return redirect('request_list_from_stock')
            elif user.employee.designation.name == 'Finance Personnel':
                return redirect('cashier_list')

                

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
            'patient' : get_object_or_404(Patient, id=kwargs['id'])
        })

class PatientHistory2(View):

    def get(self, *args, **kwargs):
        patient = get_object_or_404(Patient, id=kwargs['id'])
        stay_duration = PatientStayDuration.objects.filter(patient=patient).exclude(leave_date__isnull=True)
        summary_array = []
        for duration in stay_duration:
            summary = InpatientDischargeSummary.objects.filter(stay_duration=duration).last()
            summary_array.append(summary)

        stay_duration_zip = zip(stay_duration, summary_array)    
        return render(self.request, 'core/patient_history.html', {
            'stay_duration_zip':stay_duration_zip,            
        })
class PatientVisitDetail(View):

    def get(self, *args, **kwargs):
        patient = get_object_or_404(Patient, id=kwargs['id'])
        """
        lvs = PatientVitalSign.objects.filter(patient=patient).last()
        fam_history = FamilyHistory.objects.filter(patient=patient)
        #appointments = PatientAppointment.objects.all()
        lab_tests = None
        latest_order:Order = Order.objects.filter(patient=patient).last()
        if latest_order:
            lab_tests = latest_order.test_set.all()
        """
        return render(self.request, 'core/patient_visit_detail.html', {
            'patient': patient,
            #'vital_sign': lvs,
            #'fam_history': fam_history,
            #'appts': appointments,
            #'tests': lab_tests,
        })