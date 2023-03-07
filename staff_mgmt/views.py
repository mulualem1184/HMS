import datetime
from datetime import date, timedelta
from typing import Sequence

from core.models import Patient
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from notification.models import notify

from staff_mgmt.decorators import (can_approve_document, can_create_workshift,
                                   can_toggle_leave_request,
                                   department_head_or_staff_required)
from staff_mgmt.forms import (ChangePasswordForm, DepartmentForm,
                              DesignationForm, EmployeeDocumentForm,
                              EmployeeForm, FilterScheduleForm, LeaveForm,
                              ResetPasswordForm, UpdateAttendanceForm,
                              UpdateDepartmentHeadForm, UserForm,
                              WorkShiftForm,MedicalWritePermissionForm,MedicalViewPermissionForm,
                              ComponentPermissionForm,LaboratoryViewPermissionForm,
                              SettingPermissionForm,LaboratoryWritePermissionForm,BillingWritePermissionForm
                              ,BillingViewPermissionForm,SettingPermissionForm,PharmacyPermissionForm,
                              WardPermissionForm,OtherViewPermissionForm,OtherWritePermissionForm)
from staff_mgmt.utils import (TimeOverlapError, generate_random_color,
                              get_time_difference,save_permission_form)

from . import tasks as bg_tasks
from .models import (Attendance, AttendanceReport, Department, DepartmentHead,
                     Designation, Employee, EmployeeDocument, ShiftType,
                     StaffLeave, WorkShift,Permissions,MedicalPermission)



class AddDepartment(View):

    def get(self, *args, **kwargs):
        department_form = DepartmentForm()
        return render(self.request, 'add_department.html', {
            'department_form': department_form,
        })

    def post(self, *args, **kwargs):
        department_form = DepartmentForm(data=self.request.POST)
        if department_form.is_valid():
            department_form.save()
            messages.success(self.request, "Department added successfully.")
            return redirect('staff:add_department') # or redirect to department list view
        else:
            messages.error(self.request, "Error while creating department.")
            messages.error(self.request, "HINT: check if a department with the same name already exists.")
            return redirect('staff:add_department')


class EditDepartment(View):

    def get(self, *args, **kwargs):
        department_id = kwargs['dep_id']
        dpt = get_object_or_404(Department, id=department_id)
        department_form = DepartmentForm(instance=dpt)
        return render(self.request, 'edit_department.html', {
            'department_form': department_form,
        })

    def post(self, *args, **kwargs):
        department_id = kwargs['dep_id']
        dpt = get_object_or_404(Department, id=department_id)
        department_form = DepartmentForm(instance=dpt, data=self.request.POST)
        if department_form.is_valid():
            department_form.save()
            messages.success(self.request, 'Department edited successfully.')
            return redirect('staff:add_department') # to-do redirect to department list view
        else:
            messages.error(self.request, 'Error while editing department')
            messages.error(self.request, "HINT: check if a department with the same name already exists.")
            return redirect('staff:edit_department', department_id) # to-do redirect to department list view


class ListDepartment(View):

    def get(self, *args, **kwargs):
        return render(self.request, 'list_department.html', {
            'dept_list': Department.objects.all(),
        })


class RemoveDepartment(View):

    def get(self, *args, **kwargs):
        department_id = kwargs['dep_id']
        dpt = get_object_or_404(Department, id=department_id)
        dpt.delete()
        messages.success(self.request, 'Department deleted.')
        return redirect('staff:list_department')


class AddDesignation(View):

    def get(self, *args, **kwargs):
        designation_form = DesignationForm()
        designation_list = Designation.objects.all()
        return render(self.request, 'add_designation.html', {
            'designation_form': designation_form,
            'designation_list': designation_list,
        })

    def post(self, *args, **kwargs):
        designation_form = DesignationForm(data=self.request.POST)
        if designation_form.is_valid():
            designation_form.save()
            messages.success(self.request, "Designation added successfully.")
            return redirect('staff:add_designation')
        else:
            messages.error(self.request, "Error while creating designation.")
            return redirect('staff:add_designation')


class ListDesignation(View):

    def get(self, *args, **kwargs):
        return render(self.request, 'list_designation.html', {
            'designation_list': Designation.objects.all(),
        })


class EditDesignation(View):

    def get(self, *args, **kwargs):
        designation_id = kwargs['desig_id']
        designation = get_object_or_404(Designation, id=designation_id)
        desig_form = DesignationForm(instance=designation)
        return render(self.request, 'edit_designation.html', {
            'desig_form': desig_form,
        })

    def post(self, *args, **kwargs):
        desig_id = kwargs['desig_id']
        desig = get_object_or_404(Designation, id=desig_id)
        desig_form = DesignationForm(instance=desig, data=self.request.POST)
        if desig_form.is_valid():
            desig_form.save()
            messages.success(self.request, 'Designation edited successfully.')
            return redirect('staff:list_designation') 
        else:
            messages.error(self.request, 'Error while editing Designation')
            messages.error(self.request, "HINT: check if a Designation with the same name already exists.")
            return redirect('staff:edit_designation', desig_id)

    
class RemoveDesignation(View):

    def get(self, *args, **kwargs):
        desig_id = kwargs['desig_id']
        desig = get_object_or_404(Designation, id=desig_id)
        desig.delete()
        messages.success(self.request, 'Designation deleted.')
        return redirect('staff:list_designation')


class EmployeeList(View):

    def get(self, *args, **kwargs):
        return render(self.request, 'employee_list.html',{
            'employee_list': Employee.objects.all(),
        })


