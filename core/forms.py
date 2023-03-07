from django import forms
from .models import Patient, PatientVitalSign, PatientPaymentStatus, InsuranceDetail,PatientAllergy,PatientClinicalFinding,PatientTreatment,Image,File,PatientParaclinicalFinding,PatientSurgery,PatientBloodGroup,PatientNote,PatientMedicalHistory,PatientSocialHistory,PatientFamilyHistory,PatientOccupation,AdditionalPatientInfo,PersonInfo,Copayer,PatientFamilyMedic,PatientReferrer,Occupation,PatientConsultation,ReviewOfSystems,PatientSurgeryHistory,PhysicalExam,PatientDemoValues,ScheduleStuff,MedicalCertificate,PatientMaterial,PatientCheckin,PatientResource,Recurrence,Resource,PatientDiagnosis,Task,Stock,StockShelf
from dal import autocomplete
from inpatient_app.models import IPDTreatmentPlan
class PatientForm(forms.ModelForm):

    class Meta:
        model = Patient
        widgets = {}
        exclude = []
        


class VitalSignForm(forms.ModelForm):
    class Meta:
        model = PatientVitalSign
        fields = [
            'pulse_rate', 'temperature', 'temperature_unit',
            'systolic_blood_pressure', 'diastolic_blood_pressure', 
            'oxygen_saturation','blood_glucose_level',
            'glucose_level_unit'
        ]
        widgets = {            
            'pulse_rate': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'temperature': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'systolic_blood_pressure': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'diastolic_blood_pressure': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'oxygen_saturation': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'blood_glucose_level': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'glucose_level_unit': forms.Select(attrs={
                'class' : 'form-control select2',
            }),
            'temperature_unit': forms.Select(attrs={
                'class' : 'form-control select2',
            }),

        }

class TemperatureForm(forms.ModelForm):
    class Meta:
        model = PatientVitalSign
        fields = [
            'temperature', 'temperature_unit',
        ]
        widgets = {            
            'temperature': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'temperature_unit': forms.Select(attrs={
                'class' : 'form-control select2',
            }),

        }

class BloodPressureForm(forms.ModelForm):
    class Meta:
        model = PatientVitalSign
        fields = [
            'systolic_blood_pressure', 'diastolic_blood_pressure', 
        ]
        widgets = {            
            'systolic_blood_pressure': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'diastolic_blood_pressure': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),

        }


class GlucoseLevelForm(forms.ModelForm):
    class Meta:
        model = PatientVitalSign
        fields = [
            'blood_glucose_level', 'glucose_level_unit', 
        ]
        widgets = {            
            'blood_glucose_level': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'glucose_level_unit': forms.Select(attrs={
                'class' : 'form-control select2',
            }),

        }

class OxygenSaturationForm(forms.ModelForm):
    class Meta:
        model = PatientVitalSign
        fields = [
            'oxygen_saturation',  
        ]
        widgets = {            
            'oxygen_saturation': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),

        }

class DemoValuesForm(forms.ModelForm):
    class Meta:
        model = PatientDemoValues
        fields = [
            'name','cholestrol', 'HDL', 'LDL',
            'TGO', 'TGP' 
        ]
        widgets = {            
            'name': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'cholestrol': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'HDL': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'LDL': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'TGO': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'TGP': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),

        }

class EditDemoValuesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        patientid = kwargs.pop('patientid')
        patient = Patient.objects.get(id=patientid)
        try:
            demo = PatientDemoValues.objects.get(patient=patient,active=True)
        except:
            demo = PatientDemoValues()

        super(EditDemoValuesForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            if hasattr(demo,f):
                value = getattr(demo,f)
                self.fields[f].initial = value

    class Meta:
        model = PatientDemoValues
        fields = [
            'name','cholestrol', 'HDL', 'LDL',
            'TGO', 'TGP' 
        ]
        widgets = {            
            'name': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'cholestrol': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'HDL': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'LDL': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'TGO': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'TGP': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),

        }

class PatientPaymentStatusForm(forms.ModelForm):
    
    class Meta:
        model = PatientPaymentStatus 
        fields = ['payment_status']
        
        widgets = {
            'payment_status': forms.Select(attrs={
            'class' : 'select2 form-control',

                }),
            }

class InsuranceDetailForm(forms.ModelForm):
    
    class Meta:
        model = InsuranceDetail
        fields = ['name',  'phone_number', 'address']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'phone_number': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'address': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),

            }

class PatientAllergyForm(forms.ModelForm):
    
    class Meta:
        model = PatientAllergy
        fields = ['allergy']
        
        widgets = {
            'allergy': forms.Textarea(attrs={
                'class' : 'form-control forms',
            }),

            }

