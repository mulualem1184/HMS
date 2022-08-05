from django.urls import path

from .views import (EnterResult, InsertFiles, ListImagingOrders,
                    RemoveReportImage, TogglePayment, ViewReport, XRayOrder)

app_name = 'radiology'

urlpatterns = [
    path('xray/<int:patient_id>', XRayOrder.as_view(), name='xray_order'),
    path('list-orders', ListImagingOrders.as_view(), name='order_list'),
    path('toggle-payment/<int:order_id>', TogglePayment.as_view(), name='toggle_payment'),
    path('report/<int:order_id>', EnterResult.as_view(), name='enter_result'),
    path('insert-report-image/<int:order_id>', InsertFiles.as_view(), name='insert_report_image'),
    path('remove-report-image/<int:file_id>', RemoveReportImage.as_view(), name='remove_report_image'),
    path('view-report/<int:order_id>', ViewReport.as_view(), name='view_report'),
]