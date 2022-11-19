from typing import Dict

from django import template
from lis.models import NormalRange
from inpatient_app.models import Bed,WardDischargeSummary,IPDTreatmentPlan
from core.models import Patient,Resource,PatientResource,PatientConsultation,PatientDemoValues

from pharmacy_app.forms import EditPrescriptionInfoForm
from core.forms import EditPatientTreatmentForm,EditPatientResourceForm

register = template.Library()

@register.simple_tag(takes_context=True)
def get_dict_elt(context, dict:Dict, key:str):
    # a template tag that will return str representation of normal range
    try:
        nrange:NormalRange = dict.get(key, None)
        if nrange:
            return f' {nrange.min_value} - {nrange.max_value}  {nrange.m_unit}'
        return 'not available'
    except: 
        return ''

@register.simple_tag(takes_context=True)
def get_something(context,thirty_days_ago, bed_id):
    print('day isssss',thirty_days_ago,bed_id)
    bed = Bed.objects.get(id=bed_id)
    result = bed.is_admitted(thirty_days_ago,bed.id)    
    context.update({'result':result})
    return ""

@register.simple_tag(takes_context=True)
def is_admitted(context, patient_id):
    patient = Patient.objects.get(id=patient_id)
    result = Bed.objects.filter().first().is_inpatient(patient.id)    
    context.update({'result':result})
    return ""

@register.simple_tag(takes_context=True)
def return_info_form(context, plan_id):
    plan = IPDTreatmentPlan.objects.get(id=plan_id)
    print('plan id',plan.id)
    edit_info_form = EditPrescriptionInfoForm(planid=plan_id)    
    context.update({'info_form5':edit_info_form})
    return ""

@register.simple_tag(takes_context=True)
def return_treatment_form(context, plan_id):
    plan = IPDTreatmentPlan.objects.get(id=plan_id)
    print('plan id',plan.id)
    edit_treatment_form = EditPatientTreatmentForm(planid=plan_id)    
    
    context.update({'edit_treatment_form':edit_treatment_form})
    return ""

@register.simple_tag(takes_context=True)
def can_be_discharged(context, patient_id):
    patient = Patient.objects.get(id=patient_id)
    print('patient:', patient,'\n')
    result = WardDischargeSummary.objects.filter().first().has_summary(patient_id)
    print('result:', result,'\n')

    context.update({'can_be_discharged':result})
    return ""

@register.simple_tag(takes_context=True)
def is_scheduled(context,day, resource_id):
    print('day isssss',day,resource_id)
    resource = Resource.objects.get(id=resource_id)
    result = resource.is_scheduled(day,resource_id)    
    context.update({'result':result})
    return ""

@register.simple_tag(takes_context=True)
def return_edit_resource_form(context, resource_id):
    resource = PatientResource.objects.get(id=resource_id)
    print('resource id',resource_id)
    edit_resource_form = EditPatientResourceForm(resource_id=resource.id)    
    context.update({'edit_resource_form':edit_resource_form})
    return ""

@register.simple_tag(takes_context=True)
def return_consultation(context, consultation_id):
    consultation = PatientConsultation.objects.get(id=consultation_id)
    print('consultation',consultation,'\n')
    context.update({'consultation_object':consultation})
    return ""

@register.simple_tag(takes_context=True)
def return_demo_value(context, value_id):
    demo_value = PatientDemoValues.objects.get(id=value_id)
    context.update({'demo_value_object':demo_value})
    return ""
