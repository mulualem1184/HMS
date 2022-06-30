from typing import Sequence

from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone

from staff_mgmt.models import Attendance, WorkShift

from .utils import get_time_difference

User = get_user_model()


@receiver(user_logged_in)
def save_attendance_for_logged_in_user(sender, **kwargs):
    _user:User = kwargs.get('user')
    try:
        _user.employee
    except:
        return
    login_time = _user.last_login.time()
    day = timezone.now().weekday()
    employee_shifts:Sequence[WorkShift] = _user.employee.today_shifts
    for shift in employee_shifts:
        if get_time_difference(login_time, shift.end_time):
            att, is_created = Attendance.objects.get_or_create(employee=_user.employee, shift=shift, date=timezone.now().date())
            if is_created | (att.start_time is None):
                att.start_time = login_time
                att.save()
    print('Attendance has been updated.')