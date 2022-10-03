from core.models import Patient
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .forms import ReportForm, XRayRequestForm
from .models import ImageFile, ImagingReport, Order
from notification.models import notify
from outpatient_app.models import OutpatientRadiologyResult, PatientVisit
from datetime import datetime


class XRayOrder(View):

    def get(self, *args, **kwargs):
        patient_id = kwargs['patient_id']
        patient = get_object_or_404(Patient, id=patient_id)
        request_form  = XRayRequestForm()
        return render(self.request, 'radiology/request_form.html', {
            'request_form': request_form,
            'patient_id': patient_id,
        })

    def post(self, *args, **kwargs):
        patient_id = kwargs['patient_id']
        patient = get_object_or_404(Patient, id=patient_id)
        request_form = XRayRequestForm(data=self.request.POST)
        if request_form.is_valid():
            with transaction.atomic():
                xray_request = request_form.save()
                order = Order(patient=patient, ordered_by=self.request.user)
                order.xray_request = xray_request
                order.save()
                messages.success(self.request, '')
                return redirect('radiology:order_list') # redirect_to via next
        else:
            messages.error(self.request, "Error while making orders")
            return render(self.request, 'radiology/request_form.html', {
                'request_form': request_form,
                'patient_id': patient_id,
            })


class ListImagingOrders(View):

    def get(self, *args, **kwargs):
        order_list = Order.objects.all()
        return render(self.request, 'radiology/order_list.html', {
            'order_list': order_list,
        })


class InsertFiles(View):

    def post(self, *args, **kwargs):
        order = get_object_or_404(Order, id=kwargs['order_id'])
        for f in self.request.FILES:
            ImageFile.objects.create(order=order, file=self.request.FILES[f])
        messages.success(self.request, "Image added successfully")
        return redirect('radiology:enter_result', order.id)


class EnterResult(View):

    def get(self, *args, **kwargs):
        order_id = kwargs['order_id']
        order = get_object_or_404(Order, id=order_id)
        images = ImageFile.objects.filter(order=order, deleted=False)
        report_form = ReportForm()
        try:
            if order.report:
                report_form = ReportForm(instance=order.report)
        except: pass
        return render(self.request, 'radiology/enter_result.html', {
            'report_form': report_form,
            'order': order,
            'images': images,
        })

    def post(self, *args, **kwargs):
        order_id = kwargs['order_id']
        order = get_object_or_404(Order, id=order_id)
        report_form = ReportForm(data=self.request.POST)
        if report_form.is_valid():
            report = report_form.save(commit=False)
            report.order = order
            report.reported_by = self.request.user

            rad_history = OutpatientRadiologyResult()
            patient = order.patient
            rad_history.patient = patient
            rad_history.visit = PatientVisit.objects.filter(patient = patient).exclude(visit_status='Ended').last()
            rad_history.result = report 
            #medication_history.doctor = 
            rad_history.registered_on = datetime.now()

            report.save()
            rad_history.save()
            order.complete = True
            order.save()
            messages.success(self.request, "Report saved.")
            notify(order.ordered_by, 'info', f'Order with id {order.id} complete')
            return redirect('radiology:order_list')


class TogglePayment(View):

    def get(self, *args, **kwargs):
        order_id = kwargs['order_id']
        order = get_object_or_404(Order, id=order_id)
        order.paid = not order.paid
        order.save()
        messages.success(self.request, "Payment updated")
        return redirect('radiology:order_list')


class RemoveReportImage(View):
    
    def get(self, *args, **kwargs):
        file_id = kwargs['file_id']
        image_file = get_object_or_404(ImageFile, id=file_id)
        image_file.deleted = True
        image_file.save()
        messages.success(self.request, "Message deleted successfully")
        return redirect('radiology:enter_result', image_file.order.id)


class ViewReport(View):

    def get(self, *args, **kwargs):
        order_id = kwargs['order_id']
        order = get_object_or_404(Order, id=order_id)
        images = ImageFile.objects.filter(order=order, deleted=False)
        report = ''
        try:
            report = ImagingReport.objects.get(order=order).report
        except: pass
        return render(self.request, 'radiology/view_report.html', {
            'report': report,
            'order': order,
            'images': images,
            'date': order.report.date,
            'reported_by': order.report.reported_by
        })