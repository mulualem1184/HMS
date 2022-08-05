from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls.conf import include
from django.views.generic.base import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('lis/', include('lis.urls')),
    path('notification/', include('notification.urls')),
    path('staff/', include('staff_mgmt.urls', namespace='staff')),
    path('emergency/', include('emg_ps.urls', namespace='emergency')),
    path('base-temp', TemplateView.as_view(template_name='base.html')),
    path('original-temp', TemplateView.as_view(template_name='original_template.html')),
    path('core/', include('core.urls', namespace='core')),
    path('radiology/', include('radiology.urls', namespace='radiology')),
    path('site-config/', include('site_config.urls', namespace='site_config')),    
    path('', include('pharmacy_app.urls')),
    path('', include('inpatient_app.urls')),
    path('', include('outpatient_app.urls')),
    path('', include('billing_app.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
