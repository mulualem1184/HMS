from datetime import timedelta
from typing import Sequence

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from .utils import TimeOverlapError, check_time_overlap, get_time_difference

USER = get_user_model()


class Department(models.Model):
    """
    name: name of the department
    """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Designation(models.Model):
    """
    name: name of the type of staff e.g Doctor
    department: the department this staff belongs too
    staff_code: code the staff gets identified with, also used with permissions
    """
    name = models.CharField(max_length=100)
    department = models.ForeignKey(to=Department, on_delete=models.CASCADE)
    staff_code = models.CharField(max_length=50, verbose_name='Designation Code')

    class Meta:
        unique_together = ('name', 'staff_code')

    def __str__(self) -> str:
        return self.name


class Specialty(models.Model):

    name = models.CharField(max_length=100)
    designation = models.ForeignKey(to=Designation, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name
    

class ShiftType(models.Model):
    department = models.ForeignKey(to=Department, on_delete=models.CASCADE)
    can_overlap = models.BooleanField(default=False)

    def __str__(self):
        return f"{str(self.department)} shift"


class WorkShift(models.Model):
    DAY_CHOICES = (
        (0, 'MONDAY'),
        (1, 'TUESDAY'),
        (2, 'WEDNESDAY'),
        (3, 'THURSDAY'),
        (4, 'FRIDAY'),
        (5, 'SATURDAY'),
        (6, 'SUNDAY'),
    )

    shift_type = models.ForeignKey(to=ShiftType, on_delete=models.CASCADE)
    day = models.PositiveSmallIntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f'{self.get_day_display()} {self.start_time} - {self.end_time}'

    @property
    def department(self):
        return self.shift_type.department

    @property
    def work_hours(self):
        diff_in_min = get_time_difference(self.start_time, self.end_time)
        return diff_in_min/60

    def save(self, *args, **kwargs) -> None:
        overlaps = False
        if not self.shift_type.can_overlap:
            shift_set:Sequence[WorkShift] = self.__class__.objects.filter(day=self.day, shift_type=self.shift_type)
            # exclude self.id; comparison with only other objects is needed
            if self.id:
                shift_set = shift_set.exclude(id=self.id)
            for ws in shift_set:
                if check_time_overlap((self.start_time, self.end_time), (ws.start_time, ws.end_time)) | check_time_overlap((ws.start_time, ws.end_time), (self.start_time, self.end_time)):
                    overlaps = True
                    break
        if overlaps:
            raise TimeOverlapError("Overlapping time is not allowed for current shift")
        return super().save(*args, **kwargs)


class Employee(models.Model):
    """
    user_profile: django's auth user
    designation: the role of the user
    employed_date: time of employment 
    """
    employee_id = models.CharField(max_length=100, unique=True)
    user_profile = models.OneToOneField(to=USER, on_delete=models.CASCADE)
    designation = models.ForeignKey(to=Designation, on_delete=models.DO_NOTHING)
    specialty = models.ForeignKey(to=Specialty, on_delete=models.SET_NULL, null=True, blank=True)
    employed_date = models.DateField()
    shift_set = models.ManyToManyField(to=WorkShift)
    on_leave = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.user_profile.full_name}-{str(self.user_profile)}'

    @property
    def department(self):
        # returns the department this employee belongs to
        return self.designation.department

    @property
    def first_name(self):
        return self.user_profile.first_name

    @property
    def last_name(self):
        return self.user_profile.last_name

    @property
    def full_name(self):
        return self.user_profile.full_name

    @property
    def email(self):
        return self.user_profile.email

    @property
    def phone_number(self):
        return self.user_profile.phone_number

    @property
    def today_shifts(self):
        day = timezone.now().weekday()
        return self.shift_set.filter(day=day)

    def save(self, *args, **kwargs):
        self.employee_id = self.employee_id.upper()
        return super().save(*args, **kwargs)