class PatientClinicalFindingForm(forms.ModelForm):    
    class Meta:
        model = PatientClinicalFinding
        fields = [ 'clinical_finding']
        
        widgets = {
            'clinical_finding': forms.Textarea(attrs={
                'class' : 'form-control forms',
            }),

            }

class PatientParaClinicalFindingForm(forms.ModelForm):    
    class Meta:
        model = PatientParaclinicalFinding
        fields = [ 'note']
        
        widgets = {
            'note': forms.Textarea(attrs={
                'class' : 'form-control forms',
            }),

            }

class PatientTreatmentForm(forms.ModelForm):    
    class Meta:
        model = PatientTreatment
        fields = [ 'treatment', 'detail']
        
        widgets = {
            'treatment': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'detail': forms.Textarea(attrs={
                'class' : 'form-control forms',
            }),

            }

class PatientDiagnosisForm(forms.ModelForm):    
    class Meta:
        model = PatientDiagnosis
        fields = [ 'diagnosis', 'detail']
        
        widgets = {
            'diagnosis': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'detail': forms.Textarea(attrs={
                'class' : 'form-control forms',
            }),

            }

class EditPatientTreatmentForm(forms.ModelForm):    
    def __init__(self, *args, **kwargs):
        planid = kwargs.pop('planid')
        plan = IPDTreatmentPlan.objects.get(id=planid)
        #print('plannnn ',plan.id)
        #print('pspspspsjnjjjjjj',plan.treatment)
        treatment = plan.treatment
        super(EditPatientTreatmentForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            if hasattr(treatment,f):
                value = getattr(treatment,f)
                self.fields[f].initial = value

    class Meta:
        model = PatientTreatment
        fields = [ 'treatment', 'detail']
        
        widgets = {
            'treatment': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'detail': forms.Textarea(attrs={
                'class' : 'form-control forms',
            }),

            }

class ImageForm(forms.ModelForm):    
    class Meta:
        model = Image
        fields = [ 'image']
        
        widgets = {
            'treatment': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'detail': forms.Textarea(attrs={
                'class' : 'form-control forms',
            }),
            }

class FileForm(forms.ModelForm):    
    class Meta:
        model = Image
        fields = [ 'image']
        
        widgets = {
            'treatment': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'detail': forms.Textarea(attrs={
                'class' : 'form-control forms',
            }),
            }

class PatientSurgeryForm(forms.ModelForm):    
    class Meta:
        model = PatientSurgery
        fields = [ 'note']
        
        widgets = {
            'note': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            }

class PatientBloodGroupForm(forms.ModelForm):    
    def __init__(self, *args, **kwargs):
        patientid = kwargs.pop('patientid')
        patient = Patient.objects.get(id=patientid)
        try:
            blood_group = PatientBloodGroup.objects.get(patient=patient, active=True)
        except :
            blood_group = PatientBloodGroup()

        super(PatientBloodGroupForm, self).__init__(*args, **kwargs)
        if blood_group.blood_type:
            self.fields['blood_type'].initial = blood_group.blood_type
        if blood_group.rh_factor:
            self.fields['rh_factor'].initial = blood_group.rh_factor

    class Meta:
        model = PatientBloodGroup
        fields = [ 'blood_type','rh_factor']
        
        widgets = {
            'blood_type': forms.Select(attrs={
                'class' : 'form-control select2',
            }),
            'rh_factor': forms.Select(attrs={
                'class' : 'form-control select2',
            }),
            }


class PatientNoteForm(forms.ModelForm):    
    def __init__(self, *args, **kwargs):
        patientid = kwargs.pop('patientid')
        patient = Patient.objects.get(id=patientid)
        try:
            note = PatientNote.objects.get(patient=patient, active=True)
        except :
            note = PatientNote()
        super(PatientNoteForm, self).__init__(*args, **kwargs)
        if note.note:
            self.fields['note'].initial = note.note

    class Meta:
        model = PatientNote
        fields = [ 'note']
        
        widgets = {
            'note': forms.Textarea(attrs={
                'class' : 'form-control forms',
            }),
            }

class PatientMedicalHistoryForm(forms.ModelForm):    
    def __init__(self, *args, **kwargs):
        patientid = kwargs.pop('patientid')
        patient = Patient.objects.get(id=patientid)
        try:
            medical_history = PatientMedicalHistory.objects.get(patient=patient)
        except Exception as e:
            medical_history = PatientMedicalHistory()

        super(PatientMedicalHistoryForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            if hasattr(medical_history,f):
                value = getattr(medical_history,f)
                self.fields[f].initial = value

            #print(f)

        """
        if medical_history.high_blood_pressure:
            self.fields['high_blood_pressure'].initial = medical_history.high_blood_pressure
        if medical_history.high_blood_pressure:
            self.fields['high_blood_pressure'].initial = medical_history.high_blood_pressure
        if medical_history.high_blood_pressure:
            self.fields['high_blood_pressure'].initial = medical_history.high_blood_pressure
        if medical_history.high_blood_pressure:
            self.fields['high_blood_pressure'].initial = medical_history.high_blood_pressure
        if medical_history.high_blood_pressure:
            self.fields['high_blood_pressure'].initial = medical_history.high_blood_pressure
        if medical_history.high_blood_pressure:
            self.fields['high_blood_pressure'].initial = medical_history.high_blood_pressure
        """
    class Meta:
        model = PatientMedicalHistory
        fields = [ 'high_blood_pressure','high_cholesterol',
                    'vein_trouble','kidney_disease',
                    'thyroid_problems','drug_abuse',
                    'replacement','DVT','pulmonary_embolus',
                    'tuberculosis','nervous_disorder',
                    'sinus','tonsillitis','bleeding_tendencies',
                    'lung_disease','asthma','heart_trouble',
                    'seasonal_allergies','arthiritis','gastrointestinal',
                    'cancer','stroke','diabetes','pneumonia','hepatitis',
                    'osteporosis','other'

        ]
        
        widgets = {
            'gastrointestinal': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'cancer': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'stroke': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'diabetes': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'pneumonia': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'osteporosis': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'other': forms.Textarea(attrs={
                'class' : 'form-control forms',
            }),
            'nervous_disorder': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'sinus': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'tonsillitis': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'bleeding_tendencies': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'lung_disease': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'asthma': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'heart_trouble': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'seasonal_allergies': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'arthiritis': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),

            'high_blood_pressure': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'vein_trouble': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'thyroid_problems': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'high_cholesterol': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'kidney_disease': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'drug_abuse': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'replacement': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'DVT': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'pulmonary_embolus': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'tuberculosis': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'hepatitis': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),

            }

