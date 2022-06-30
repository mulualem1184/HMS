from typing import Sequence
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import Patient

User = get_user_model()

class SampleType(models.Model):
    """
      name: name of sample type; like BLOOD, STOOL, URINE
    """
    name = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.name}"


class Specimen(models.Model):

    """
    barcode_image is generated from the accesion number and is saved 
      on this models post_save signal
    """

    def barcode_image_upload_path(self, filename:str):
        # path name to where the barcode image will be stored
        return f"barcode-images/{filename}.jpg"

    # patient = models.ForeignKey(to=..., on_delete=models.DO_NOTHING)
    collected_by = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    collected_at = models.DateTimeField(default=timezone.now)
    sample_type = models.ForeignKey(to=SampleType, on_delete=models.PROTECT)
    container_type = models.CharField(max_length=1000, default="", blank=True)
    sample_volume = models.FloatField(null=True, blank=True)
    accession_number = models.CharField(max_length=50, blank=True, default='')
    barcode_image = models.ImageField(blank=True, upload_to=barcode_image_upload_path)

    def __str__(self):
        return f'{self.id}'


class LaboratorySection(models.Model):
    name = models.CharField(max_length=500, unique=True, null=False, blank=False)

    def __str__(self):
        return self.name


class LaboratoryTestType(models.Model):
    """
    section: the department this test belongs to
    name: name of the test
    tat: amount of time it takes to perform this test in hours
    is_available: is the test available in this lab/hospital
    """

    section = models.ForeignKey(to=LaboratorySection, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=1000, unique=True, blank=False, null=False)
    price = models.FloatField(null=False)
    tat = models.FloatField(verbose_name='TAT', help_text="amount of time it takes to complete this test in hours")
    is_available = models.BooleanField(default=True, blank=True)

    def __str__(self):
        return f"{self.name} [{self.section.name}]"


class Order(models.Model):
    """
    ordered_by: foreign key relation to the Doctor who made the order.
    orderd_at: date and time of when the order was made
    expected_time: datetime of when the results are expected to be returned
    priority: priority of the order. 
    """
    PRIORITY_CHOICES = [
        ('NORMAL', 'NORMAL'),
        ('EMERGENCY', 'EMERGENCY'),
    ]
    patient:Patient = models.ForeignKey(to=Patient, on_delete=models.CASCADE)
    ordered_by = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    ordered_at = models.DateTimeField(auto_now_add=True)
    priority = models.CharField(max_length=50, default='NORMAL', choices=PRIORITY_CHOICES)
    comments = models.TextField(default="", blank=True, null=True)

    def __str__(self):
        return f'{self.pk}'

    @property
    def is_paid(self):
        available_tests = [t for t in self.test_set.all() if t.test_type.is_available]
        if not available_tests: return True
        return all([ t.paid for t in available_tests ])


    def mark_as_paid(self, stat=False):
        # marks the tests that belong to this Order as paid
        for test in self.test_set.all():
            test.paid = True
            test.save()

    @property
    def total_price(self):
        # returns summation of the prices of tests that are
        # included in this 'Order'
        total_price:float = 0.0
        for test in self.test_set.all():
            if test.test_type.is_available:
                total_price += test.price
        return total_price

    @property
    def progress(self, str_rep=True):
        all_tests = self.test_set.all()
        completed_tests = 0
        for test in all_tests:
            if test.status in ('COMPLETED', ):
                completed_tests+=1
        try:
            p_complete = round(completed_tests/len(all_tests)*100, 2)
        except: return None
        if str_rep:
            return f"{p_complete} %"
        return p_complete

    @property
    def is_complete(self) -> bool:
        all_tests = self.test_set.all()
        completed = True
        for test in all_tests:
            if test.status != 'COMPLETED':
                completed = False
                break
        return completed

    @property
    def no_of_tests(self) -> int:
        # total number of tests that belong in this Order
        return self.test_set.count()

    @property
    def no_of_paid_tests(self) -> int:
        paid_tests = 0
        for test in self.test_set.all():
            if test.paid:
                paid_tests += 1
        return paid_tests

    
