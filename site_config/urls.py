from django.urls import path
from .views import EditSiteInfo, SiteSettings

app_name = 'site_config'

urlpatterns = [
    path('', SiteSettings.as_view(), name='site_settings'),
    path('edit-site-info', EditSiteInfo.as_view(), name='edit_site_info'),
]