class PatientSocialHistoryForm(forms.ModelForm):    
    def __init__(self, *args, **kwargs):
        patientid = kwargs.pop('patientid')
        patient = Patient.objects.get(id=patientid)
        try:
            social_history = PatientSocialHistory.objects.get(patient=patient)
        except Exception as e:
            social_history = PatientSocialHistory()

        super(PatientSocialHistoryForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            if hasattr(social_history,f):
                value = getattr(social_history,f)
                self.fields[f].initial = value
                #print(f,'\n')

    class Meta:
        model = PatientSocialHistory
        fields = [ 'tobaco_use','alcohol_use',
                    'caffeine_use','drug_use',
                    'sleep','exercise',

        ]
        
        widgets = {
            'alcohol_use': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'tobaco_use': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'caffeine_use': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'drug_use': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'sleep': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'exercise': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),

            }

class PatientFamilyHistoryForm(forms.ModelForm):    
    def __init__(self, *args, **kwargs):
        patientid = kwargs.pop('patientid')
        patient = Patient.objects.get(id=patientid)
        try:
            family_history = PatientFamilyHistory.objects.get(patient=patient)
        except Exception as e:
            family_history = PatientFamilyHistory()

        super(PatientFamilyHistoryForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            if hasattr(family_history,f):
                value = getattr(family_history,f)
                self.fields[f].initial = value
                #print(f,'\n')

    class Meta:
        model = PatientFamilyHistory
        fields = [ 'high_blood_pressure','tuberculosis',
                    'heart_trouble','mental_illness',
                    'cancer','stroke','diabetes',
                    'kidney_trouble','sickle_cell',
                    'epilepsy','other'

        ]
        
        widgets = {
            'high_blood_pressure': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'tuberculosis': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'heart_trouble': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'mental_illness': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'cancer': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'stroke': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'diabetes': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'kidney_trouble': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'sickle_cell': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'epilepsy': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'other': forms.Textarea(attrs={
                'class' : 'form-control forms',
            }),

            }

class PatientOccupationForm(forms.ModelForm):    
    def __init__(self, *args, **kwargs):
        patientid = kwargs.pop('patientid')
        patient = Patient.objects.get(id=patientid)
        try:
            occupation = PatientOccupation.objects.get(patient=patient,active=True)
        except Exception as e:
            occupation = PatientOccupation()

        super(PatientOccupationForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            if hasattr(occupation,f):
                value = getattr(occupation,f)
                self.fields[f].initial = value

    class Meta:
        model = PatientOccupation
        fields = [ 'occupation','company',
        ]
        
        widgets = {
            'occupation': forms.Select(attrs={
                'class' : 'form-control forms',
            }),
            'company': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),

            }

class CreateOccupationForm(forms.ModelForm):    

    class Meta:
        model = Occupation
        fields = [ 'name']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),

            }

