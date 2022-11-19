from django.db import models
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from datetime import datetime as datetime2
#from django.core.validators import 
from staff_mgmt.models import Employee
import barcode                      # additional imports
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File
class Patient(models.Model):
    SEX_CHOICES = [
        ('MALE','MALE'),
        ('FEMALE', 'FEMALE'),
    ]

    TITLE_CHOICES = [
        ('1','Mr.'),
        ('2', 'Ms.'),
        ('3', 'Mrs.'),

    ]

    REGION_CHOICES = [
        ('Addis Ababa','Addis Ababa'),
        ('Tigray','Tigray'),
        ('Afar', 'Afar'),
        ('Amhara', 'Amhara'),
        ('Oromia', 'Oromia'),
        ('Benishangul', 'Benishangul'),
        ('Gambella', 'Gambella'),
        ('SNNPRS', 'SNNPRS'),
        ('Somali', 'Somali'),
        ('Sidama', 'Sidama'),
    ]

    inpatient_status = [
        ('yes','yes'),
        ('no', 'no'),
    ]

    registered_at = models.DateTimeField(auto_now_add=True) # saves datetime when the instance is first created
    first_name = models.CharField(max_length=50, validators=[RegexValidator('^[a-zA-Z]*$', ),])
    last_name = models.CharField(max_length=50,validators=[RegexValidator('^[a-zA-Z]*$', ),])
    grandfather_name = models.CharField(max_length=50,validators=[RegexValidator('^[a-zA-Z]*$', ),],null=True,blank=True)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES)
    title = models.CharField(max_length=10, choices=TITLE_CHOICES,null=True,blank=True)
    dob = models.DateField(null=True,blank=True)
    occupation = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=10)
    email = models.EmailField(max_length=50,null=True, blank=True)
    #address = models.CharField(max_length=300)
    sub_city = models.CharField(max_length=2000, null=True, blank=True) 
    wereda = models.CharField(max_length=2000, null=True, blank=True) 
    kebele = models.CharField(max_length=2000, null=True, blank=True) 
    region = models.CharField(max_length=20, choices=REGION_CHOICES, null=True)
    inpatient = models.CharField(max_length=10, choices=inpatient_status, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    
    @property
    def age(self):
        # returns age from dob
        if self.dob:
            td = datetime.date.today() - self.dob
            return td.days//365

    @property
    def registered_today(self):
        today = datetime2.now()
        rt = Patient.objects.filter(registered_at__day=today.day)
        if rt:
            return rt.count()
        else:
            return 0
"""
class Patient(models.Model):
    SEX_CHOICES = [
        ('MALE','MALE'),
        ('FEMALE', 'FEMALE'),
    ]

    TITLE_CHOICES = [
        ('1','Mr.'),
        ('2', 'Ms.'),
        ('3', 'Mrs.'),

    ]

    REGION_CHOICES = [
        ('Addis Ababa','Addis Ababa'),
        ('Tigray','Tigray'),
        ('Afar', 'Afar'),
        ('Amhara', 'Amhara'),
        ('Oromia', 'Oromia'),
        ('Benishangul', 'Benishangul'),
        ('Gambella', 'Gambella'),
        ('SNNPRS', 'SNNPRS'),
        ('Somali', 'Somali'),
        ('Sidama', 'Sidama'),
    ]

    inpatient_status = [
        ('yes','yes'),
        ('no', 'no'),
    ]

    registered_at = models.DateTimeField(auto_now_add=True) # saves datetime when the instance is first created
    first_name = models.CharField(max_length=50, validators=[RegexValidator('^[a-zA-Z]*$', ),])
    last_name = models.CharField(max_length=50,validators=[RegexValidator('^[a-zA-Z]*$', ),])
    grandfather_name = models.CharField(max_length=50,validators=[RegexValidator('^[a-zA-Z]*$', ),],null=True,blank=True)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES)
    title = models.CharField(max_length=10, choices=TITLE_CHOICES,null=True,blank=True)
    dob = models.DateField(null=True,blank=True)
    occupation = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=10)
    email = models.EmailField(max_length=50,null=True, blank=True)
    #address = models.CharField(max_length=300)
    sub_city = models.CharField(max_length=2000, null=True, blank=True) 
    wereda = models.CharField(max_length=2000, null=True, blank=True) 
    kebele = models.CharField(max_length=2000, null=True, blank=True) 
    region = models.CharField(max_length=20, choices=REGION_CHOICES, null=True)
    inpatient = models.CharField(max_length=10, choices=inpatient_status, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name}"
"""


class Occupation(models.Model):
    name = models.CharField(max_length=200, null=True,blank=True)
    def __str__(self):
        return  str(self.name)

class PatientOccupation(models.Model):
    patient = models.ForeignKey(to=Patient, on_delete=models.CASCADE,null=True,blank=True)
    occupation = models.ForeignKey(to=Occupation, on_delete=models.CASCADE,null=True,blank=True)
    company = models.CharField(max_length=200, null=True,blank=True)

class AdditionalPatientInfo(models.Model):
    MARTIAL_STATUS_CHOICES = [
        (1,'MARRIED'),
        (2, 'DIVORCED'),
        (3, 'SINGLE'),

    ]
    patient = models.ForeignKey(to=Patient, on_delete=models.CASCADE,null=True,blank=True)
    martial_status = models.CharField(max_length=20, choices=MARTIAL_STATUS_CHOICES,null=True,blank=True)
    spouse_name = models.CharField(max_length=200, null=True,blank=True)
    maiden_name = models.CharField(max_length=200, null=True,blank=True)
    nationality = models.CharField(max_length=200, null=True,blank=True)
    place_of_birth = models.CharField(max_length=200, null=True,blank=True)
    hobby = models.CharField(max_length=200, null=True,blank=True)

class TextMessage(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    to = models.CharField(max_length=20)
    delivered = models.BooleanField(default=False)

    def __str__(self):
        return self.to

class HealthHistory(models.Model):

    patient = models.ForeignKey(to=Patient, on_delete=models.CASCADE)
    diabetes = models.BooleanField(default=False)
    high_blood_pressure = models.BooleanField(default=False)
    cholestrol = models.BooleanField(default=False, verbose_name="High Cholestrol")


class FamilyRelation(models.Model):
    RELATION_TYPE = [
        ('MOTHER', 'MOTHER'),
        ('FATHER', 'FATHER'),
        ('CHILDREN', 'CHILDREN'),
        ('BROTHER/SISTER', 'BROTHER/SISTER'),
    ]
    name = models.CharField(max_length=20, choices=RELATION_TYPE, unique=True)

    def str(self):
        return self.name


class CancerType(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def str(self) -> str:
        return self.name


class FamilyCancerHistory(models.Model):
    relation = models.ForeignKey(to=FamilyRelation, on_delete=models.CASCADE)
    cancer_type = models.ForeignKey(to=CancerType, on_delete=models.CASCADE)


class FamilyHistory(models.Model):
    date = models.DateField()
    patient = models.ForeignKey(to=Patient, on_delete=models.CASCADE)
    relation = models.ForeignKey(to=FamilyRelation, on_delete=models.CASCADE)
    health_condition = models.TextField()
    cancer_history = models.ManyToManyField(to=FamilyCancerHistory, blank=True)

    def str(self) -> str:
        return "Family history for "+ str(self.patient)



class Image(models.Model):
    def upload_location(self, file_name):
        return file_name

    image = models.ImageField(null=True,upload_to=upload_location)

class File(models.Model):
    def file_upload_location(self, file_name):
        return file_name

    file = models.FileField(upload_to=file_upload_location)

class Resource(models.Model):
    resource = models.CharField(max_length=5000, blank=True)
    private = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    registered_by = models.ForeignKey(Employee, on_delete= models.SET_NULL, null=True)
    registered_on = models.DateTimeField(null=True)

    def __str__(self):
        return  str(self.resource)

    def is_scheduled(self,day,resource_id):
        resource = Resource.objects.get(id=resource_id)
        print('resource:',resource)
        print('day:', day)
        scheduled_resources = resource.scheduled_resource.filter(start_time__lte=day, end_time__gte=day).exists()
        if scheduled_resources:
            return True
        else:
            return False

class Treatment(models.Model):
    treatment = models.CharField(max_length=5000, blank=True)

    def __str__(self):
        return  str(self.treatment)

class ClinicalFinding(models.Model):
    clinical_finding = models.CharField(max_length=5000, blank=True)

    def __str__(self):
        return  str(self.clinical_finding)

class ParaclinicalFinding(models.Model):
    paraclinical_finding = models.CharField(max_length=5000, blank=True)

    def __str__(self):
        return  str(self.paraclinical_finding)

class Diagnoses(models.Model):
    diagnoses = models.CharField(max_length=5000, blank=True)

    def __str__(self):
        return  str(self.diagnoses)

class Compliant(models.Model):
    compliant = models.CharField(max_length=5000, blank=True)

    def __str__(self):
        return  str(self.compliant)

class Material(models.Model):
    material = models.CharField(max_length=5000, blank=True)
    def __str__(self):
        return  str(self.material)

class PatientBloodGroup(models.Model):
    symptom_status = (
        ('active', 'active'),
        ('not_active', 'not_active'),
    )
    blood_type_units = (
        ('1', 'O'),
        ('2', 'A'),
        ('3', 'B'),
        ('4', 'AB'),

    )
    rh_units = (
        ('1', '+'),
        ('2', '-'),

    )

    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    blood_type = models.CharField(max_length=100, null=True, blank=True, choices=blood_type_units)
    rh_factor = models.CharField(max_length=100, null=True, blank=True, choices=rh_units)
    active = models.CharField(max_length=100, null=True, blank=True, choices=symptom_status, default=True)
    registered_by = models.ForeignKey(Employee, on_delete= models.SET_NULL, null=True)
    registered_on = models.DateTimeField(null=True)

class Day(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self):
        return  str(self.name)

class Recurrence(models.Model):
    DAILY_CHOICES = (
        ('1', 'Every'),
        ('2', 'Every Weekday'),
        ('3', 'Every Weekend Day'),
    )

    YEARLY_CHOICES = (
        ('1', 'January'),
        ('2', 'February'),
        ('3', 'May'),
    )

    days = models.ManyToManyField(Day,blank=True)
    daily_choices = models.CharField(max_length=100, null=True, blank=True, choices=DAILY_CHOICES)
    daily = models.BooleanField(default=False)
    weekly = models.BooleanField(default=False)
    monthly = models.BooleanField(default=False)
    yearly = models.BooleanField(default=False)
    recurrence_amount = models.IntegerField(null=True, blank=True)
    monthly_day = models.IntegerField(null=True, blank=True)
    every_int = models.IntegerField(null=True, blank=True)
    yearly_choices = models.CharField(max_length=100, null=True, blank=True, choices=YEARLY_CHOICES)
    recurrence_count = models.IntegerField(null=True, blank=True)
    recurrence_threshold = models.IntegerField(null=True, blank=True)

    active = models.BooleanField(default=False)

class PatientRecurrence(models.Model):
    DAILY_CHOICES = (
        ('1', 'Every'),
        ('2', 'Every Weekday'),
        ('3', 'Every Weekend Day'),
    )


    days = models.ManyToManyField(Day)
    daily_choices = models.CharField(max_length=100, null=True, blank=True, choices=DAILY_CHOICES)
    daily = models.BooleanField(default=False)
    weekly = models.BooleanField(default=False)
    monthly = models.BooleanField(default=False)
    yearly = models.BooleanField(default=False)
    recurrence_amount = models.IntegerField(null=True, blank=True)
    recurrence_count = models.IntegerField(null=True, blank=True)

    active = models.BooleanField(default=False)

class PatientVitalSign(models.Model):
    symptom_status = (
        ('active', 'active'),
        ('not_active', 'not_active'),
    )
    temperature_unit = (
        ('Fahrenheit', 'Fahrenheit'),
        ('Celcius', 'Celcius'),
    )
    glucose_units = (
        ('mmol/L', 'mmol/L'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    pulse_rate = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(200.0)], null=True, blank=True)  
    temperature = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(100.0)], null=True, blank=True)
    temperature_unit = models.CharField(max_length=100, null=True, blank=True, choices=temperature_unit)
    systolic_blood_pressure = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(200.0)], null=True, blank=True)
    diastolic_blood_pressure = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(90.0)], null=True, blank=True)
    oxygen_saturation = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],blank=True, null=True)
    blood_glucose_level = models.FloatField( null=True, blank=True)
    glucose_level_unit = models.CharField(max_length=100, null=True, blank=True, choices=glucose_units)

    active = models.CharField(max_length=100, null=True, blank=True, choices=symptom_status, default=True)
    registered_by = models.ForeignKey(Employee, on_delete= models.SET_NULL, null=True)
    registered_on = models.DateTimeField(null=True)