class Attendance(models.Model):
    """
    shift: the shift this attendance record is being stored for
    date: date of the attendance
    to-do: future dates should not be saved
    """

    employee = models.ForeignKey(to=Employee, on_delete=models.CASCADE)
    shift = models.ForeignKey(to=WorkShift, on_delete=models.CASCADE, related_name='attendance_list') # unique_for_date=True
    date = models.DateField(default=timezone.now)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    @property
    def start_time_str(self):
        return str(self.start_time)

    @property
    def end_time_str(self):
        return str(self.end_time)

    @property
    def is_present(self):
        if self.start_time:
            return True
        return False

    @property
    def work_hours(self):
        # if not all([self.start_time, self.end_time]):
        #     return 0
        print("Start time is ", self.start_time)
        print("End time is ", self.end_time)
        if not self.start_time:
            return 0
        elif self.start_time and (not self.end_time):
            if (timezone.now().date() - self.date).days == 0:
                return round(get_time_difference(self.start_time, timezone.now().time())/60, 2)
            else:
                return round(get_time_difference(self.start_time, self.shift.end_time)/60, 2)
        end_min = self.end_time.hour*60 + self.end_time.minute
        start_min = self.start_time.hour*60 + self.start_time.minute
        return round((end_min - start_min)/60, 2)


class EmployeeDocument(models.Model):
    """
    stores documents related to employee
    employee: user this document belongs to
    document_name: name of the type of this document e.g passport, image
    document: the actual file; could be image, docs, pdf
    """

    def file_upload_location(self, filename):
        return f"employee-documents/{self.employee.id}/{filename}"

    employee = models.ForeignKey(to=Employee, on_delete=models.CASCADE, related_name='document_set')
    document_name = models.CharField(max_length=100)
    document = models.FileField(upload_to=file_upload_location)
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(to=USER, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.employee)


class StaffLeave(models.Model):

    TYPES_OF_LEAVE = [
        ('ANNUAL LEAVE', 'ANNUAL LEAVE'),
        ('SICK LEAVE', 'SICK LEAVE'),
    ]

    LEAVE_REQUEST_STATUS = [
        ('PENDING', 'PENDING'),
        ('APPROVED', 'APPROVED'),
        ('DECLINED', 'DECLINED'),
    ]

    employee = models.ForeignKey(to=Employee, on_delete=models.CASCADE)
    from_date = models.DateField()
    to_date = models.DateField()
    description = models.TextField()
    type_of_leave = models.CharField(max_length=20, choices=TYPES_OF_LEAVE)
    status = models.CharField(max_length=20, choices=LEAVE_REQUEST_STATUS , default='PENDING')

    @property
    def no_of_days(self):
        return (self.to_date - self.from_date).days

    @staticmethod
    def check_leave(e, date) -> bool:
        # checks if e is on leave for the given date
        lr = StaffLeave.objects.filter(employee=e, from_date__lte=date, to_date__gte=date, status='APPROVED')
        if lr:
            return True
        return False


class DepartmentHead(models.Model):
    department = models.ForeignKey(to=Department, on_delete=models.CASCADE)
    employee = models.ForeignKey(to=Employee, on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True)
    assigned_by = models.ForeignKey(to=USER, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.department} department head"

    @staticmethod
    def get_department_head(dept:Department) -> Employee:
        lh = None
        try:
            lh:DepartmentHead = DepartmentHead.objects.filter(department=dept).last()
        except: pass
        if lh and not lh.end_date:
            return lh.employee
        return None

    @staticmethod
    def is_employee_department_head(employee:Employee) -> Department:
        lh = None
        try:
            lh = DepartmentHead.objects.filter(employee=employee).last()
        except: pass
        if lh and not lh.end_date:
            return lh.department
        return None


class AttendanceReport:

    def __init__(self, shift:WorkShift, from_date=None, end_date=None) -> None:
        self.shift = shift
        if not any([from_date, end_date]):
            end_date = timezone.now().date()
            from_date = end_date - timedelta(days=30)
        if not from_date and end_date:
            from_date = end_date - timedelta(days=30)
        attendance_list = self.shift.attendance_list.filter(date__gte=from_date, date__lte=end_date)
        employees = self.shift.employee_set.all()
        self.total_employees:int = self.shift.employee_set.count()
        self.total_work_hours = sum([a.shift.work_hours for a in attendance_list])
        self.actual_work_hours = sum([a.work_hours for a in attendance_list])       
class StaffTeam(models.Model):
    team_name = models.CharField(max_length=1000, blank=True)   
    department = models.ForeignKey(to=Department, on_delete=models.CASCADE)
    registered_on = models.DateTimeField(null=True)

    def __str__(self):
        return  str(self.team_name)
