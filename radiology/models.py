from django.db import models
from django.contrib.auth import get_user_model
from core.models import Patient


User = get_user_model()


class ImagingTest(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class XRayFilm(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class XRayFilmPrice(models.Model):
    film = models.ForeignKey(to=XRayFilm, on_delete=models.SET_NULL, null=True)
    price = models.IntegerField(null=True, blank=True)
    discounted_price = models.IntegerField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.film) + str(self.price)

class UltrasoundRequest(models.Model):
    reason = models.CharField(max_length=200)


class XRayRequest(models.Model):
    SCAN_AREA_CHOICES = [
        ('CHEST', 'CHEST'),
        ('LEG', 'LEG'),
        ('RIGHT HAND', 'RIGHT HAND'),
        ('LEFT HAND', 'LEFT HAND'),
        ('SPINE', 'SPINE'),
    ]
    scan_area = models.CharField(max_length=100, choices=SCAN_AREA_CHOICES, null=True)
    film = models.ForeignKey(to=XRayFilm, on_delete=models.SET_NULL, null=True)
    number = models.CharField(max_length=100)
    marker = models.CharField(max_length=100)


class Order(models.Model):
    ordered_by = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True, related_name='imaging_order')
    ordered_at = models.DateTimeField(auto_now_add=True)
    patient = models.ForeignKey(to=Patient, on_delete=models.CASCADE, related_name='imaging_order')
    xray_request = models.ForeignKey(to=XRayRequest, null=True, on_delete=models.SET_NULL)
    usound_request = models.ForeignKey(to=UltrasoundRequest, null=True, on_delete=models.SET_NULL, blank=True)
    paid = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)

    @property
    def type(self):
        if self.xray_request:
            return "X-Ray"
        return "Ultra-Sound"

    @property
    def scan_area(self):
        if self.xray_request:
            return self.xray_request.scan_area
        return None


class ImagingReport(models.Model):
    order = models.OneToOneField(to=Order, on_delete=models.CASCADE, related_name='report')
    report = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    reported_by = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)


class ImageFile(models.Model):

    def upload_location(self, file_name):
        return file_name

    file = models.FileField(upload_to=upload_location)
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)


"""
doctor orders some kinda imaging test
lab tech sees orders enters report and image files
doc gets notified and can see the images and report
insert file and write report
deleted status on ImageFile
"""