class EmployeeAttendance(View):

    def get(self, *args, **kwargs):
        emp_id = kwargs['emp_id']
        emp = get_object_or_404(Employee, employee_id=emp_id)
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
        attendance_list = Attendance.objects.filter(employee=emp, date__range=[start_date, end_date])
        emp_shift = emp.shift_set.all()
        return render(self.request, 'attendance_list.html', {
            'attendance_list': attendance_list,
            'employee_shift': emp_shift,
        })


class AddEmployee(View):

    def get(self, *args, **kwargs):
        user_form = UserForm()
        employee_form = EmployeeForm()
        return render(self.request, 'add_employee.html', {
            'user_form': user_form,
            'employee_form': employee_form,
        })

    def post(self, *args, **kwargs):
        user_form = UserForm(data=self.request.POST, files=self.request.FILES)
        employee_form = EmployeeForm(data=self.request.POST)
        if employee_form.is_valid():
            if user_form.is_valid():
                user = user_form.save()
                employee = employee_form.save(commit=False)
                employee.user_profile = user
                employee.save()
                messages.success(self.request, "Employee saved successfully")
                return redirect('staff:list_employee') # employee_info page
            else:
                messages.error(self.request, "Error while creating employee")
                return render(self.request, 'add_employee.html', {
                    'user_form': user_form,
                    'employee_form': employee_form,
                })
        else:
            for error in employee_form.errors:
                messages.error(self.request, f"{error}: {employee_form.errors[error].as_text()}")
            return render(self.request, 'add_employee.html', {
                'user_form': user_form,
                'employee_form': employee_form,
            })


class EditEmployee(View):

    def get(self, *args, **kwargs):
        emp_id = kwargs['emp_id'].upper()
        employee:Employee = get_object_or_404(Employee, employee_id=emp_id)
        user_form = UserForm(instance=employee.user_profile)
        # remove fields that are not going to be edited
        user_form.fields.pop('password')
        employee_form = EmployeeForm(instance=employee)
        return render(self.request, 'edit_employee.html', {
            'user_form': user_form,
            'employee_form': employee_form,
        })

    def post(self, *args, **kwargs):
        emp_id = kwargs['emp_id'].upper()
        employee:Employee = get_object_or_404(Employee, employee_id=emp_id)
        user_form = UserForm(instance=employee.user_profile, data=self.request.POST, files=self.request.FILES)
        employee_form = EmployeeForm(instance=employee, data=self.request.POST)
        # remove fields that are not going to be edited
        user_form.fields.pop('password')
        if user_form.is_valid():
            user_form.save(update=True)
            messages.success(self.request, "Employee edited successfully")
        else:
            for error in user_form.errors:
                messages.error(self.request, f'{error}: {user_form.errors[error].as_text()}')
                print(dir(user_form.errors[error]))
        if employee_form.is_valid():
            employee_form.save()
        else:
            for error in user_form.errors:
                messages.error(self.request, user_form.errors[error])
        employee.refresh_from_db()
        return redirect('staff:edit_employee', employee.employee_id)


class AddEmployeeDocument(View):

    def post(self, *args, **kwargs):
        id = kwargs['id']
        emp:Employee = get_object_or_404(Employee, id=id)
        document_form = EmployeeDocumentForm(data=self.request.POST, files=self.request.FILES)
        if document_form.is_valid():
            doc = EmployeeDocument(employee=emp, document_name=document_form.data['document_name'], document=document_form.files['document'])
            doc.save()
            messages.success(self.request, "Document added successfully")
        return redirect('staff:view_employee', emp.id)


class EmployeeProfile(View):

    def get(self, *args, **kwargs):
        id = kwargs['id']
        emp = get_object_or_404(Employee, id=id) # or replace with `employee_id=id`
        document_form = EmployeeDocumentForm(initial={'employee':emp.id})
        password_form = ResetPasswordForm()
        if emp.user_profile == self.request.user:
            password_form = ChangePasswordForm()
        return render(self.request, "employee_profile.html", {
            'employee': emp,
            'employee_documents': emp.document_set.all(),
            'document_form': document_form,
            'password_form': password_form,
        })


class ChangePassword(View):
    
    def post(self, *args, **kwargs):
        password_form = None
        logged_in_user = self.request.user
        if 'id' in kwargs:
            emp = get_object_or_404(Employee, id=kwargs['id'])
            if emp.user_profile == logged_in_user:
                password_form = ChangePasswordForm(data=self.request.POST)
                current_password = password_form.data['current_password']
                new_password = password_form.data['new_password']
                if logged_in_user.check_password(current_password):
                    logged_in_user.set_password(new_password)
                    logged_in_user.save()
                    messages.success(self.request, "Password changed")
                    return redirect('staff:view_employee', emp.id)
                else:
                    messages.error(self.request, "Wrong current password")
                    return redirect('staff:view_employee', emp.id)
            else:
                # reset password
                password_form = ResetPasswordForm(data=self.request.POST)
                password = password_form.data['password']
                user_profile = emp.user_profile
                user_profile.set_password(password)
                user_profile.save()
                messages.success(self.request, "password reseted")
                return redirect('staff:view_employee', emp.id)


class ToggleActiveStatus(View):

    def get(self, *args, **kwargs):
        id = kwargs['id']
        emp = get_object_or_404(Employee, id=id)
        user = emp.user_profile
        user.is_active = not user.is_active
        user.save()
        messages.success(self.request, "Updated active status")
        return redirect('staff:view_employee', id)


