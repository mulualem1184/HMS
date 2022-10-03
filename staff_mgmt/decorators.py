from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect

from staff_mgmt.models import DepartmentHead, EmployeeDocument, ShiftType, StaffLeave, WorkShift

from .forms import WorkShiftForm


def can_create_workshift():
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            logged_in_user = request.user
            ws_form = WorkShiftForm(data=request.POST)
            shift_type = ws_form.data['shift_type']
            try:
                shift_type:ShiftType = ShiftType.objects.get(id=shift_type)
            except: pass
            department_head = DepartmentHead.get_department_head(shift_type.department)
            if logged_in_user.is_staff:
                return func(request, *args, **kwargs)
            elif department_head and department_head.user_profile.id == logged_in_user.id:
                return func(request, *args, **kwargs)
            else:
                messages.error(request, f'Permission Denied: Not allowed to create shift for {shift_type.department} department')
                return redirect('staff:add_workshift')
        return wrapper
    return decorator


def staff_required():
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            try:
                logged_in_user = request.user
                if logged_in_user.is_staff:
                    return func(request, *args, **kwargs)
                return HttpResponseForbidden()
            except:
                return HttpResponseForbidden()
        return wrapper
    return decorator


def department_head_or_staff_required():
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            logged_in_user = request.user
            ws_id = kwargs['id']
            ws:WorkShift = WorkShift.objects.get(id=ws_id)
            department = ws.shift_type.department
            dep_head = DepartmentHead.get_department_head(department)
            if logged_in_user.is_staff:
                return func(request, *args, **kwargs)
            elif dep_head and dep_head.user_profile.id == logged_in_user.id:
                 return func(request, *args, **kwargs)
            else:
                messages.error(request, 'Permission Denied: Could not proceed with request')
                return redirect('staff:list_workshift')
        return wrapper
    return decorator


def can_approve_document():
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            logged_in_user = request.user
            doc_id = kwargs['id']
            doc = get_object_or_404(EmployeeDocument, id=doc_id)
            if DepartmentHead.get_department_head(doc.employee.department).user_profile.id == logged_in_user.id:
                return func(request, *args, **kwargs)
            else:
                messages.error(request, 'Permission Denied: Could not proceed with request')
                return redirect('staff:view_employee', doc.employee.id)
        return wrapper
    return decorator


def can_toggle_leave_request():
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            logged_in_user = request.user
            lr = get_object_or_404(StaffLeave, id=kwargs['id'])
            if DepartmentHead.get_department_head(lr.employee.department).user_profile.id == logged_in_user.id:
                return func(request, *args, **kwargs)
            else:
                messages.error(request, 'Permission Denied: Could not proceed with request')
                return redirect('staff:leave_request_list')
        return wrapper
    return decorator