class LaboratoryTest(models.Model):
    """
    order: foreign-key r/n with Order to which this test belongs to
    test_type: type of test that will be performed
    specimen: collected specimen for this test
    special_instructions: instructions given by the doctor to be considered when performing this test
    paid: paid or not
    status: choice field to track the status of a test
    fail_reason: reason for failure if a 'status' is marked as FAIL 
    referred: if test is not available and must be done on any other labs
    """

    STATUS_CHOICES = [
        ('PENDING', 'PENDING'), # when the order is first made
        ('COMPLETED', 'COMPLETED'), # when test results are entered
        ('SPECIMEN COLLECTED', 'SPECIMEN COLLECTED'), # when samples are collected and its info registered
        ('STARTED', 'STARTED'), # when testing process has started
        ('AWAITING RESULT ENTRY', 'AWAITING RESULT ENTRY'), # when test is complete but results haven't yet been entered
        # ??? (5, 'REFERRED'), # when test is not available and sent out to other labs
        ('FAIL', 'FAIL'), # machine errors/sample rejections...
    ]

    order:Order = models.ForeignKey(to=Order, on_delete=models.CASCADE, related_name="test_set")
    test_type:LaboratoryTestType = models.ForeignKey(to=LaboratoryTestType, on_delete=models.DO_NOTHING)
    specimen:Specimen = models.ForeignKey(to=Specimen, null=True, on_delete=models.CASCADE, related_name='test_set', blank=True)
    special_instructions:str = models.TextField(default='', blank=True)
    paid:bool = models.BooleanField(default=False)
    status = models.CharField(max_length=50,default='PENDING', choices=STATUS_CHOICES, blank=True)
    fail_reason = models.TextField(default='', blank=True, null=True)
    referred:bool = models.BooleanField(default=None, null=True)

    class Meta:
        unique_together = ('order', 'test_type') # a test_type can only be included once

    def __str__(self) -> str:
        return f"{self.test_type.name}"

    def save(self, *args, **kwargs) -> None:
        if self.referred is None: # exectute only the first time
            self.referred = False if self.test_type.is_available else True # if test is available it will not be marked as 'referred'
        return super().save(*args, **kwargs)

    @property
    def price(self) -> int:
        return self.test_type.price

    @property
    def ordered_at(self):
        return self.order.ordered_at

    @property
    def ordered_by(self):
        return self.order.ordered_by

    @property
    def section(self):
        return self.test_type.section

    @property
    def patient(self):
        return self.order.patient


class LaboratoryTestResultType(models.Model):
    """
    this model stores data that help in generating a test result entry form
    name: name of the input data that is required
    input_type: type of input field that's expected; fields are NUMBER, CHOICE, BOOL and TEXT
    """
    INPUT_TYPE_CHOICES = [
        ('BOOL', '+VE/-VE'),
        ('TEXT', 'TEXT'),
        ('NUMBER', 'NUMBER'),
        ('CHOICE', 'CHOICE'),
    ]

    test_type = models.ForeignKey(to=LaboratoryTestType, on_delete=models.CASCADE)
    name = models.CharField(max_length=500, null=False, blank=False, default='result')
    input_type = models.CharField(max_length=15, choices=INPUT_TYPE_CHOICES, default='TEXT')

    class Meta:
        unique_together = ('name', 'test_type') 

    def __str__(self):
        return f"[{self.test_type.name}] {self.name}"