class RemoveEmployee(View):

    def get(self, *args, **kwargs):
        id = kwargs['id']
        emp = get_object_or_404(Employee, id=id)
        user = emp.user_profile
        user.delete()
        messages.success(self.request, 'Employee data deleted.')
        return redirect('staff:list_employee')


class RemoveDocument(View):

    @method_decorator(can_approve_document())
    def get(self, *args, **kwargs):
        id = kwargs['id']
        doc = get_object_or_404(EmployeeDocument, id=id)
        doc.delete()
        notify(doc.employee.user_profile, 'info', f'{doc.document_name} document declined')
        messages.success(self.request, "Document removed")
        return redirect('staff:view_employee', doc.employee.id)


class RequestLeave(View):

    def get(self, *args, **kwargs):
        id = kwargs['id']
        emp = get_object_or_404(Employee, id=id)
        leave_list = StaffLeave.objects.filter(employee=emp)
        llr:StaffLeave = leave_list.last()
        if llr.status in ['APPROVED', 'PENDING']:
            if not (llr.from_date - timezone.now().date()).days >= 0:
                messages.error(self.request, 'Can not make a new leave request.')
                return redirect('staff:view_employee', emp.id)
        leave_form = LeaveForm(initial={
            'employee': emp.id,
            'from_date': datetime.date.today(),
            'to_date': datetime.date.today() + timedelta(days=10),
        })
        return render(self.request, 'request_leave.html', {
            'leave_form': leave_form,
            'leave_list': leave_list,
        })

    def post(self, *args, **kwargs):
        id = kwargs['id']
        emp = get_object_or_404(Employee, id=id)
        leave_form = LeaveForm(data=self.request.POST)
        if leave_form.is_valid():
            staff_leave = leave_form.save(commit=False)
            staff_leave.employee = emp
            staff_leave.save()
            messages.success(self.request, "Leave request submitted")
            return redirect('staff:view_employee', emp.id)
        else:
            return render(self.request, 'request_leave.html', {
                'leave_form': leave_form,
            })


class ViewLeaveRequest(View):

    @method_decorator(can_toggle_leave_request())
    def get(self, *args, **kwargs):
        id = kwargs['id']
        lr = get_object_or_404(StaffLeave, id=id)
        return render(self.request, 'view_leave_request.html', {
            'lr': lr
        })


class LeaveRequestList(View):

    @method_decorator(login_required)
    def get(self, *args, **kwargs):
        user = self.request.user
        emp = None
        department = None
        request_list = []
        #    request_list = StaffLeave.objects.filter(employee__designation__department=department)
        """
        try:
            emp = user.employee
            department = DepartmentHead.is_employee_department_head(emp)
            #if department:
            request_list = StaffLeave.objects.filter(employee__designation__department=department)
            #else: 
            #    messages.error(self.request, 'Permission Denied; Could not show you leave request list')
            return render(self.request, 'leave_request_list.html', {
                'request_list': request_list
            })
        except: pass
        """
        request_list = StaffLeave.objects.all()
        return render(self.request, 'leave_request_list.html', {
            'request_list': request_list
        })


class ApproveLeaveRequest(View):

    @method_decorator(can_toggle_leave_request())
    def get(self, *args, **kwargs):
        id = kwargs['id']
        lr = get_object_or_404(StaffLeave, id=id)
        if not (lr.from_date - timezone.now().date()).days >= 0:
            messages.error(self.request, 'Leave request has expired; can not make updates.')
            return redirect('staff:leave_request_list')
        else:
            lr.status = 'APPROVED'
            lr.save()
            lr.employee.on_leave = True
            lr.employee.save()
            bg_tasks.schedule_leave_status_updater(lr)
            messages.success(self.request, "Leave request approved")
            return redirect('staff:leave_request_list')


class DenyLeaveRequest(View):

    @method_decorator(can_toggle_leave_request())
    def get(self, *args, **kwargs):
        id = kwargs['id']
        lr = get_object_or_404(StaffLeave, id=id)
        if not (lr.from_date - timezone.now().date()).days >= 0:
            messages.error(self.request, 'Leave request has expired; can not make updates.')
            return redirect('staff:leave_request_list')
        else:
            lr.status = 'DECLINED'
            lr.save()
            lr.employee.on_leave = False
            lr.employee.save()
            bg_tasks.cancel_scheduled_leave_update(lr.id)
            messages.success(self.request, "Leave request declined")
            return redirect('staff:leave_request_list')


class AddWorkShift(View):
    post_decorators = [login_required, can_create_workshift()]

    @method_decorator(login_required)
    def get(self, *args, **kwargs):
        shift_form = WorkShiftForm(initial={
            'start_time': '02:00:00',
            'end_time': '11:00:00',
        })
        return render(self.request, 'add_workshift.html', {
            'shift_form': shift_form,
        })

    @method_decorator(post_decorators)
    def post(self, *args, **kwargs):
        shift_form = WorkShiftForm(data=self.request.POST)
        if shift_form.is_valid():
            try:
                shift_form.save()
            except TimeOverlapError:
                messages.error(self.request, "entered time overlaps with previous shifts")
                return render(self.request, 'add_workshift.html', {
                    'shift_form': shift_form,
                })
            except Exception as e:
                messages.error(self.request, str(e))
                return render(self.request, 'add_workshift.html', {
                    'shift_form': shift_form,
                })
            messages.success(self.request, 'Work Shift added')
            return redirect('staff:add_workshift')
        else:
            messages.error(self.request, "wrong time format")
            return render(self.request, 'add_workshift.html', {
                'shift_form': shift_form,
            })

