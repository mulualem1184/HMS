from django.contrib import admin

from staff_mgmt.models import (Attendance, Department, DepartmentHead,
                               Employee, EmployeeDocument, ShiftType,
                               StaffLeave, WorkShift, Designation,
                               Permissions,MedicalPermission,ComponentPermission,
                               BillingPermission,WardPermission,PharmacyPermission)

admin.site.register([
    Department, Employee, Attendance, 
    WorkShift, EmployeeDocument, StaffLeave,
    ShiftType, DepartmentHead,Designation,Permissions,MedicalPermission,
    ComponentPermission,BillingPermission,WardPermission,PharmacyPermission
])