class AdditionalPatientInfoForm(forms.ModelForm):    
    def __init__(self, *args, **kwargs):
        patientid = kwargs.pop('patientid')
        patient = Patient.objects.get(id=patientid)
        try:
            info = AdditionalPatientInfo.objects.get(patient=patient,active=True)
        except:
            info = AdditionalPatientInfo()

        super(AdditionalPatientInfoForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            if hasattr(info,f):
                value = getattr(info,f)
                self.fields[f].initial = value

    class Meta:
        model = AdditionalPatientInfo
        fields = [ 'martial_status','spouse_name',
                    'maiden_name','nationality',
                    'place_of_birth','hobby'
        ]
        
        widgets = {
            'martial_status': forms.Select(attrs={
                'class' : 'form-control select2',
            }),
            'spouse_name': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'maiden_name': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'nationality': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'place_of_birth': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'hobby': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),

            }

class PersonInfoForm(forms.ModelForm):    

    class Meta:
        model = PersonInfo
        fields = [ 'first_name','last_name',
                    'title','phone_number',
                    'date_of_birth','sub_city',
                    'wereda','kebele','region',
                    'image','email','account_number',
                    'note'
        ]
        
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'last_name': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'sub_city': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'wereda': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'kebele': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'region': forms.Select(attrs={
                'class' : 'form-control select2',
            }),
            'image': forms.Select(attrs={
                'class' : 'form-control select2',
            }),
            'title': forms.Select(attrs={
                'class' : 'form-control select2',
            }),
            'account_number': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'phone_number': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'date_of_birth': forms.DateInput(attrs={
            'class' : 'form-control forms',
                }),
            'email': forms.TextInput(attrs={
            'class': 'form-control',
        }),

            }


class PatientCheckinForm(forms.ModelForm):    

    class Meta:
        model = PatientCheckin
        fields = [ 'treatment','note','status'
        ]
        
        widgets = {
            'treatment': forms.Select(attrs={
                'class' : 'form-control forms select2',
            }),
            'note': forms.Textarea(attrs={
                'class' : 'form-control forms',
            }),
            'status': forms.Select(attrs={
                'class' : 'form-control select2',
            }),

            }

class EditPatientCheckinForm(forms.ModelForm):    
    def __init__(self, *args, **kwargs):
        checkinid = kwargs.pop('checkinid')
        checkin = PatientCheckin.objects.get(id=checkinid)
        #print('plannnn ',plan.id)
        #print('pspspspsjnjjjjjj',plan.treatment)
        treatment = plan.treatment
        super(EditPatientCheckinForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            if hasattr(treatment,f):
                value = getattr(treatment,f)
                self.fields[f].initial = value

    class Meta:
        model = PatientCheckin
        fields = [ 'treatment','note','status'
        ]
        
        widgets = {
            'treatment': forms.Select(attrs={
                'class' : 'form-control forms select2',
            }),
            'note': forms.Textarea(attrs={
                'class' : 'form-control forms',
            }),
            'status': forms.Select(attrs={
                'class' : 'form-control select2',
            }),

            }


class CreateResourceForm(forms.ModelForm):    

    class Meta:
        model = Resource
        fields = [ 'resource', ]
        
        widgets = {
            'resource': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),

            }

class PatientResourceForm(forms.ModelForm):    

    class Meta:
        model = PatientResource
        fields = [ 'resource','note','reason','category' ]
        
        widgets = {
            'note': forms.Textarea(attrs={
                'class' : 'form-control forms',
            }),
            'category': forms.Select(attrs={
                'class' : 'form-control select2',
            }),
            'reason': forms.Textarea(attrs={
                'class' : 'form-control forms',
            }),
            'resource': forms.Select(attrs={
                'class' : 'form-control select2',
            }),

            }

class TaskForm(forms.ModelForm):    

    class Meta:
        model = Task
        fields = [ 'task' ]
        
        widgets = {
            'task': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),

            }

