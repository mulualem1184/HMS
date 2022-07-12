from core.forms import VitalSignForm
from core.utils.sms import send_text
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.utils import timezone

from emg_ps.models import (ChiefComplaint, EmergencyCase, Epidemic, MedicalEmergencyType,
                           PatientReferralLocation)

from .forms import (ContactPersonForm, EmergencyCaseForm, EpidemicForm, FilterCaseForm,
                    MedicalEmergencyTypeForm)
from .utils import Fieldset



class RegisterEpidemic(View):

    def get(self, *args, **kwargs):
        return render(self.request, 'register_epidemic.html', {
            'epidemic_form': EpidemicForm(),
            'active_link': 'emg'
        })

    def post(self, *args, **kwargs):
        form = EpidemicForm(self.request.POST)
        if form.is_valid():
            form.save()
            messages.success(self.request, "Epidemic Registered successfully.")
            return redirect('emergency:register_epidemic')
        else:
            messages.error(self.request, 'Error saving new epidemic. check your inputs')
            return render(self.request, 'register_epidemic.html', {
                'epidemic_form': form,
                'active_link': 'emg',
            })


class EditEpidemic(View):

    def get(self, *args, **kwargs):
        id = kwargs['id']
        epidemic = get_object_or_404(Epidemic, id=id)
        return render(self.request, 'edit_epidemic.html', {
            'epidemic_form': EpidemicForm(instance=epidemic),
            'active_link': 'emg',
        })

    def post(self, *args, **kwargs):
        id = kwargs['id']
        epidemic = get_object_or_404(Epidemic, id=id)
        form = EpidemicForm(instance=epidemic, data=self.request.POST)
        if form.is_valid():
            form.save()
            messages.success(self.request, "Epidemic edited successfully.")
            return redirect('emergency:epidemic_list')
        else:
            messages.error(self.request, 'Error updating info. check your input values')
            return render(self.request, 'edit_epidemic.html', {
                'epidemic_form': form,
                'active_link': 'emg'
            })

    
class DeleteEpidemic(View):

    def get(self, id, *args, **kwargs):
        ep = get_object_or_404(Epidemic, id=id)
        messages.success(self.request, 'Item Deleted')
        return redirect('emergency:epidemic_list')


class ViewEpidemicList(View):

    def get(self, *args, **kwargs):
        epid_list = Epidemic.objects.all()
        return render(self.request, 'epidemic_list.html', {
            'epid_list': epid_list,
            'active_link': 'emg',
        })


class RegisterMedicalEmergencyType(View):

    def get(self, *args, **kwargs):
        emg_form = MedicalEmergencyTypeForm()
        return render(self.request, 'add_emg_type.html', {
            'emg_form': emg_form,
            'active_link': 'emg'
        })

    def post(self, *args, **kwargs):
        emg_form = MedicalEmergencyTypeForm(self.request.POST)
        if emg_form.is_valid():
            emg_form.save()
            messages.success(self.request, 'Information added.')
            return redirect('emergency:add_emg_type')
        else:
            messages.error(self.request, 'Error while saving info')
            messages.error(self.request, 'HINT: check if emergency type with same name already exists')
            return render(self.request, 'add_emg_type.html', {
                'emg_form': emg_form
            })


class EditMedicalEmergencyType(View):

    def get(self, *args, **kwargs):
        emg_type = get_object_or_404(MedicalEmergencyType, id=kwargs['id'])
        emg_form = MedicalEmergencyTypeForm(instance=emg_type)
        return render(self.request, 'edit_emg_type.html', {
            'emg_form': emg_form,
            'active_link': 'emg'
        })

    def post(self, *args, **kwargs):
        emg_type = get_object_or_404(MedicalEmergencyType, id=kwargs['id'])
        emg_form = MedicalEmergencyTypeForm(instance=emg_type, data=self.request.POST)
        if emg_form.is_valid():
            emg_form.save()
            messages.success(self.request, 'Information Edited.')
            return redirect('emergency:list_emg_types')
        else:
            messages.error(self.request, 'Error while editing info')
            messages.error(self.request, 'HINT: check if emergency type with same name already exists')
            return render(self.request, 'edit_emg_type.html', {
                'emg_form': emg_form
            })


