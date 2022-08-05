from .models import SiteConfig


def site_configurations(request):
    site_config = SiteConfig.objects.last()
    if not site_config:
        site_config = SiteConfig(name='HMS')
        site_config.save()
    return {
        'site_config': site_config,
    } 