class EditPatientResourceForm(forms.ModelForm):    
    def __init__(self, *args, **kwargs):
        resource_id = kwargs.pop('resource_id')
        resource = PatientResource.objects.get(id=resource_id)
        #print('plannnn ',resource.id)
        super(EditPatientResourceForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            if hasattr(resource,f):
                value = getattr(resource,f)
                self.fields[f].initial = value

    class Meta:
        model = PatientResource
        fields = [ 'resource','note','reason','category'    ]
        
        widgets = {
            'note': forms.Textarea(attrs={
                'class' : 'form-control forms',
            }),
            'category': forms.Select(attrs={
                'class' : 'form-control select2',
            }),
            'reason': forms.Textarea(attrs={
                'class' : 'form-control forms',
            }),
            'resource': forms.Select(attrs={
                'class' : 'form-control select2',
            }),

            }

"""
class ResourceForm(forms.ModelForm):    

    class Meta:
        model = Resource
        fields = [ 'resource','private' ]
        
        widgets = {
            'resource': forms.Textarea(attrs={
                'class' : 'form-control forms',
            }),
            'category': forms.Select(attrs={
                'class' : 'form-control select2',
            }),
            'reason': forms.Textarea(attrs={
                'class' : 'form-control forms',
            }),
            'resource': forms.Select(attrs={
                'class' : 'form-control select2',
            }),

            }
"""
class ScheduleStuffForm(forms.ModelForm):    

    class Meta:
        model = ScheduleStuff
        fields = [ 'reason','category',
        ]
        
        widgets = {
            'reason': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'category': forms.Select(attrs={
                'class' : 'form-control select2',
            }),

            }

class MedicalCertificateForm(forms.ModelForm):    

    class Meta:
        model = MedicalCertificate
        fields = [ 'reason','certificate_type','remarks'
        ]
        
        widgets = {
            'reason': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'certificate_type': forms.Select(attrs={
                'class' : 'form-control select2',
            }),
            'remarks': forms.Textarea(attrs={
                'class' : 'form-control forms',
            }),

            }

class EditMedicalCertificateForm(forms.ModelForm):    
    def __init__(self, *args, **kwargs):
        certificateid = kwargs.pop('certificateid')
        certificate= MedicalCertificate.objects.get(id=certificateid)
        #print('pcertifnnn ',certificate)
        #print('pspspspsjnjjjjjj',plan.treatment)
        super(EditMedicalCertificateForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            if hasattr(certificate,f):
                value = getattr(certificate,f)
                self.fields[f].initial = value

    class Meta:
        model = MedicalCertificate
        fields = [ 'patient','reason','certificate_type','remarks'
        ]
        
        widgets = {
            'patient': forms.Select(attrs={
                'class' : 'form-control select2',
            }),
            'reason': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'certificate_type': forms.Select(attrs={
                'class' : 'form-control select2',
            }),
            'remarks': forms.Textarea(attrs={
                'class' : 'form-control forms',
            }),

            }

class EditPersonInfoForm(forms.ModelForm):    
    def __init__(self, *args, **kwargs):
        patientid = kwargs.pop('patientid')
        patient = Patient.objects.get(id=patientid)
        try:
            info = PersonInfo.objects.get(patient=patient,active=True)
        except:
            info = PersonInfo()

        super(EditPersonInfoForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            if hasattr(info,f):
                value = getattr(info,f)
                self.fields[f].initial = value

    class Meta:
        model = PersonInfo
        fields = [ 'first_name','last_name',
                    'title','phone_number',
                    'date_of_birth','sub_city',
                    'wereda','kebele','region',
                    'image','email','account_number',
                    'note'
        ]
        
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'last_name': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'sub_city': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'wereda': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'kebele': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'region': forms.Select(attrs={
                'class' : 'form-control select2',
            }),
            'image': forms.Select(attrs={
                'class' : 'form-control select2',
            }),
            'title': forms.Select(attrs={
                'class' : 'form-control select2',
            }),
            'account_number': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'phone_number': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'date_of_birth': forms.DateInput(attrs={
            'class' : 'form-control forms',
                }),
            'email': forms.TextInput(attrs={
            'class': 'form-control',
        }),

            }

class CopayerForm(forms.ModelForm):    
    class Meta:
        model = Copayer
        fields = [ 'tax_handling','person_info',
                    'copayer_type',
        ]
        
        widgets = {
            'copayer_type': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'person_info': forms.Select(attrs={
                'class' : 'form-control select2',
            }),
            'tax_handling': forms.Select(attrs={
                'class' : 'form-control select2',
            }),

            }

class FamilyMedicForm(forms.ModelForm):    
    def __init__(self, *args, **kwargs):
        patientid = kwargs.pop('patientid')
        patient = Patient.objects.get(id=patientid)
        try:
            family_medic = PatientFamilyMedic.objects.get(patient=patient, active=True)
        except:
            family_medic = PatientFamilyMedic()

        super(FamilyMedicForm, self).__init__(*args, **kwargs)
        if family_medic.medic:
            self.fields['medic'].initial = family_medic.medic

    class Meta:
        model = PatientFamilyMedic
        fields = [ 'medic']
        
        widgets = {
            'medic': forms.Select(attrs={
                'class' : 'form-control select2',
                'name':'medic',
                'id':'medic'
            }),

            }

class PatientSurgeryHistoryForm(forms.ModelForm):    
    def __init__(self, *args, **kwargs):
        patientid = kwargs.pop('patientid')
        patient = Patient.objects.get(id=patientid)
        try:
            surgery = PatientSurgeryHistory.objects.get(patient=patient, active=True)
        except:
            surgery = PatientSurgeryHistory()

        super(PatientSurgeryHistoryForm, self).__init__(*args, **kwargs)
        if surgery.surgery_history:
            self.fields['surgery_history'].initial = surgery.surgery_history

    class Meta:
        model = PatientSurgeryHistory
        fields = [ 'surgery_history']
        
        widgets = {
            'surgery_history': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),

            }

class ReferrerForm(forms.ModelForm):    
    class Meta:
        model = PatientReferrer
        fields = [ 'referrer']
        
        widgets = {
            'referrer': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),

            }


