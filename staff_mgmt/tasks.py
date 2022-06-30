from datetime import timedelta

from background_task import background
from background_task.models import Task
from django.utils import timezone

from .models import Employee, StaffLeave


@background(schedule=60)
def update_leave_status(employee_id:int):
    try:
        employee:Employee = Employee.objects.get(id=employee_id)
        employee.on_leave = False
        employee.save()
    except:
        pass


def schedule_leave_status_updater(leave:StaffLeave, offset=120):
    if not isinstance(leave, StaffLeave):
        return
    employee = leave.employee
    end_date = leave.to_date
    date_dc:timedelta = end_date - timezone.now().date()
    update_leave_status(employee.id, schedule=int(date_dc.total_seconds()) + offset, creator=leave)


def cancel_scheduled_leave_update(creator_id:int):
    # removes scheduled task if the leave request is denied
    tasks = Task.objects.filter(creator_object_id=creator_id)
    for task in tasks:
        task.delete()