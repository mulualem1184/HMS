from core.utils.sms import send_text
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from emg_ps.models import EmergencyCase, Epidemic, MedicalEmergencyType

from .forms import (ContactPersonForm, EmergencyCaseForm, EpidemicForm,
                    MedicalEmergencyTypeForm)


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
        return render(self.request, 'case_list.html', {
            'case_list': case_list,
            'active_link': 'emg',
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