class DeleteMedicalEmergencyType(View):

    def get(self, *args, **kwargs):
        id = kwargs.get('id')
        ob = get_object_or_404(MedicalEmergencyType, id=id)
        ob.delete()
        messages.success(self.request, "Item deleted successfully.")
        return redirect('emergency:list_emg_types')


class MedicalEmergencyTypes(View):
    
    def get(self, *args, **kwargs):
        emg_types = MedicalEmergencyType.objects.all()
        return render(self.request, 'emergency_types_list.html', {
            'emergency_types': emg_types,
            'active_link': 'emg',
        })


class NewCase(View):

    def get(self, *args, **kwargs):
        from .forms import (
            contact_person_fieldset, patient_info_fieldset,
             triage_color_fieldset, other_fieldset,
             triage_stat_fieldset
        )
        contact_person_form = ContactPersonForm()
        new_case_form = EmergencyCaseForm()
        referral_locations = PatientReferralLocation.objects.all()
        chief_complaints = ChiefComplaint.objects.all()
        vitalsign_form = VitalSignForm()
        latest_cases = list(reversed(EmergencyCase.objects.filter(active=True)))[:5]
        tot_refs = EmergencyCase.objects.exclude(referred_from__name='').count()
        dead_patients = EmergencyCase.objects.filter(triage_color='BLACK').count()
        return render(self.request, 'new_case.html', {
            'contact_person_form': contact_person_form,
            'new_case_form': new_case_form,
            'vitalsign_form': vitalsign_form,
            'ref_locations': referral_locations,
            'cc_list': chief_complaints,
            'triage_color_fieldset': triage_color_fieldset,
            'other_fieldset': other_fieldset,
            'triage_stat_fieldset': triage_stat_fieldset,
            'patient_info_fieldset': patient_info_fieldset,
            'contact_person_fieldset': contact_person_fieldset,
            'fieldsets': [
                patient_info_fieldset,
                contact_person_fieldset,
            ],
            'latest_cases': latest_cases,
            'total_number': EmergencyCase.objects.filter(active=True).count(),
            'tot_refs': tot_refs,
            'dead_patients': dead_patients,
            'active_link': 'emg',
        })

    def post(self, *args, **kwargs):
        contact_person_form = ContactPersonForm(data=self.request.POST)
        new_case_form = EmergencyCaseForm(data=self.request.POST)
        vital_sign_form = VitalSignForm(data=self.request.POST)
        if new_case_form.is_valid():
            contact_person = contact_person_form.save()
            vital_sign = vital_sign_form.save()
            new_case:EmergencyCase = new_case_form.save(commit=False)
            new_case.contact_person = contact_person
            new_case.vital_sign = vital_sign
            # get referral location
            try:
                referral_location_id = self.request.POST.get('referral_location')
                loc = PatientReferralLocation.objects.get(id=referral_location_id)
                new_case.referred_from = loc
            except: pass
            new_case.save()
            # get list of cc
            cc_list = self.request.POST.getlist('chief_complaint')
            if not cc_list:
                # get other_complaint from request.post
                cc = ChiefComplaint(name=self.request.POST.get('other_complaint', ''))
                cc.save()
                new_case.chief_complaint_set.add(cc)
            else:
                for cc_id in cc_list:
                    try:
                        cc = ChiefComplaint.objects.get(id=cc_id)
                        new_case.chief_complaint_set.add(cc)
                    except: pass
            messages.success(self.request, 'Emergency case saved.')
            return redirect('emergency:new_emg_case')
        else:
            messages.error(self.request, 'Error creating new case.')
            return render(self.request, 'new_emg_case.html', {
                'contact_person_form': contact_person_form,
                'new_case_form': new_case_form,
                'active_link': 'emg'
            })


