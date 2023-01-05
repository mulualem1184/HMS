from typing import Dict

from django import template
from lis.models import NormalRange,LaboratoryTest,LaboratoryTestResultType,NormalRange,LaboratoryTestType
from lis.forms import ResultEntryForm,EditSpecimenForm,EditLabTestTypeForm,EditLabTestResultTypeForm
from inpatient_app.models import Bed,WardDischargeSummary,IPDTreatmentPlan,PerformPlan
from core.models import Patient,Resource,PatientResource,PatientConsultation,PatientDemoValues,MedicalCertificate
from billing_app.forms import EditItemForm,EditItemPriceForm
from billing_app.models import Item
from pharmacy_app.forms import EditPrescriptionInfoForm,EditPrescriptionInfoForm2
from core.forms import EditPatientTreatmentForm,EditPatientResourceForm,EditMedicalCertificateForm
from datetime import timedelta
from datetime import datetime
from django import forms

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
    #print('day isssss',day,resource_id)
    resource = Resource.objects.get(id=resource_id)
    result = resource.is_scheduled(day,resource_id)    
    schedule = PatientResource.objects.filter(resource=resource).first()
    #resource.scheduled_resource.filter(start_time__lte=day, end_time__gte=day).exists()
    context.update({'result':result})
    context.update({'schedule':schedule})
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

@register.simple_tag(takes_context=True)
def is_performed(context,day, plan_id):
    plan = IPDTreatmentPlan.objects.get(id=plan_id)

    try:
        performed_plan = PerformPlan.objects.filter().first()
    except Exception as e:
        return ""
    performed = performed_plan.is_performed(day,plan_id)    
    #resource.scheduled_resource.filter(start_time__lte=day, end_time__gte=day).exists()
    print('\n','performed: ',performed,'\n')
    context.update({'performed':performed})
    if performed==True:
        after_date = day + timedelta(hours=12)
        before_date = day - timedelta(hours=12)
        performance = PerformPlan.objects.filter(registered_on__range=[before_date,after_date], plan=plan).last()
        context.update({'performance':performance})
    return ""

@register.simple_tag(takes_context=True)
def return_edit_certificate_form(context, certificate_id):
    certificate = MedicalCertificate.objects.get(id=certificate_id)
    edit_certificate_form = EditMedicalCertificateForm(certificateid=certificate.id)    
    context.update({'edit_certificate_form':edit_certificate_form})
    return ""

@register.simple_tag(takes_context=True)
def return_edit_prescription_form(context, info_id):
    edit_prescription_form = EditPrescriptionInfoForm2(info_id=info_id)    
    context.update({'edit_prescription_form':edit_prescription_form})
    return ""

@register.simple_tag(takes_context=True)
def is_in_date_array(context,day,date_array):
    #print('dateeee: ',date_array, 'day',str(day.month))
    #print('dayDDD: ', date_array)
    day1 = str(day.year) + "-" + str(day.month) + "-" + str(day.day)
    #print(day1)
    if day1 in date_array:
        #print('already')
        is_in_array = True
        context.update({'is_in_array':is_in_array})

    else:
        date_array.append(day1)
        #for d in date_array:
            #print(d,'kdlsdksld')
        is_in_array = False
        context.update({'is_in_array':is_in_array})

    return ""

@register.simple_tag(takes_context=True)
def get_result_form(context,test_id):
    result_entry_form = ResultEntryForm()

    test = LaboratoryTest.objects.get(id=test_id)
    form_fields = {}
    normal_range = {}
    for result_type in LaboratoryTestResultType.objects.filter(test_type=test.test_type,active=True):
        if result_type.input_type == 'NUMBER':
            form_field = forms.FloatField(widget=forms.NumberInput(
                attrs={
                    'min': 1,
                    'class': 'form-control',
                }
            ))
            normal_range = NormalRange.get_range(result_type, 33, 'M') #TO-DO pass patient age and sex
            #normal_range.update({
            #    f'id_{result_type.name}' : normal_range,
            #    })
            form_fields.update({result_type.name : form_field})
        elif result_type.input_type == "CHOICE":
            choice_set = [(x.choice, x.choice) for x in result_type.choice_set.all()]
            form_fields.update({result_type.name : forms.TypedChoiceField(choices=choice_set, widget=forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ))})
        elif result_type.input_type == 'BOOL':
            form_fields.update({result_type.name : forms.BooleanField(required=False, widget=forms.CheckboxInput(
                attrs={
                    'id': 'checkboxbg1'
                }
            ))})
        elif result_type.input_type == 'TEXT':
            form_fields.update({result_type.name : forms.CharField(widget=forms.Input(
                attrs={
                    'class': 'form-control',
                }
            ))})
    result_entry_form.fields.update(form_fields)
    print('test:', test,'\n')
    print('result form:', result_entry_form,'\n')

    context.update({'result_entry_form':result_entry_form})
    return ""

@register.simple_tag(takes_context=True)
def return_edit_specimen_form(context, specimen_id):
    edit_specimen_form = EditSpecimenForm(specimen_id=specimen_id)   
    context.update({'edit_specimen_form':edit_specimen_form})
    return ""

@register.simple_tag(takes_context=True)
def return_edit_test_type_form(context, test_type_id):
    edit_test_type_form = EditLabTestTypeForm(test_type_id=test_type_id)   
    context.update({'edit_test_type_form':edit_test_type_form})
    return ""

@register.simple_tag(takes_context=True)
def return_edit_result_type_form(context, result_type_id):
    edit_result_type_form = EditLabTestResultTypeForm(result_type_id=result_type_id)   
    context.update({'edit_result_type_form':edit_result_type_form})
    return ""


@register.simple_tag(takes_context=True)
def return_edit_item_form(context, item_id):
    edit_item_form = EditItemForm(item_id=item_id)   
    item = Item.objects.get(id=item_id)
    edit_price_form = EditItemPriceForm(price_id=item.price_info.id)   

    context.update({'edit_item_form':edit_item_form},

        )
    context.update(
                    {'edit_price_form':edit_price_form}
        )

    return ""


@register.simple_tag(takes_context=True)
def return_lab_item(context, test_type_id):
    test_type = LaboratoryTestType.objects.get(id=test_type_id)
    lab_item = Item.objects.filter(lab_test=test_type).last()
    context.update({'lab_item':lab_item},
        )

    return ""
