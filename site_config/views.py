from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from .decorators import staff_required
from .forms import SiteConfigForm
from .models import SiteConfig


class SiteSettings(View):
    
    @method_decorator(staff_required())
    def get(self, *args, **kwargs):
        return render(self.request, 'site_config/settings.html')


@method_decorator(staff_required(), 'dispatch')
class EditSiteInfo(View):

    def get(self, *args, **kwargs):
        site_setting = SiteConfig.objects.last()
        edit_form = SiteConfigForm(instance=site_setting)
        return render(self.request, 'site_config/edit_site_info.html', {
            'edit_form': edit_form,
        })

    def post(self, *args, **kwargs):
        site_setting = SiteConfig.objects.last()
        edit_form = SiteConfigForm(data=self.request.POST, files=self.request.FILES, instance=site_setting)
        if edit_form.is_valid():
            edit_form.save()
            if 'remove_logo' in self.request.POST:
                site_setting.logo = None
                site_setting.save()
            messages.success(self.request, 'Site information updated!')
            return redirect('admin_dashboard')
        else:
            messages.error(self.request, 'Error while updating site info')
            return render(self.request, 'site_config/edit_site_info.html', {
                'edit_form': edit_form
            })
