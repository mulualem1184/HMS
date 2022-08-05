from django.http import HttpResponseForbidden


def staff_required():
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if request.user.is_staff:
                return func(request, *args, **kwargs)
            return HttpResponseForbidden()
        return wrapper
    return decorator