from django.contrib import admin

from staff_mgmt.models import (Attendance, Department, Employee,
                               EmployeeDocument, ShiftType, StaffLeave,
                               WorkShift)

admin.site.register([
    Department, Employee, Attendance, 
    WorkShift, EmployeeDocument, StaffLeave,
    ShiftType
])