class PatientDemoValues(models.Model):
    name = models.CharField(max_length=500, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    cholestrol = models.FloatField( null=True, blank=True)  
    HDL = models.FloatField( null=True, blank=True)  
    LDL = models.FloatField( null=True, blank=True)  
    TGO = models.FloatField( null=True, blank=True)  
    TGP = models.FloatField( null=True, blank=True)  
    active = models.BooleanField(default=True)
    registered_by = models.ForeignKey(Employee, on_delete= models.SET_NULL, null=True)
    registered_on = models.DateTimeField(null=True)

class PatientCheckin(models.Model):
    status_choices = (
        ('Admitted', 'Admitted'),
        ('Cancelled', 'Cancelled'),
        ('No Show', 'No Show'),

    )
    status = models.CharField(max_length=100, null=True, blank=True, choices=status_choices)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    treatment = models.ForeignKey(Treatment, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.CharField(max_length=5000, blank=True,null=True)
    active = models.BooleanField(default=True)
    registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
    registered_on = models.DateTimeField(null=True)

class PatientResource(models.Model):
    category_choices = (
        ('Admitted', 'Admitted'),
        ('Cancelled', 'Cancelled'),
        ('No Show', 'No Show'),

    )
    category = models.CharField(max_length=100, null=True, blank=True, choices=category_choices)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    resource = models.ForeignKey(Resource, on_delete=models.SET_NULL, null=True, blank=True,related_name='scheduled_resource')
    note = models.CharField(max_length=5000, blank=True,null=True)
    reason = models.CharField(max_length=5000, blank=True,null=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    active = models.BooleanField(default=True)
    registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
    registered_on = models.DateTimeField(null=True)


class PatientNote(models.Model):

    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.CharField(max_length=5000, blank=True)
    active = models.BooleanField(default=True)
    registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
    registered_on = models.DateTimeField(null=True)

class PatientAllergy(models.Model):

    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    allergy = models.CharField(max_length=5000, blank=True)
    active = models.BooleanField(default=True)
    registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
    registered_on = models.DateTimeField(null=True)
class Tag(models.Model):
    name = models.CharField(max_length=200, null=True)

class PatientBarcode(models.Model):
    def upload_location(self, file_name):
        return file_name
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    bar_code = models.ImageField(null=True,upload_to=upload_location,blank=True)
    def save(self, *args, **kwargs):          # overriding save() 
        COD128 = barcode.get_barcode_class('code128')
        rv = BytesIO()
        code = COD128(f'{self.patient.first_name}', writer=ImageWriter()).write(rv)
        self.bar_code.save(f'{self.patient.first_name}.png', File(rv), save=False)
        return super().save(*args, **kwargs)



class PatientClinicalFinding(models.Model):

    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag)
    clinical_finding = models.CharField(max_length=5000, blank=True)
    image = models.ManyToManyField(Image)
    active = models.BooleanField(default=True)
    registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
    registered_on = models.DateTimeField(null=True)

    def __str__(self):
        return "finding" + str(self.patient) 

class PatientParaclinicalFinding(models.Model):

    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag)
    note = models.CharField(max_length=5000, blank=True)
    file = models.ManyToManyField(File)
    active = models.BooleanField(default=True)
    registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
    registered_on = models.DateTimeField(null=True)

    def __str__(self):
        return  str(self.patient) 

class PatientTreatment(models.Model):

    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag)
    treatment = models.CharField(max_length=5000, blank=True)
    detail = models.CharField(max_length=10000, blank=True)
    image = models.ManyToManyField(Image)
    active = models.BooleanField(default=True)
    registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
    registered_on = models.DateTimeField(null=True)

    def __str__(self):
        return  str(self.patient) + str(self.treatment)

