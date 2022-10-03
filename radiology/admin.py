from django.contrib import admin
from .models import XRayFilm, Order, ImageFile, ImagingReport,XRayFilmPrice


admin.site.register([XRayFilm, Order, ImageFile, ImagingReport, XRayFilmPrice])