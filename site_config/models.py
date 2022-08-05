from django.db import models


class SiteConfig(models.Model):

    def logo_upload_location(self, filename):
        return 'logo'

    name = models.CharField(max_length=5)
    logo = models.ImageField(upload_to=logo_upload_location, null=True, blank=True)

    def __str__(self):
        return self.name