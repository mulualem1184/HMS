from .models import SiteConfig


def site_configurations(request):
    site_config = SiteConfig.objects.last()
    if not site_config:
        site_config = SiteConfig(name='HMS')
        site_config.save()
    return {
        'site_config': site_config,
    } 

def designation_configurations(request):
    try:
        user_designation = request.user.employee.designation  
        print('designation: ',user_designation)
        print('user: ',request.user)

        return {
            'user_designation': user_designation,
        } 

    except:
        pass