@method_decorator([login_required, department_head_or_staff_required()], 'dispatch')
class EditWorkShift(View):

    def get(self, *args, **kwargs):
        id = kwargs['id']
        ws = get_object_or_404(WorkShift, id=id)
        shift_form = WorkShiftForm(instance=ws)
        return render(self.request, 'edit_workshift.html', {
            'shift_form': shift_form,
        })

    def post(self, *args, **kwargs):
        id = kwargs['id']
        ws = get_object_or_404(WorkShift, id=id)
        shift_form = WorkShiftForm(instance=ws, data=self.request.POST)
        if shift_form.is_valid():
            shift_form.save()
            messages.success(self.request, "Workshift edited")
            return redirect('staff:list_workshift')
        messages.error(self.request, "Error while editing shift info")
        return render(self.request, 'edit_workshift.html', {
            'shift_form': shift_form,
        })


class RemoveWorkShift(View):

    @method_decorator(department_head_or_staff_required())
    def get(self, *args, **kwargs):
        id = kwargs['id']
        ws = get_object_or_404(WorkShift, id=id)
        ws.delete()
        messages.success(self.request, "Workshift deleted")
        return redirect('staff:list_workshift')


class ListWorkShift(View):

    def get(self, *args, **kwargs):
        return render(self.request, 'list_workshift.html', {
            'ws_list': WorkShift.objects.all().order_by('day')
        })


@method_decorator([login_required, department_head_or_staff_required()], 'dispatch')
class AssignEmployeesToShift(View):

    def get(self, *args, **kwargs):
        shift_id = kwargs['id']
        shift = get_object_or_404(WorkShift, id=shift_id)
        employee_list = Employee.objects.filter(designation__department=shift.shift_type.department)
        current_employee_id_list = [e.id for e in shift.employee_set.all() ]
        return render(self.request, 'employee_to_shift.html', {
            'shift': shift,
            'employee_list': employee_list,
            'current_employees': current_employee_id_list,
        })

    def post(self, *args, **kwargs):
        shift_id = kwargs['id']
        shift = get_object_or_404(WorkShift, id=shift_id)
        selected_ids = [ int(x) for x in self.request.POST.getlist('employee') ]
        employee_list:Sequence[Employee] = Employee.objects.all()
        for e in employee_list:
            if e.id in selected_ids:
                e.shift_set.add(shift)
            else:
                e.shift_set.remove(shift)
            e.save()
        return redirect('staff:assign_shift', shift.id)


class DailyAttendanceView(View):

    def get(self, *args, **kwargs):
        attendance_list = []
        day = timezone.now().weekday()
        today_shifts = WorkShift.objects.filter(day=day)
        for shift in today_shifts:
            for e in shift.employee_set.all():
                att, _ = Attendance.objects.get_or_create(employee=e, shift=shift, date=date.today())
                # if is_created:
                #     att.start_time = shift.start_time
                #     att.save()
                attendance_list.append(att)
        return render(self.request, 'attendance.html', {
            'attendance_list': attendance_list,
        })


class UpdateAttendance(View):

    def post(self, *args, **kwargs):
        id = kwargs['id']
        att = get_object_or_404(Attendance, id=id)
        att_form = UpdateAttendanceForm(instance=att, data=self.request.POST)
        if att_form.is_valid():
            att_form.save()
        else:
            messages.error(self.request, "Error Saving attendance")
            return redirect('staff:daily_attendance')
        messages.success(self.request, "Attendance Updated")
        return redirect('staff:daily_attendance')


class AttendanceView(View):

    def get(self, *args, **kwargs):
        day = timezone.now().weekday()
        today_shifts = WorkShift.objects.filter(day=day)
        return render(self.request, 'attendance.html', {
            'shifts': today_shifts
        })


class CloseAttendance(View):
    
    def get(self, *args, **kwargs):
        employee = None
        try:
            employee = self.request.user.employee
        except:
            return redirect('core:logout')
        attendance_list:Sequence[Attendance] = Attendance.objects.filter(date=timezone.now().date(), employee=employee)
        current_time = timezone.now().time()
        current_att = None
        if not attendance_list:
            messages.error(self.request, 'No attendance record been created.')
            return redirect('staff:daily_attendance') # to-do error page
        for att in attendance_list:
            if get_time_difference(att.start_time, current_time):
                current_att = att
        current_att.end_time = current_time
        current_att.save()
        messages.success(self.request, "Attendance updated.")
        return redirect('staff:daily_attendance') # to-do users dashboard


class ShiftReport(View):

    def get(self, *args, **kwargs):
        filters = {}
        dept_id = self.request.GET.get('dept')
        dept = None
        try:
            dept = Department.objects.get(id=dept_id)
            filters.update({'shift_type__department': dept})
        except:
            pass
        shift_list = WorkShift.objects.filter(**filters)
        report_list:Sequence[AttendanceReport] = []
        for shift in shift_list:
            report_list.append(AttendanceReport(shift))
        return render(self.request, 'shift_report.html', {
            'report_list': report_list,
        })

class ApproveDocument(View):

    @method_decorator(can_approve_document())
    def get(self, *args, **kwargs):
        id = kwargs['id']
        document = get_object_or_404(EmployeeDocument, id=id)
        if not document.approved:
            document.approved = True
            document.approved_by = self.request.user
            document.save()
        elif document.approved_by == self.request.user:
            document.approved = False
            document.approved_by = None
            document.save()
        messages.success(self.request, "Documents approval status updated.")
        return redirect('staff:view_employee', document.employee.id)