class FilterCases(View):

    def get(self, *args, **kwargs):
        symptom_id = self.request.GET.get('cc_id')
        cc = None
        try:
            cc = ChiefComplaint.objects.get(id=symptom_id)
            case_list = cc.emergencycase_set.filter(active=True) 
            return render(self.request, 'case_list.html', {
                'case_list': case_list,
                'active_link': 'emg',
            })
        except:
            return redirect('emergency:case_list')

    def post(self, *args, **kwargs):
        filter_form = FilterCaseForm(data=self.request.POST)
        filter_form.is_valid()
        from_date = filter_form.data.get('from_date', '') or '1970-01-01'
        to_date = filter_form.data.get('to_date', '') or str(timezone.now().date())
        case_list = EmergencyCase.objects.filter(active=True)
        triage_color = filter_form.data.get('triage_color', None) or None
        try:
            case_list = case_list.filter(referred_from=filter_form.data['referred_from'])
        except:pass
        case_list = case_list.filter(arrival_date__date__gte=from_date, arrival_date__date__lte=to_date)
        if triage_color not in (0, '0', '', None):
            case_list = case_list.filter(triage_color=triage_color)
        return render(self.request, 'case_list.html', {
            'case_list': case_list,
            'filter_case_form': filter_form,
            'active_link': 'emg',
        })
        

"""
class RegisterNewCase(View):

    def get(self, *args, **kwargs):
        contact_person_form = ContactPersonForm()
        new_case_form = EmergencyCaseForm()
        return render(self.request, 'new_emg_case.html', {
            'contact_person_form': contact_person_form,
            'new_case_form': new_case_form,
            'active_link': 'emg'
        })

    def post(self, *args, **kwargs):
        contact_person_form = ContactPersonForm(self.request.POST)
        new_case_form = EmergencyCaseForm(self.request.POST)
        if new_case_form.is_valid():
            if not contact_person_form.is_valid():
                messages.error(self.request, 'Error creating new case.')
                return render(self.request, 'new_emg_case.html', {
                    'contact_person_form': contact_person_form,
                    'new_case_form': new_case_form,
                    'active_link': 'emg'
                })
            contact_person = contact_person_form.save()
            new_case = new_case_form.save(commit=False)
            new_case.contact_person = contact_person
            new_case.save()
            messages.success(self.request, 'Case information saved successfully')
            return redirect('emergency:new_case') # to-do list-view             
        else:
            messages.error(self.request, 'Error creating new case.')
            return render(self.request, 'new_emg_case.html', {
                'contact_person_form': contact_person_form,
                'new_case_form': new_case_form,
                'active_link': 'emg'
            })
"""

class DeleteEmergencyCase(View):
    
    def get(self, *args, **kwargs):
        id = kwargs['id']
        case = get_object_or_404(EmergencyCase, id=id)
        case.active = False
        case.save()
        return redirect('emergency:case_list')


class ViewEmergencyCaseList(View):
    
    def get(self, *args, **kwargs):
        case_list = EmergencyCase.objects.filter(active=True)
        filter_case_form = FilterCaseForm()
        return render(self.request, 'case_list.html', {
            'case_list': case_list,
            'active_link': 'emg',
            'filter_case_form': filter_case_form,
        })


class NotificationToContactPerson(View):

    def post(self, *args, **kwargs):
        case = get_object_or_404(EmergencyCase, id=kwargs['id'])
        message = self.request.POST.get('message')
        send_text(phone=case.contact_person.phone_number, message=message)
        # get redirect_to url either case-detail/case-list
        redirect_to = self.request.GET.get('next', 'emergency:case_list')
        messages.info(self.request, 'Message queued to be sent')
        return redirect(redirect_to)


class EditEmergencyCase(View):

    def get(self, *args, **kwargs):
        id = kwargs['id']
        case = get_object_or_404(EmergencyCase, id=id)
        case_form = EmergencyCaseForm(instance=case)
        contact_person_form = ContactPersonForm(instance=case.contact_person)
        return render(self.request, 'edit_emergency_case.html', {
            'edit_case_form': case_form,
            'contact_person_form': contact_person_form,
            'active_link': 'emg',
        })


    def post(self, *args, **kwargs):
        id = kwargs['id']
        case = get_object_or_404(EmergencyCase, id=id)
        case_form = EmergencyCaseForm(instance=case, data=self.request.POST)
        contact_person_form = ContactPersonForm(instance=case.contact_person, data=self.request.POST)
        if not case_form.is_valid() or not contact_person_form.is_valid():
            messages.error(self.request, "Error while editing Emergency case")
            return render(self.request, 'edit_emergency_case.html', {
                'edit_case_form': case_form,
                'contact_person_form': contact_person_form,
                'active_link': 'emg',
            })
        else:
            case_form.save()
            contact_person_form.save()
            messages.success(self.request, "Case info edited successfully")
            return redirect('emergency:edit_case', id)