class PatientSurgery(models.Model):

    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag)
    note = models.CharField(max_length=10000, blank=True)
    active = models.BooleanField(default=True)
    registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
    registered_on = models.DateTimeField(null=True)

    def __str__(self):
        return  str(self.patient) 


class ScheduleStuff(models.Model):
    category_choices = (
        ('Appointment', 'Appointment'),
        #('Kebele Discount', 'Kebele Discount'),
        ('Administrative', 'Administrative'),
        ('Payment', 'Payment'),
    )
    time_units = (
        ('Minutes', 'Minutes'),
        #('Kebele Discount', 'Kebele Discount'),
        ('Hours', 'Hours'),
        ('Days', 'Days'),
        ('Weeks', 'Weeks'),

    )

    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag)
    reason = models.CharField(max_length=1000, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True, choices=category_choices, default=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    note = models.CharField(max_length=1000, blank=True,null=True)
    reminder_unit = models.CharField(max_length=100, null=True, blank=True, choices=time_units, default=True)

    active = models.BooleanField(default=True)
    registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
    registered_on = models.DateTimeField(null=True)

    def __str__(self):
        return  str(self.patient) 

class MedicalCertificate(models.Model):
    category_choices = (
        ('Normal Certificate', 'Normal Certificate'),
        #('Kebele Discount', 'Kebele Discount'),
        ('Maternity', 'Maternity'),
        ('Hospital Leave', 'Hospital Leave'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.CharField(max_length=1000, blank=True)
    certificate_type = models.CharField(max_length=100, null=True, blank=True, choices=category_choices, default=True)
    remarks = models.CharField(max_length=1000, blank=True)

    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)

    active = models.BooleanField(default=True)
    registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
    registered_on = models.DateTimeField(null=True)

    def __str__(self):
        return  str(self.patient) 

class MedicalAttendance(models.Model):
    category_choices = (
        ('Normal Certificate', 'Normal Certificate'),
        #('Kebele Discount', 'Kebele Discount'),
        ('Maternity', 'Maternity'),
        ('Hospital Leave', 'Hospital Leave'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)

    date = models.DateTimeField(null=True)
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)

    active = models.BooleanField(default=True)
    registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
    registered_on = models.DateTimeField(null=True)

    def __str__(self):
        return  str(self.patient) 


class PatientMaterial(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(blank=True, null=True)
    active = models.BooleanField(default=True)
    registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
    registered_on = models.DateTimeField(null=True)

    def __str__(self):
        return "Material" + str(self.patient) 

class Surgery(models.Model):
    surgery = models.CharField(max_length=5000, blank=True)
    def __str__(self):
        return  str(self.surgery)

class Recommendation(models.Model):
    recommendation = models.CharField(max_length=5000, blank=True)
    def __str__(self):
        return  str(self.recommendation)

class ReviewOfSystems(models.Model):
    fatigue = models.CharField(max_length=100, null=True, blank=True)
    fevers = models.CharField(max_length=100, null=True, blank=True)
    headache = models.CharField(max_length=100, null=True, blank=True)
    weight_loss = models.CharField(max_length=100, null=True, blank=True)
    other = models.CharField(max_length=100, null=True, blank=True)
    chest_pain = models.CharField(max_length=100, null=True, blank=True)
    difficulty_breathing = models.CharField(max_length=100, null=True, blank=True)
    palpitations = models.CharField(max_length=100, null=True, blank=True)
    swelling = models.CharField(max_length=100, null=True, blank=True)
    blurred_vision = models.CharField(max_length=100, null=True, blank=True)
    eye_pain = models.CharField(max_length=100, null=True, blank=True)
    eye_sensetivity = models.CharField(max_length=100, null=True, blank=True)
    tremors = models.CharField(max_length=100, null=True, blank=True)
    dizzy_spers = models.CharField(max_length=100, null=True, blank=True)
    numbness = models.CharField(max_length=100, null=True, blank=True)
    wheezing = models.CharField(max_length=100, null=True, blank=True)
    shortness_of_breath = models.CharField(max_length=100, null=True, blank=True)
    cough = models.CharField(max_length=100, null=True, blank=True)
    sleep_apnea = models.CharField(max_length=100, null=True, blank=True)
    joint_pain = models.CharField(max_length=100, null=True, blank=True)
    neck_pain = models.CharField(max_length=100, null=True, blank=True)
    back_pain = models.CharField(max_length=100, null=True, blank=True)
    excessive_thirst = models.CharField(max_length=100, null=True, blank=True)
    too_hot_or_cold = models.CharField(max_length=100, null=True, blank=True)
    tired = models.CharField(max_length=100, null=True, blank=True)
    abdominal_pain = models.CharField(max_length=100, null=True, blank=True)
    nausea = models.CharField(max_length=100, null=True, blank=True)
    indigestion = models.CharField(max_length=100, null=True, blank=True)

    registered_by = models.ForeignKey(Employee, on_delete= models.SET_NULL, null=True)
    registered_on = models.DateTimeField(null=True)


class PhysicalExam(models.Model):
    general = models.CharField(max_length=100, null=True, blank=True)
    head = models.CharField(max_length=100, null=True, blank=True)
    eyes = models.CharField(max_length=100, null=True, blank=True)
    ears = models.CharField(max_length=100, null=True, blank=True)
    nose = models.CharField(max_length=100, null=True, blank=True)
    mouth_and_throat = models.CharField(max_length=100, null=True, blank=True)
    neck = models.CharField(max_length=100, null=True, blank=True)
    breasts = models.CharField(max_length=100, null=True, blank=True)
    gastrointestinal = models.CharField(max_length=100, null=True, blank=True)
    genitourinary = models.CharField(max_length=100, null=True, blank=True)
    neurologic = models.CharField(max_length=100, null=True, blank=True)
    psyhiatric = models.CharField(max_length=100, null=True, blank=True)

class PatientConsultation(models.Model):

    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    systems_review = models.ForeignKey(ReviewOfSystems, on_delete=models.SET_NULL, null=True, blank=True)
    physical_exam = models.ForeignKey(PhysicalExam, on_delete=models.SET_NULL, null=True, blank=True)
    vital_sign = models.ForeignKey(PatientVitalSign, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey('lis.Order', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=100, blank=True)
    tags = models.ManyToManyField(Tag,null=True,blank=True)
    condition = models.CharField(max_length=100, blank=True)
    compliant = models.ManyToManyField(Compliant,null=True,blank=True)
    treatment = models.ManyToManyField(Treatment,null=True,blank=True)
    image = models.ManyToManyField(Image,null=True,blank=True)
    clinical_finding = models.ManyToManyField(ClinicalFinding,null=True,blank=True)
    paraclinical_finding = models.ManyToManyField(ParaclinicalFinding,null=True,blank=True)
    diagnoses = models.ManyToManyField(Diagnoses,null=True,blank=True)
    material = models.ManyToManyField(Material,null=True,blank=True)
    surgery = models.ManyToManyField(Surgery,null=True,blank=True)
    recommendation = models.ManyToManyField(Recommendation,null=True,blank=True)
    active = models.BooleanField(default=True)
    registered_by = models.ForeignKey(Employee,  on_delete= models.SET_NULL, null=True, blank=True)
    registered_on = models.DateTimeField(null=True)

    def __str__(self):
        return "cons" + str(self.patient) 

class PatientPaymentStatus(models.Model):
    payment_status = (
        ('Free', 'Free'),
        #('Kebele Discount', 'Kebele Discount'),
        ('Discount', 'Discount'),
        ('Insurance', 'Insurance'),
        ('Default', 'Default'),

    )

    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    payment_status = models.CharField(max_length=100, null=True, blank=True, choices=payment_status, default=True)
    active = models.BooleanField(default=True)
    registered_on = models.DateTimeField(null=True)
    registered_by = models.ForeignKey(Employee, on_delete= models.SET_NULL, null=True)

    def __str__(self):
        return  str(self.patient) + str(self.payment_status)

    @property
    def discountPatientAmount(self):
        rt = PatientPaymentStatus.objects.filter(active=True,payment_status='Discount')
        if rt:
            return rt.count()
        else:
            return 0

    @property
    def freePatientAmount(self):
        rt = PatientPaymentStatus.objects.filter(active=True,payment_status='Free')
        if rt:
            return rt.count()
        else:
            return 0
    @property
    def insurancePatientAmount(self):
        rt = PatientPaymentStatus.objects.filter(active=True,payment_status='Insurance')
        if rt:
            return rt.count()
        else:
            return 0
    @property
    def defaultPatientAmount(self):
        rt = PatientPaymentStatus.objects.filter(active=True, payment_status='Default')
        if rt:
            return rt.count()
        else:
            return 0


class InsuranceDetail(models.Model):
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=300)


class PatientInsurance(models.Model):

    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    insurance_detail = models.ForeignKey(InsuranceDetail, on_delete=models.SET_NULL, null=True, blank=True)
    active = models.BooleanField(default=True)
    registered_on = models.DateTimeField(null=True)

class PersonInfo(models.Model):
    TYPE_CHOICES = [
        ('1','Family Medic'),
        ('2', 'Referrer'),
        ('3', 'Emergency Contact'),

    ]
    TITLE_CHOICES = [
        ('Mr.','Mr.'),
        ('Ms.', 'Ms.'),
        ('Mrs.', 'Mrs.'),

    ]
    REGION_CHOICES = [
        ('Addis Ababa','Addis Ababa'),
        ('Tigray','Tigray'),
        ('Afar', 'Afar'),
        ('Amhara', 'Amhara'),
        ('Oromia', 'Oromia'),
        ('Benishangul', 'Benishangul'),
        ('Gambella', 'Gambella'),
        ('SNNPRS', 'SNNPRS'),
        ('Somali', 'Somali'),
        ('Sidama', 'Sidama'),
    ]

    person_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    account_number = models.CharField(max_length=14,null=True,blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    note = models.CharField(max_length=5000, null=True, blank=True)
    title = models.CharField(max_length=10, choices=TITLE_CHOICES,null=True,blank=True)
    phone_number = models.CharField(max_length=10)
    date_of_birth = models.DateField(null=True,blank=True)
    sub_city = models.CharField(max_length=2000, null=True, blank=True) 
    wereda = models.CharField(max_length=2000, null=True, blank=True) 
    kebele = models.CharField(max_length=2000, null=True, blank=True) 
    region = models.CharField(max_length=20, choices=REGION_CHOICES, null=True)
    image = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True, blank=True)
    registered_on = models.DateTimeField(null=True)
    registered_by = models.ForeignKey(Employee, on_delete= models.SET_NULL, null=True)
    email = models.EmailField(max_length=50,null=True, blank=True)
    active = models.BooleanField(default=True)
    def __str__(self):
        return  str(self.first_name) + " " + str(self.last_name)

class PatientFamilyMedic(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    medic = models.ForeignKey(PersonInfo, on_delete=models.SET_NULL, null=True, blank=True)
    active = models.BooleanField(default=True)
    registered_on = models.DateTimeField(null=True)

class PatientReferrer(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    referrer = models.CharField(max_length=100, null=True, blank=True)
    active = models.BooleanField(default=True)
    registered_on = models.DateTimeField(null=True)

class Copayer(models.Model):
    TAX_HANDLING_CHOICES = [
        ('1','Copayer Covers Taxes'),
        ('2', 'Patient Pays Taxes'),

    ]

    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    tax_handling = models.CharField(max_length=10, choices=TAX_HANDLING_CHOICES,null=True,blank=True)
    person_info = models.ForeignKey(PersonInfo, on_delete=models.SET_NULL, null=True, blank=True)
    copayer_type = models.CharField(max_length=100, null=True, blank=True) 
    registered_on = models.DateTimeField(null=True)
    registered_by = models.ForeignKey(Employee, on_delete= models.SET_NULL, null=True)
    active = models.BooleanField(default=True)


class PatientMedicalHistory(models.Model):

    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    high_blood_pressure = models.CharField(max_length=100, null=True, blank=True)
    high_cholesterol = models.CharField(max_length=100, null=True, blank=True)
    vein_trouble = models.CharField(max_length=100, null=True, blank=True)
    kidney_disease = models.CharField(max_length=100, null=True, blank=True)
    thyroid_problems = models.CharField(max_length=100, null=True, blank=True)
    drug_abuse = models.CharField(max_length=100, null=True, blank=True)
    replacement = models.CharField(max_length=100, null=True, blank=True)
    DVT = models.CharField(max_length=100, null=True, blank=True)
    pulmonary_embolus = models.CharField(max_length=100, null=True, blank=True)
    tuberculosis = models.CharField(max_length=100, null=True, blank=True)
    nervous_disorder = models.CharField(max_length=100, null=True, blank=True)
    sinus = models.CharField(max_length=100, null=True, blank=True)
    tonsillitis = models.CharField(max_length=100, null=True, blank=True)
    bleeding_tendencies = models.CharField(max_length=100, null=True, blank=True)
    lung_disease = models.CharField(max_length=100, null=True, blank=True)
    asthma = models.CharField(max_length=100, null=True, blank=True)
    heart_trouble = models.CharField(max_length=100, null=True, blank=True)
    seasonal_allergies = models.CharField(max_length=100, null=True, blank=True)
    arthiritis = models.CharField(max_length=100, null=True, blank=True)
    gastrointestinal = models.CharField(max_length=100, null=True, blank=True)
    cancer = models.CharField(max_length=100, null=True, blank=True)
    stroke = models.CharField(max_length=100, null=True, blank=True)
    diabetes = models.CharField(max_length=100, null=True, blank=True)
    pneumonia = models.CharField(max_length=100, null=True, blank=True)
    hepatitis = models.CharField(max_length=100, null=True, blank=True)
    osteporosis = models.CharField(max_length=100, null=True, blank=True)
    other = models.CharField(max_length=1000, null=True, blank=True)

    registered_by = models.ForeignKey(Employee, on_delete= models.SET_NULL, null=True)
    registered_on = models.DateTimeField(null=True)

class PatientSocialHistory(models.Model):

    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    tobaco_use = models.CharField(max_length=100, null=True, blank=True)
    alcohol_use = models.CharField(max_length=100, null=True, blank=True)
    caffeine_use = models.CharField(max_length=100, null=True, blank=True)
    drug_use = models.CharField(max_length=100, null=True, blank=True)
    exercise = models.CharField(max_length=100, null=True, blank=True)
    sleep = models.CharField(max_length=100, null=True, blank=True)

class PatientSurgeryHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    surgery_history = models.CharField(max_length=1000, null=True, blank=True)
    registered_by = models.ForeignKey(Employee, on_delete= models.SET_NULL, null=True)
    registered_on = models.DateTimeField(null=True)
    active = models.BooleanField(default=True)

class PatientFamilyHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    high_blood_pressure = models.CharField(max_length=100, null=True, blank=True)
    tuberculosis = models.CharField(max_length=100, null=True, blank=True)
    mental_illness = models.CharField(max_length=100, null=True, blank=True)
    heart_trouble = models.CharField(max_length=100, null=True, blank=True)
    cancer = models.CharField(max_length=100, null=True, blank=True)
    stroke = models.CharField(max_length=100, null=True, blank=True)
    diabetes = models.CharField(max_length=100, null=True, blank=True)
    kidney_trouble = models.CharField(max_length=100, null=True, blank=True)
    sickle_cell = models.CharField(max_length=100, null=True, blank=True)
    epilepsy = models.CharField(max_length=100, null=True, blank=True)

    other = models.CharField(max_length=1000, null=True, blank=True)

    registered_by = models.ForeignKey(Employee, on_delete= models.SET_NULL, null=True)
    registered_on = models.DateTimeField(null=True)


"""
weight = models.FloatField(
    validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
)
"""