class Schedule(View):

    def get(self, *args, **kwargs):
        filter_form = FilterScheduleForm(self.request.GET)
        today = timezone.now().date()
        shift_type = None
        events = []
        dept_id = int(self.request.GET.get('department', 0) or 0)
        try:
            if dept_id:
                department = Department.objects.get(id=dept_id)
                shift_type = ShiftType.objects.get(department=department)
        except: pass
        month = int(self.request.GET.get('month', 0))
        if month and month > 0 and month <= 12:
             today = datetime.date(today.year, int(month), 1) # construct date with the new month
        shifts = WorkShift.objects.all()
        if shift_type:
            shifts = shifts.filter(shift_type=shift_type)
        for i in range(40):
            d = today + timedelta(days=i)
            day_shifts:Sequence[WorkShift] = shifts.filter(day=d.weekday())
            for shift in day_shifts:
                shift_workers = shift.employee_set.all()
                for e in shift_workers:
                    color = generate_random_color()
                    if StaffLeave.check_leave(e, d):
                        color = 'red'
                        events.append({
                            'title': e.full_name,
                            'url': reverse('staff:view_employee', args=[e.id]),
                            'start': str(d),
                            'end': str(d + timedelta(days=1)),
                            'backgroundColor': color,
                        })
                        events.append({
                            'title': "On leave",
                            'start': str(d),
                            'end': str(d + timedelta(days=1)),
                            'backgroundColor': color,
                        })
                        continue
                    events.append({
                        'title': e.full_name,
                        'url': reverse('staff:view_employee', args=[e.id]),
                        'start': str(d),
                        'end': str(d + timedelta(days=1)),
                        'backgroundColor': color,
                        'groupId': f'{e.id}'
                    })
                    events.append({
                        'title': f'{shift.start_time}-{shift.end_time}',
                        'start': str(d),
                        'end': str(d + timedelta(days=1)),
                        'backgroundColor': color,
                        'groupId': f'{shift.id}'
                    })
        return render(self.request, 'schedule.html', {
            'events': str(events),
            'filter_form': filter_form,
            'initial_date': str(today),
        })


class Dashboard(View):
    
    def get(self, *args, **kwargs):
        employees = Employee.objects.all()
        new_patients:int = Patient.objects.filter(registered_at__date=timezone.now().date()).count()
        today_attendance = Attendance.objects.filter(date=timezone.now().date())
        total_needed_employees:int = today_attendance.count()
        employees_present = len([x for x in today_attendance if x.is_present ])
        return render(self.request, 'staff_dashboard.html', {
            'employees': employees,
            'employees_present': employees_present,
            'total_needed_employees': total_needed_employees,
            'new_patients': new_patients,
        })


class UpdateDepartmentHead(View):

    def get(self, *args, **kwargs):
        department = get_object_or_404(Department, id=kwargs['id'])
        head = DepartmentHead.get_department_head(department)
        dh_info = DepartmentHead.objects.filter(department=department)
        u_form = UpdateDepartmentHeadForm()
        qs = Employee.objects.all()
        emp_ids = [e.id for e in qs if e.department.id == department.id]
        u_form.fields['employee'].queryset = qs.filter(id__in=emp_ids)
        if not head:
            pass
        return render(self.request, 'update_department_head.html', {
            'dh_info': dh_info,
            'head': head,
            'update_form': u_form,
            'department': department, 
        })

    def post(self, *args, **kwargs):
        department = get_object_or_404(Department, id=kwargs['id'])
        u_form = UpdateDepartmentHeadForm(data=self.request.POST)
        if u_form.is_valid():
            dh:DepartmentHead = DepartmentHead.objects.filter(department=department).last()
            # if dh:
            #     dh.delete()
            employee = u_form.cleaned_data['employee']
            if dh:
                if dh.employee.id == employee.id:
                    messages.info(self.request, f'{employee.full_name} is already the Department Head.')
                    return redirect('staff:update_department_head', department.id)
            DepartmentHead.objects.create(
                department=department, employee=employee,
                assigned_by=self.request.user,
            )
            messages.success(self.request, f"Department Head assigned for {str(department)}")
            return redirect('staff:update_department_head', department.id)
        else:
            messages.error(self.request, "Error while assigning department head")
            return redirect('staff:update_department_head', department.id)