class PatientMaterialForm(forms.ModelForm):    
    class Meta:
        model = PatientMaterial
        fields = [ 'material','quantity',                   
        ]
        widgets = {

            'material': forms.Select(attrs={
            'class' : 'forms form-control select2',
                }),
            'quantity': forms.NumberInput(attrs={
            'class' : 'forms form-control',
                }),

            }

class EditPartialConsultationForm(forms.ModelForm):    
    def __init__(self, *args, **kwargs):
        consultation_id = kwargs.pop('consultation_id')
        consultation = PatientConsultation.objects.get(id=consultation_id)
        super(EditPartialConsultationForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            if hasattr(consultation,f):
                value = getattr(consultation,f)
                self.fields[f].initial = value

    class Meta:
        model = PatientConsultation
        fields = [ 'title','condition',                   
        ]
        widgets = {

            'title': forms.TextInput(attrs={
            'class' : 'forms form-control',
                }),
            'condition': forms.TextInput(attrs={
            'class' : 'forms form-control',
                }),

            }

class PartialConsultationForm(forms.ModelForm):    
    class Meta:
        model = PatientConsultation
        fields = [ 'title','condition',                   
        ]
        widgets = {

            'title': forms.TextInput(attrs={
            'class' : 'forms form-control',
                }),
            'condition': forms.TextInput(attrs={
            'class' : 'forms form-control',
                }),

            }
class PatientConsultationForm(forms.ModelForm):    
    class Meta:
        model = PatientConsultation
        fields = [ 'tags','title','condition','compliant',
                    'treatment','clinical_finding','paraclinical_finding',
                    'diagnoses','material','surgery','recommendation'
        ]
        widgets = {

            'treatment': forms.SelectMultiple(attrs={
            'class' : 'form-control select2',
                }),         
            'tags': forms.SelectMultiple(attrs={
            'class' : 'form-control select2',
            'id' : 'tags_id',

                }),         
            'clinical_finding': forms.SelectMultiple(attrs={
            'class' : 'form-control select2',
            'id' : 'clinical_finding_id',
                }),         
            'paraclinical_finding': forms.SelectMultiple(attrs={
            'class' : 'form-control select2',
            'id' : 'para_finding_id',
                }),         
            'compliant': forms.SelectMultiple(attrs={
            'class' : 'form-control select2',
            'id' : 'compliant_id',
                }),         
            'diagnoses': forms.SelectMultiple(attrs={
            'class' : 'form-control select2',
            'id' : 'diagnoses_id',
                }),         
            'material': forms.SelectMultiple(attrs={
            'class' : 'form-control select2',
            'id' : 'material_id',
                }),         
            'surgery': forms.SelectMultiple(attrs={
            'class' : 'form-control select2',
            'id' : 'surgery_id',
                }),         
            'recommendation': forms.SelectMultiple(attrs={
            'class' : 'form-control select2',
            'id' : 'recommendation_id',
                }),         

            }

class EditPatientConsultationForm(forms.ModelForm):    
    def __init__(self, *args, **kwargs):
        consultation_id = kwargs.pop('consultation_id')
        consultation = PatientConsultation.objects.get(id=consultation_id)
        super(EditPatientConsultationForm, self).__init__(*args, **kwargs)
        self.fields['tags'].initial = consultation.tags.all()
        
        """
        for f in self.fields:
            if hasattr(consultation,f):
                #for t in consultation.f.all():
                #    print('wor',t,'\n')
                for d in f.objects.all():
                    print(d,'\n')
                value = getattr(consultation,f)
                print('value: ',value,'\n')
                self.fields[f].initial = value
        """        
    class Meta:
        model = PatientConsultation
        fields = [ 'tags','title','condition','compliant',
                    'treatment','clinical_finding','paraclinical_finding',
                    'diagnoses','material','surgery','recommendation'
        ]
        widgets = {

            'treatment': forms.SelectMultiple(attrs={
            'class' : 'form-control select2',
                }),         
            'tags': forms.SelectMultiple(attrs={
            'class' : 'form-control select2',
            'id' : 'tags_id',

                }),         
            'clinical_finding': forms.SelectMultiple(attrs={
            'class' : 'form-control select2',
            'id' : 'clinical_finding_id',
                }),         
            'paraclinical_finding': forms.SelectMultiple(attrs={
            'class' : 'form-control select2',
            'id' : 'para_finding_id',
                }),         
            'compliant': forms.SelectMultiple(attrs={
            'class' : 'form-control select2',
            'id' : 'compliant_id',
                }),         
            'diagnoses': forms.SelectMultiple(attrs={
            'class' : 'form-control select2',
            'id' : 'diagnoses_id',
                }),         
            'material': forms.SelectMultiple(attrs={
            'class' : 'form-control select2',
            'id' : 'material_id',
                }),         
            'surgery': forms.SelectMultiple(attrs={
            'class' : 'form-control select2',
            'id' : 'surgery_id',
                }),         
            'recommendation': forms.SelectMultiple(attrs={
            'class' : 'form-control select2',
            'id' : 'recommendation_id',
                }),         

            }


class ReviewOfSystemsForm(forms.ModelForm):    

    class Meta:
        model = ReviewOfSystems
        fields = [ 'fatigue','fevers',
                    'headache','weight_loss',
                    'other','chest_pain',
                    'difficulty_breathing','palpitations',
                    'swelling','blurred_vision',
                    'eye_pain','eye_sensetivity',
                    'wheezing','shortness_of_breath',
                    'cough','sleep_apnea',
                    'tremors','dizzy_spers',
                    'numbness', 'abdominal_pain',
                    'joint_pain','neck_pain',
                    'back_pain','excessive_thirst',
                    'too_hot_or_cold','tired',
                    'nausea',
                    'indigestion'

        ]
        
        widgets = {
            'abdominal_pain': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),

            'neck_pain': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'back_pain': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'excessive_thirst': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'too_hot_or_cold': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'tired': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'abdominal_pain': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'indigestion': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'nausea': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),

            'wheezing': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'shortness_of_breath': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'cough': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'sleep_arena': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'tremors': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'dizzy_spers': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'numbness': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'tingling': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'joint_pain': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),

            'fatigue': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'fevers': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'blurred_vision': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),

            'headache': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'weight_loss': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'other': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'chest_pain': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'difficulty_breathing': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'palpitations': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'eye_pain': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'eye_sensetivity': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'swelling': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),

            }


