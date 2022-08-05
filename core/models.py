from django.db import models
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
#from django.core.validators import 

class Patient(models.Model):
    SEX_CHOICES = [
        ('MALE','MALE'),
        ('FEMALE', 'FEMALE'),
    ]
    inpatient_status = [
        ('yes','yes'),
        ('no', 'no'),
    ]

    registered_at = models.DateTimeField(auto_now_add=True) # saves datetime when the instance is first created
    first_name = models.CharField(max_length=50, validators=[RegexValidator('^[a-zA-Z]*$', ),])
    last_name = models.CharField(max_length=50,validators=[RegexValidator('^[a-zA-Z]*$', ),])
    sex = models.CharField(max_length=10, choices=SEX_CHOICES)
    dob = models.DateField()
    occupation = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=10)
    address = models.CharField(max_length=300)
    inpatient = models.CharField(max_length=10, choices=inpatient_status, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    
    @property
    def age(self):
        # returns age from dob
        td = datetime.date.today() - self.dob
        return td.days//365


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

class PatientVitalSign(models.Model):
    symptom_status = (
        ('active', 'active'),
        ('not_active', 'not_active'),
    )
    temperature_unit = (
        ('Fahrenheit', 'Fahrenheit'),
        ('Celcius', 'Celcius'),
    )
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    pulse_rate = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(200.0)], null=True, blank=True)  
    temperature = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(100.0)], null=True, blank=True)
    temperature_unit = models.CharField(max_length=100, null=True, blank=True, choices=temperature_unit)
    systolic_blood_pressure = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(200.0)], null=True, blank=True)
    diastolic_blood_pressure = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(90.0)], null=True, blank=True)
    active = models.CharField(max_length=100, null=True, blank=True, choices=symptom_status, default=True)
    registered_on = models.DateTimeField(null=True)


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

class InsuranceDetail(models.Model):
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=300)


class PatientInsurance(models.Model):

    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    insurance_detail = models.ForeignKey(InsuranceDetail, on_delete=models.SET_NULL, null=True, blank=True)
    active = models.BooleanField(default=True)
    registered_on = models.DateTimeField(null=True)

#Take it to staff


"""
weight = models.FloatField(
    validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
)
"""