class NormalRange(models.Model):
    """
    represents the normal range of a test result.
    normal range is dependent on sex and age range
    """

    SEX_CHOICES = (
        ('M', 'MALE'),
        ('F', 'FEMALE'),
        ('B', 'Both'),
    )

    test_result_type = models.ForeignKey(to=LaboratoryTestResultType, on_delete=models.CASCADE)
    sex = models.CharField(max_length=1, default='B', choices=SEX_CHOICES)
    min_age = models.PositiveIntegerField(default=0, blank=True, null=True)
    max_age = models.PositiveIntegerField(default=200, blank=True, null=True)
    min_value = models.FloatField(null=True, blank=True)
    max_value = models.FloatField(null=True)
    m_unit = models.CharField(max_length=200, verbose_name="Measurement Unit", blank=True, default="")

    def age_range(self) -> str:
        if all([self.min_age, self.max_age]):
            return f"{self.min_age} - {self.max_age}"
        elif (self.min_age) and (not self.max_age):
            return f" > {self.min_age}"
        elif (self.max_age) and (not self.min_age):
            return f" < {self.max_age}"
        return None

    def value_range(self) -> str:
        if all([self.min_value, self.max_value]):
            return f"{self.min_value} - {self.max_value} {self.m_unit}"
        elif (self.min_value) and (not self.max_value):
            return f" > {self.min_value} {self.m_unit}"
        elif (self.max_value) and (not self.min_value):
            return f" < {self.max_value} {self.m_unit}"
        return None

    def save(self, *args, **kwargs):
        if self.min_age > self.max_age:
            raise ValueError('minumum age can not be greater than maximum age.')
        if self.min_value > self.max_value:
            raise ValueError('minimum value can not be greater than maximum value.')
        super().save(*args, **kwargs)

    @staticmethod
    def get_range(result_type, age=0, sex='B'):
        """
        returns normal range for the given parameters
        age must be between min_age and max_age
        sex could be either of the genders or 'B' for both sexes
        """
        normal_range = None
        try:
            normal_range = NormalRange.objects.get(test_result_type=result_type, min_age__lte=age, max_age__gte=age, sex__in=('B', sex))
        except:
            pass
        return normal_range

    def __str__(self):
        return f"{self.test_result_type}"


class LaboratoryTestResult(models.Model):
    """
    test: the test this result belongs to
    reported_by: user who created this instance
    result_type: what kind of result this test expects
    value: actual value of the result
    """
    test:LaboratoryTest = models.ForeignKey(to=LaboratoryTest, on_delete=models.CASCADE, related_name='result_set')
    reported_by = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    result_type = models.ForeignKey(to=LaboratoryTestResultType, on_delete=models.PROTECT)
    value = models.CharField(max_length=500, blank=False, null=False)

    def __str__(self):
        return f"{self.result_type}: {self.value}"

    @property
    def normal_range(self,age=18, sex='M') -> NormalRange:
        # returns normal range for the given age and sex
        return NormalRange.get_range(self.result_type, self.test.order.patient.age, self.test.order.patient.sex[0]) # first letter of patient.sex

    @property
    def label(self):
        return self.result_type.name

    @property
    def get_parsed_value(self):
        # returns appropriate output based on the result types input
        # if input type is NUMBER self.value will be converted to float
        # if it's BOOL self.value will be changed to +ve and -ve string
        # if its' either CHOICE or TEXT it will be returned as it is
        if self.result_type.input_type == 'NUMBER':
            value = self.value 
            try:
                value = float(self.value)
            except: pass
            return value
        elif self.result_type.input_type == 'BOOL':
            if self.value == 'on':
                return "+ve"
            else:
                return "-ve"
        else:
            return self.value


class TestResultChoice(models.Model):
    """
    A model which holds choices of a test result
        e.g: BLOOD GROUP choices: A, B, AB and O
    """
    test_result_type = models.ForeignKey(to=LaboratoryTestResultType, on_delete=models.CASCADE, related_name='choice_set')
    choice = models.CharField(max_length=200)


    class Meta:
        unique_together = ('test_result_type', 'choice')
    def __str__(self):
        return f"{self.choice}"


class ReferredTestResult(models.Model):
    """
    lab_name: name of hospital/laboratory this test was referred to
    test: test that is being referred
    """
    lab_name = models.CharField(verbose_name="Lab. Name:", max_length=150, blank=True, null=True, help_text="Laboratory name the result came from.")
    test = models.OneToOneField(to=LaboratoryTest, on_delete=models.CASCADE)