class AssignPrevilages(View):

    def get(self, *args, **kwargs):
        designation_id = kwargs['designation_id']
        designation = Designation.objects.get(id=designation_id)
        #specimen_list = Specimen.objects.first().patient_specimens(patient_id)
        """
        try:
            des = designation.permission.medical
            print('exists')
            medical_form = MedicalPermissionForm(designation_id=designation_id)
            
        except Exception as e:
            raise e
            #medical_form = MedicalPermissionForm()
        """
        medical_form = MedicalViewPermissionForm(designation_id=designation_id)
        medical_write_form = MedicalWritePermissionForm(designation_id=designation_id)
        component_form = ComponentPermissionForm(designation_id=designation_id)
        laboratory_view_form = LaboratoryViewPermissionForm(designation_id=designation_id)
        laboratory_write_form = LaboratoryWritePermissionForm(designation_id=designation_id)
        setting_form = SettingPermissionForm(designation_id=designation_id)
        billing_write_form = BillingWritePermissionForm(designation_id=designation_id)
        billing_view_form = BillingViewPermissionForm(designation_id=designation_id)
        pharmacy_form = PharmacyPermissionForm(designation_id=designation_id)
        ward_form = WardPermissionForm(designation_id=designation_id)
        other_form = OtherViewPermissionForm(designation_id=designation_id)

        print(self.request.user.employee.designation)
        """
        for f in medical_form:
            print(f,'\n')
        """
        context = {'designation':designation,
                    'medical_form':medical_form,
                    'component_form':component_form,
                    'laboratory_view_form':laboratory_view_form,
                    'laboratory_write_form':laboratory_write_form,
                    'setting_form':setting_form,
                    'billing_write_form':billing_write_form,
                    'billing_view_form':billing_view_form,
                    'other_form':other_form,

                    }

        return render(self.request, 'assign_previlages.html',context)
    
    def post(self, *args, **kwargs):
        designation_id = kwargs['designation_id']
        designation = Designation.objects.get(id=designation_id)
        medical_form = MedicalViewPermissionForm(self.request.POST,designation_id=designation_id)
        component_form = ComponentPermissionForm(self.request.POST,designation_id=designation_id)
        laboratory_view_form = LaboratoryViewPermissionForm(self.request.POST,designation_id=designation_id)
        setting_form = SettingPermissionForm(self.request.POST,designation_id=designation_id)
        billing_write_form = BillingWritePermissionForm(self.request.POST,designation_id=designation_id)
        billing_view_form = BillingViewPermissionForm(self.request.POST,designation_id=designation_id)
        pharmacy_form = PharmacyPermissionForm(self.request.POST,designation_id=designation_id)
        ward_form = WardPermissionForm(self.request.POST,designation_id=designation_id)
        other_form = OtherViewPermissionForm(self.request.POST,designation_id=designation_id)

        try:
            permissions = designation.permission
        except:
            permissions = Permissions()

        if medical_form.has_changed():
            #save_permission_form(self,medical_form,designation,'M')
            #print('reached')
            
            if medical_form.is_valid():
                medical_form1 = medical_form.save(commit=False)
                try:
                    medical = designation.permission.medical
                    for f in medical_form.changed_data:
                        print(medical_form.changed_data,'\n')
                        field = str(f)
                        print(f,field,'\n')
                        try:
                            print(self.request.POST[f],'\n')
                            if self.request.POST[f] == 'on':
                                value = True
                        except Exception as e:
                            value = False
                        setattr(medical,f,value)                
                        print('has reached')

                    medical.save()
                    messages.success(self.request, "Permission Given successfully!")
                    return redirect('staff:assign_previlages', designation.id)
                    
                except:
                    if permissions == None:
                        permissions = Permissions()
                    permissions.medical = medical_form1
                    designation.permission = permissions
                    medical_form1.save()
                    permissions.save()
                    designation.save()

                    messages.success(self.request, "Permission Given successfully!")
                    return redirect('staff:assign_previlages', designation.id)
            else:
                print('Form Errors:', medical_form.errors)
                messages.error(self.request, medical_form.errors)
                return redirect('staff:assign_previlages',designation_id)
            
        if component_form.has_changed():
            if component_form.is_valid():
                component_form1 = component_form.save(commit=False)
                try:
                    component = designation.permission.component
                    for f in component_form.changed_data:
                        print(component_form.changed_data,'\n')
                        try:
                            if self.request.POST[f] == 'on':
                                value = True
                        except Exception as e:
                            value = False
                        setattr(component,f,value)                
                    component.save()
                    messages.success(self.request, "Permission Given successfully!")
                    return redirect('staff:assign_previlages', designation.id)
                    
                except:
                    if permissions == None:
                        permissions = Permissions()

                    permissions.component = component_form1
                    designation.permission = permissions
                    component_form1.save()
                    permissions.save()
                    designation.save()
                    messages.success(self.request, "Component Permission Given successfully!")
                    return redirect('staff:assign_previlages', designation.id)
            else:
                print('Form Errors:', component_form.errors)
                messages.error(self.request, component_form.errors)
                return redirect('staff:assign_previlages',designation_id)
        if laboratory_view_form.has_changed():
            print('b changed')
            if laboratory_view_form.is_valid():
                laboratory_view_form1 = laboratory_view_form.save(commit=False)
                try:
                    laboratory_view = designation.permission.laboratory
                    for f in laboratory_view_form.changed_data:
                        print(laboratory_view_form.changed_data,'\n')
                        try:
                            if self.request.POST[f] == 'on':
                                value = True
                        except Exception as e:
                            value = False
                        setattr(laboratory_view,f,value)                
                    laboratory_view.save()
                    messages.success(self.request, "Permission Given successfully!")
                    return redirect('staff:assign_previlages', designation.id)
                    
                except Exception as e:
                    permissions.laboratory = laboratory_view_form1
                    designation.permission = permissions
                    laboratory_view_form1.save()
                    permissions.save()
                    designation.save()
                    messages.success(self.request, "Permission Given successfully!")
                    return redirect('staff:assign_previlages', designation.id)
            else:
                print('Form Errors:', laboratory_view_form.errors)
                messages.error(self.request, laboratory_view_form.errors)
                return redirect('staff:assign_previlages',designation_id)
        if billing_view_form.has_changed():
            print('b changed')
            if billing_view_form.is_valid():
                billing_view_form1 = billing_view_form.save(commit=False)
                try:
                    billing_view = designation.permission.billing
                    for f in billing_view_form.changed_data:
                        print(billing_view_form.changed_data,'\n')
                        try:
                            if self.request.POST[f] == 'on':
                                value = True
                        except Exception as e:
                            value = False
                        setattr(billing_view,f,value)                
                    billing_view.save()
                    messages.success(self.request, "Permission Given successfully!")
                    return redirect('staff:assign_previlages', designation.id)
                    
                except Exception as e:

                    permissions.billing = billing_view_form1
                    designation.permission = permissions
                    billing_view_form1.save()
                    permissions.save()
                    designation.save()
                    messages.success(self.request, "Component Permission Given successfully!")
                    return redirect('staff:assign_previlages', designation.id)
            else:
                print('Form Errors:', billing_view_form.errors)
                messages.error(self.request, billing_view_form.errors)
                return redirect('staff:assign_previlages',designation_id)



