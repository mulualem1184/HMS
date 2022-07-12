from django.db import models
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator


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
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES)
    dob = models.DateField()
    occupation = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)
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
    blood_pressure = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(200.0)], null=True, blank=True)
    active = models.CharField(max_length=100, null=True, blank=True, choices=symptom_status, default=True)
    registered_on = models.DateTimeField(null=True)
"""
weight = models.FloatField(
    validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
)
"""