class EditReviewOfSystemsForm(forms.ModelForm):    
    def __init__(self, *args, **kwargs):
        consultation_id = kwargs.pop('consultation_id')
        consultation = PatientConsultation.objects.get(id=consultation_id)
        review = consultation.systems_review
        super(EditReviewOfSystemsForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            if hasattr(review,f):
                value = getattr(review,f)
                self.fields[f].initial = value

    class Meta:
        model = ReviewOfSystems
        fields = [ 'fatigue','fevers',
                    'headache','weight_loss',
                    'other','chest_pain',
                    'difficulty_breathing','palpitations',
                    'swelling','blurred_vision',
                    'eye_pain','eye_sensetivity',
                    'wheezing','shortness_of_breath',
                    'cough','sleep_apnea',
                    'tremors','dizzy_spers',
                    'numbness', 'abdominal_pain',
                    'joint_pain','neck_pain',
                    'back_pain','excessive_thirst',
                    'too_hot_or_cold','tired',
                    'nausea',
                    'indigestion'

        ]
        
        widgets = {
            'abdominal_pain': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),

            'neck_pain': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'back_pain': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'excessive_thirst': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'too_hot_or_cold': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'tired': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'abdominal_pain': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'indigestion': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'nausea': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),

            'wheezing': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'shortness_of_breath': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'cough': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'sleep_arena': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'tremors': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'dizzy_spers': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'numbness': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'tingling': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'joint_pain': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),

            'fatigue': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'fevers': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'blurred_vision': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),

            'headache': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'weight_loss': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'other': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'chest_pain': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'difficulty_breathing': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'palpitations': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'eye_pain': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'eye_sensetivity': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'swelling': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),

            }

