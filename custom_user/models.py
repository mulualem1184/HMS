import time
from hashlib import md5

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):

    MALE = 'M'
    FEMALE = 'F'

    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    )

    def profile_image_upload_location(self,file_name:str):
        name = file_name.split('.')[0]
        file_ext = '.' + file_name.split('.')[1]
        name = md5(f'name {time.time()}'.encode('utf-8')).hexdigest()
        return f'profile_images/{name + file_ext}'

    username = None
    first_name = models.CharField(_('first name'), max_length=150, blank=False)
    last_name = models.CharField(_('last name'), max_length=150, blank=False)
    phone_number = models.CharField(max_length=10, unique=True)
    email = models.EmailField(max_length=50, unique=True)
    profile_image = models.ImageField(blank=True, upload_to=profile_image_upload_location)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=1, blank=True)
    age = models.PositiveSmallIntegerField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']

    objects = UserManager()


    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'