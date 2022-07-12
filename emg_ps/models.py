from core.models import Patient, PatientVitalSign
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


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


class ChiefComplaint(models.Model):
    name = models.CharField(max_length=100,)

    def __str__(self):
        return self.name


class PatientReferralLocation(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class EmergencyCase(models.Model):
    # stores details of emergency case,
    # including patient info, case type, date
    SEX_CHOICES = [
        ('MALE', 'MALE'),
        ('FEMALE', 'FEMALE')
    ]
    TRANSPORT_CHOICES = [
        ('Ambulance', 'Ambulance'),
        ('Public Taxi', 'Public Taxi'),
        ('Private Car', 'Private Car'),
        ('Walking', 'Walking'),
    ]
    TRIAGE_COLOR_CHOICES = [
        ('RED', 'RED'),
        ('ORANGE', 'ORANGE'),
        ('YELLOW', 'YELLOW'),
        ('BLACK', 'BLACK'),
    ]
    AVPU_CHOICES = [
        (0, 'ALERT'),
        (1, 'REACTS TO VOICE'),
        (2, 'REACTS TO PAIN'),
        (3, 'UNRESPONSIVE'),
    ]
    MOBILITY_CHOICES = [
        (0, 'Walking'),
        (1, 'With help'),
        (2, 'Stretcher/Immobile'),
    ]
    registered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    arrival_date = models.DateTimeField(default=timezone.now, verbose_name='Date and Time of Arrival')
    triage_date = models.DateTimeField(default=timezone.now, verbose_name='Date and Time of Triage')
    patient_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Patient full name')
    patient_age = models.PositiveSmallIntegerField(null=True, blank=True)
    patient_sex = models.CharField(max_length=10, choices=SEX_CHOICES, null=True, blank=True)
    card_number = models.CharField(max_length=300, null=True, blank=True)
    address = models.CharField(max_length=300, null=True, blank=True)
    transport = models.CharField(max_length=200, choices=TRANSPORT_CHOICES, null=True)
    was_referred = models.BooleanField(default=False)
    referred_from = models.ForeignKey(to=PatientReferralLocation, null=True, on_delete=models.SET_NULL)
    pre_hospital_care = models.CharField(verbose_name="Was pre-hospital care/first aid given?", max_length=300, default='')
    date_of_illness = models.DateTimeField(default=timezone.now)
    injury_mechanism = models.CharField(verbose_name="Mechanism of injury", max_length=400, null=True, blank=True)
    chief_complaint_set = models.ManyToManyField(to=ChiefComplaint)
    vital_sign:PatientVitalSign = models.OneToOneField(to=PatientVitalSign, null=True, blank=True, on_delete=models.SET_NULL)
    triage_treatment = models.TextField(verbose_name="Treatment and Investigation on Triage", null=True, blank=True)
    other_illness = models.TextField(verbose_name='Allergies/Past medical illnesses', blank=True, null=True)
    triage_color = models.CharField(max_length=50, choices=TRIAGE_COLOR_CHOICES, null=True, blank=True)
    avpu = models.IntegerField(verbose_name='AVPU', choices=AVPU_CHOICES, null=True, blank=True)
    mobility = models.IntegerField(choices=MOBILITY_CHOICES, null=True, blank=True, default=None)
    trauma = models.BooleanField(default=False, null=True, blank=True)
    patient = models.ForeignKey(to=Patient, on_delete=models.CASCADE, null=True, blank=True)
    contact_person = models.OneToOneField(to=ContactPerson, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    @property
    def triage_score(self):
        score = 0
        score += self.mobility or 0
        score += self.avpu or 0
        temp = self.vital_sign.temperature if self.vital_sign else None
        pr = self.vital_sign.pulse_rate if self.vital_sign else None
        bp = self.vital_sign.blood_pressure if self.vital_sign else None
        if self.trauma:
            score +=1
        if self.vital_sign:
            if temp: 
                if (temp > 38.5) or (temp < 35):
                    score += 2
            if pr:
                if (pr >= 41 and pr<=50) or (pr >= 101 and pr<=110):
                    score +=1
                elif (pr<41) or (pr>=111 and pr<=129):
                    score +=2
                elif pr > 129:
                    score +=3
            if bp:
                if (bp>=81 and bp<=100):
                    score +=1
                elif (bp>=71 and bp<80) or (bp>199):
                    score +=2
                elif (bp < 71):
                    score +=3
        return score
    

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