class PhysicalExamForm(forms.ModelForm):    
    class Meta:
        model = PhysicalExam
        fields = [ 'general','head',
                    'eyes','ears',
                    'nose','mouth_and_throat',
                    'neck','breasts',
                    'gastrointestinal','genitourinary',
                    'neurologic','psyhiatric',
        ]
        
        widgets = {
            'general': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'head': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'eyes': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'ears': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'nose': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'mouth_and_throat': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'neck': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'breasts': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'gastrointestinal': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'genitourinary': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'neurologic': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),

            'psyhiatric': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),

            }

class EditPhysicalExamForm(forms.ModelForm):    
    def __init__(self, *args, **kwargs):
        consultation_id = kwargs.pop('consultation_id')
        consultation = PatientConsultation.objects.get(id=consultation_id)
        physical_exam = consultation.physical_exam
        super(EditPhysicalExamForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            if hasattr(physical_exam,f):
                value = getattr(physical_exam,f)
                self.fields[f].initial = value

    class Meta:
        model = PhysicalExam
        fields = [ 'general','head',
                    'eyes','ears',
                    'nose','mouth_and_throat',
                    'neck','breasts',
                    'gastrointestinal','genitourinary',
                    'neurologic','psyhiatric',
        ]
        
        widgets = {
            'general': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'head': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'eyes': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'ears': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'nose': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'mouth_and_throat': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'neck': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'breasts': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'gastrointestinal': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'genitourinary': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),
            'neurologic': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),

            'psyhiatric': forms.TextInput(attrs={
                'class' : 'form-control forms',
            }),

            }



class EditVitalSignForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        consultation_id = kwargs.pop('consultation_id')
        consultation = PatientConsultation.objects.get(id=consultation_id)
        vital_sign = consultation.vital_sign
        super(EditVitalSignForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            if hasattr(vital_sign,f):
                value = getattr(vital_sign,f)
                self.fields[f].initial = value

    class Meta:
        model = PatientVitalSign
        fields = [
            'pulse_rate', 'temperature', 'temperature_unit',
            'systolic_blood_pressure', 'diastolic_blood_pressure', 
            'oxygen_saturation','blood_glucose_level',
            'glucose_level_unit'
        ]
        widgets = {            
            'pulse_rate': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'temperature': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'systolic_blood_pressure': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'diastolic_blood_pressure': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'oxygen_saturation': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'blood_glucose_level': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'glucose_level_unit': forms.Select(attrs={
                'class' : 'form-control select2',
            }),
            'temperature_unit': forms.Select(attrs={
                'class' : 'form-control select2',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': '',
            })

        }

class RecurrenceForm(forms.ModelForm):

    class Meta:
        model = Recurrence
        fields = [
            'days', 'daily_choices', 'daily',
            'weekly', 'monthly','yearly','recurrence_threshold','recurrence_amount',
            'monthly_day','every_int','yearly_choices',
            'hourly_range'
        ]
        widgets = {            
            'hourly_range': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),

            'recurrence_amount': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'recurrence_threshold': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'monthly_day': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'every_int': forms.NumberInput(attrs={
                'class' : 'form-control forms',
            }),
            'yearly_choices': forms.Select(attrs={
                'class' : 'form-control select2',
            }),

            'days': forms.SelectMultiple(attrs={
            'class' : 'form-control select2',
            'id' : 'days_id',

                }),         
            'daily_choices': forms.Select(attrs={
                'class' : 'form-control select2',
            }),
            'daily': forms.CheckboxInput(attrs={
                'class': '',
            }),
            'weekly': forms.CheckboxInput(attrs={
                'class': '',
            }),
            'monthly': forms.CheckboxInput(attrs={
                'class': '',
            }),
            'yearly': forms.CheckboxInput(attrs={
                'class': '',
            })

        }



class CreateStockForm(forms.ModelForm):    
    class Meta:
        model = Stock
        fields = [ 'stock_type','name',                   
        ]
        widgets = {

            'stock_type': forms.Select(attrs={
            'class' : 'forms form-control select2',
                }),
            'name': forms.TextInput(attrs={
            'class' : 'forms form-control',
                }),
            }

class CreateStockShelfForm(forms.ModelForm):    
    class Meta:
        model = StockShelf
        fields = [ 'stock','name',   ]
        widgets = {

            'stock': forms.Select(attrs={
            'class' : 'forms form-control select2',
                }),
            'name': forms.TextInput(attrs={
            'class' : 'forms form-control',
                }),
            }
