from django import template
from staff_mgmt.models import Attendance, WorkShift

register = template.Library()

@register.simple_tag(takes_context=True)
def update_shift_flag(context, att:Attendance, shift:WorkShift):
    # updates checkShift flag in the template context
    if att.shift == shift:
        context['checkShift'] = True
        return ''
    context['checkShift'] = False
    return ''