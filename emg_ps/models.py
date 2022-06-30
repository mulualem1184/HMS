from django.db import models
from core.models import Patient
from django.utils import timezone


class MedicalSymptom(models.Model):
    # category = FK or choice field
    code = models.CharField(max_length=50, null=True, blank=True)
    symptom = models.CharField(max_length=300)

    def __str__(self):
        if all([self.code, self.symptom]):
            return f"{self.symptom}({self.code})"
        return self.symptom


class MedicalEmergencyCategory(models.Model):
    name = models.CharField(max_length=1000, unique=True)

    def __str__(self):
        return self.name


class MedicalEmergencyType(models.Model):
    category = models.ForeignKey(to=MedicalEmergencyCategory, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=1000, unique=True)

    def __str__(self):
        return self.name


class ContactPerson(models.Model):
    name = models.CharField(max_length=50, verbose_name='Contact Person full name')
    living_address = models.CharField(max_length=100, verbose_name='Contact Person living Address')
    phone_number = models.CharField(max_length=20, verbose_name='Contact Person phone')

    def __str__(self) -> str:
        return self.name


class EmergencyCase(models.Model):
    # stores details of emergency case,
    # including patient info, case type, date
    SEX_CHOICES = [
        ('MALE', 'MALE'),
        ('FEMALE', 'FEMALE')
    ]
    date_created = models.DateTimeField(default=timezone.now)
    # registered_by = models.ForeignKey(User)
    type = models.ForeignKey(to=MedicalEmergencyType, on_delete=models.SET_NULL, null=True)
    description = models.TextField(null=True)
    patient_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Patient full name')
    patient_age = models.PositiveSmallIntegerField(null=True, blank=True)
    patient_sex = models.CharField(max_length=10, choices=SEX_CHOICES, null=True, blank=True)
    patient = models.ForeignKey(to=Patient, on_delete=models.CASCADE, null=True, blank=True)
    contact_person = models.OneToOneField(to=ContactPerson, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    

class Epidemic(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    symptoms = models.ManyToManyField(to=MedicalSymptom)
    prevention = models.TextField()
    treatment = models.TextField()
    active = models.BooleanField(default=True, verbose_name='Currently active')
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)

    @property
    def active(self):
        return self.end_date is None
    
    def __str__(self) -> str:
        return f'{self.name} from {self.start_date} to {self.end_date or "-"}'    


# class ReferredCase(models.Model):
#     reason = models.TextField(null=True, blank=True)
#     # case = models.