class AssignWritePrevilages(View):

    def get(self, *args, **kwargs):
        designation_id = kwargs['designation_id']
        designation = Designation.objects.get(id=designation_id)
        medical_write_form = MedicalWritePermissionForm(designation_id=designation_id)
        laboratory_write_form = LaboratoryWritePermissionForm(designation_id=designation_id)
        setting_form = SettingPermissionForm(designation_id=designation_id)
        billing_write_form = BillingWritePermissionForm(designation_id=designation_id)
        pharmacy_form = PharmacyPermissionForm(designation_id=designation_id)
        ward_form = WardPermissionForm(designation_id=designation_id)
        other_form = OtherWritePermissionForm(designation_id=designation_id)

        """
        for f in medical_form:
            print(f,'\n')
        """
        context = {'designation':designation,
                    'medical_write_form':medical_write_form,
                    'laboratory_write_form':laboratory_write_form,
                    'setting_form':setting_form,
                    'billing_write_form':billing_write_form,
                    'pharmacy_form':pharmacy_form,
                    'ward_form':ward_form,
                    'other_form':other_form,
                    }

        return render(self.request, 'assign_write_previlages.html',context)

    def post(self, *args, **kwargs):
        designation_id = kwargs['designation_id']
        designation = Designation.objects.get(id=designation_id)
        medical_form = MedicalWritePermissionForm(self.request.POST,designation_id=designation_id)
        laboratory_form = LaboratoryWritePermissionForm(self.request.POST,designation_id=designation_id)
        setting_form = SettingPermissionForm(self.request.POST,designation_id=designation_id)
        billing_form = BillingWritePermissionForm(self.request.POST,designation_id=designation_id)
        pharmacy_form = PharmacyPermissionForm(self.request.POST,designation_id=designation_id)
        ward_form = WardPermissionForm(self.request.POST,designation_id=designation_id)
        other_form = OtherWritePermissionForm(self.request.POST, designation_id=designation_id)

        try:
            permissions = designation.permission
        except:
            permissions = Permissions()

        if medical_form.has_changed():
            #save_permission_form(self,medical_form,designation,'M')
            #print('reached')
            
            if medical_form.is_valid():
                medical_form1 = medical_form.save(commit=False)
                try:
                    medical = designation.permission.medical
                    for f in medical_form.changed_data:
                        print(medical_form.changed_data,'\n')
                        field = str(f)
                        print(f,field,'\n')
                        try:
                            print(self.request.POST[f],'\n')
                            if self.request.POST[f] == 'on':
                                value = True
                        except Exception as e:
                            value = False
                        setattr(medical,f,value)                
                        print('has reached')

                    medical.save()
                    messages.success(self.request, "Permission Given successfully!")
                    return redirect('staff:assign_write_previlages', designation.id)
                    
                except:
                    if permissions == None:
                        permissions = Permissions()
                    permissions.medical = medical_form1
                    designation.permission = permissions
                    medical_form1.save()
                    permissions.save()
                    designation.save()

                    messages.success(self.request, "Permission Given successfully!")
                    return redirect('staff:assign_write_previlages', designation.id)
            else:
                print('Form Errors:', medical_form.errors)
                messages.error(self.request, medical_form.errors)
                return redirect('staff:assign_write_previlages',designation_id)


        if ward_form.has_changed():
            
            if ward_form.is_valid():
                ward_form1 = ward_form.save(commit=False)
                try:
                    ward = designation.permission.ward
                    for f in ward_form.changed_data:
                        print(ward_form.changed_data,'\n')
                        field = str(f)
                        print(f,field,'\n')
                        try:
                            print(self.request.POST[f],'\n')
                            if self.request.POST[f] == 'on':
                                value = True
                        except Exception as e:
                            value = False
                        setattr(ward,f,value)                
                        print('has reached')

                    ward.save()
                    messages.success(self.request, "Permission Given successfully!")
                    return redirect('staff:assign_write_previlages', designation.id)
                    
                except:
                    if permissions == None:
                        permissions = Permissions()
                    permissions.ward = ward_form1
                    designation.permission = permissions
                    ward_form1.save()
                    permissions.save()
                    designation.save()

                    messages.success(self.request, "Permission Given successfully!")
                    return redirect('staff:assign_write_previlages', designation.id)
            else:
                print('Form Errors:', ward_form.errors)
                messages.error(self.request, ward_form.errors)
                return redirect('staff:assign_write_previlages',designation_id)


        if laboratory_form.has_changed():
            
            if laboratory_form.is_valid():
                laboratory_form1 = laboratory_form.save(commit=False)
                try:
                    laboratory = designation.permission.laboratory
                    for f in laboratory_form.changed_data:
                        print(laboratory_form.changed_data,'\n')
                        field = str(f)
                        print(f,field,'\n')
                        try:
                            print(self.request.POST[f],'\n')
                            if self.request.POST[f] == 'on':
                                value = True
                        except Exception as e:
                            value = False
                        setattr(laboratory,f,value)                
                        print('has reached')

                    laboratory.save()
                    messages.success(self.request, "Permission Given successfully!")
                    return redirect('staff:assign_write_previlages', designation.id)
                    
                except:
                    if permissions == None:
                        permissions = Permissions()
                    permissions.laboratory = laboratory_form1
                    designation.permission = permissions
                    laboratory_form1.save()
                    permissions.save()
                    designation.save()

                    messages.success(self.request, "Permission Given successfully!")
                    return redirect('staff:assign_write_previlages', designation.id)
            else:
                print('Form Errors:', laboratory_form.errors)
                messages.error(self.request, laboratory_form.errors)
                return redirect('staff:assign_write_previlages',designation_id)

        if setting_form.has_changed():
            #save_permission_form(self,setting_form,designation,'M')
            #print('reached')
            
            if setting_form.is_valid():
                setting_form1 = setting_form.save(commit=False)
                try:
                    setting = designation.permission.setting
                    for f in setting_form.changed_data:
                        print(setting_form.changed_data,'\n')
                        field = str(f)
                        print(f,field,'\n')
                        try:
                            print(self.request.POST[f],'\n')
                            if self.request.POST[f] == 'on':
                                value = True
                        except Exception as e:
                            value = False
                        setattr(setting,f,value)                
                        print('has reached')

                    setting.save()
                    messages.success(self.request, "Permission Given successfully!")
                    return redirect('staff:assign_write_previlages', designation.id)
                    
                except:
                    if permissions == None:
                        permissions = Permissions()
                    permissions.setting = setting_form1
                    designation.permission = permissions
                    setting_form1.save()
                    permissions.save()
                    designation.save()

                    messages.success(self.request, "Permission Given successfully!")
                    return redirect('staff:assign_write_previlages', designation.id)
            else:
                print('Form Errors:', setting_form.errors)
                messages.error(self.request, setting_form.errors)
                return redirect('staff:assign_write_previlages',designation_id)

        if billing_form.has_changed():            
            if billing_form.is_valid():
                billing_form1 = billing_form.save(commit=False)
                try:
                    billing = designation.permission.billing
                    for f in billing_form.changed_data:
                        print(billing_form.changed_data,'\n')
                        field = str(f)
                        print(f,field,'\n')
                        try:
                            print(self.request.POST[f],'\n')
                            if self.request.POST[f] == 'on':
                                value = True
                        except Exception as e:
                            value = False
                        setattr(billing,f,value)                
                        print('has reached')

                    billing.save()
                    messages.success(self.request, "Permission Given successfully!")
                    return redirect('staff:assign_write_previlages', designation.id)
                except:
                    if permissions == None:
                        permissions = Permissions()
                    permissions.billing = billing_form1
                    designation.permission = permissions
                    billing_form1.save()
                    permissions.save()
                    designation.save()

                    messages.success(self.request, "Permission Given successfully!")
                    return redirect('staff:assign_write_previlages', designation.id)
            else:
                print('Form Errors:', billing_form.errors)
                messages.error(self.request, billing_form.errors)
                return redirect('staff:assign_write_previlages',designation_id)

        if pharmacy_form.has_changed():            
            if pharmacy_form.is_valid():
                pharmacy_form1 = pharmacy_form.save(commit=False)
                try:
                    pharmacy = designation.permission.pharmacy
                    for f in pharmacy_form.changed_data:
                        print(pharmacy_form.changed_data,'\n')
                        field = str(f)
                        print(f,field,'\n')
                        try:
                            print(self.request.POST[f],'\n')
                            if self.request.POST[f] == 'on':
                                value = True
                        except Exception as e:
                            value = False
                        setattr(pharmacy,f,value)                
                        print('has reached')

                    pharmacy.save()
                    messages.success(self.request, "Permission Given successfully!")
                    return redirect('staff:assign_write_previlages', designation.id)
                except:
                    if permissions == None:
                        permissions = Permissions()
                    permissions.pharmacy = pharmacy_form1
                    designation.permission = permissions
                    pharmacy_form1.save()
                    permissions.save()
                    designation.save()

                    messages.success(self.request, "Permission Given successfully!")
                    return redirect('staff:assign_write_previlages', designation.id)
            else:
                print('Form Errors:', pharmacy_form.errors)
                messages.error(self.request, pharmacy_form.errors)
                return redirect('staff:assign_write_previlages',designation_id)


@method_decorator(login_required, 'dispatch')
class EditSpecimen2(View):

    def post(self, *args, **kwargs):
        specimen_id = kwargs['specimen_id']

        patient = Patient.objects.get(id=patient_id)
        specimen = Specimen.objects.get(id=specimen_id)
        specimen_form = EditSpecimenForm(self.request.POST,specimen_id=specimen.id)
        if specimen_form.is_valid():
            specimen_form = specimen_form.save(commit=False)            
            specimen.sample_volume = specimen_form.sample_volume
            specimen.save()
            messages.success(self.request, "Specimen info edited successfully!")
            return redirect('specimens', patient.id)
        else:
            print('Specimen Form Errors:', specimen_form.errors)
            messages.error(self.request, specimen_form.errors)
            return redirect('specimens',patient.id)
