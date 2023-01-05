from django.urls.conf import path

from .views import (AddNormalRange, AddSampleType, AddSpecimen, CancelOrder,
                    CreateLabTestType, CreateOrder, EditLabTestResultType,
                    EditLabTestType, EditTestResult, EnterTestResult,
                    MarkMultipleOrdersAsPaid, MarkOrderAsPaid, MyOrders,
                    OrderForPatient, RemoveLabTestType, RemoveResultType,
                    ReportPage, SetSpecimenForTest, ToggleTestPaidStatus,
                    UpdateTestStatus, ViewOrder, ViewOrderList,
                    ViewSpecimenImage, ViewTest, ViewTestList, ViewTestResult, LaboratoryList,
                    AssignLabEmployee,Specimens,AddSpecimenToTest,EditSpecimen,
                    DeleteSpecimen, LabDashboard,EditSpecimen2,LabResultRanges,
                    LabResults,CreateLabTestItem
                    )

urlpatterns = [
    path('order', CreateOrder.as_view(), name='create-order'),
    path('order-for-patient/<int:patient_id>', OrderForPatient.as_view(), name='order-for-patient'),
    path('view-orders', ViewOrderList.as_view() ,name='view-orders'),
    path('my-orders', MyOrders.as_view(), name='my-orders'),
    path('enter-test-result/<int:test_id>', EnterTestResult.as_view(),name='enter-test-result'),
    path('view-test-result/<int:test_id>', ViewTestResult.as_view(), name='view-test-result'),
    path('edit-test-result/<int:test_id>', EditTestResult.as_view(), name='edit-test-result'),
    path('add-specimen/<int:test_id>', AddSpecimen.as_view(), name='add-specimen'),
    path('set-specimen/<int:test_id>', SetSpecimenForTest.as_view(), name='set-accession-number'),
    path('mark-order-as-paid/<int:order_id>', MarkOrderAsPaid.as_view(), name='mark-order-as-paid' ),
    path('mark-multiple-orders-as-paid', MarkMultipleOrdersAsPaid.as_view(), name='mark-multiple-orders-as-paid'),
    path('cancel-order', CancelOrder.as_view(), name='cancel-order'),
    path('toggle-paid/<int:test_id>', ToggleTestPaidStatus.as_view(), name='toggle-test-paid-status'),
    path('view-order/<int:order_id>', ViewOrder.as_view(), name='view-order'),
    path('view-test/<int:test_id>', ViewTest.as_view(), name='view-test'),
    path('update-test-status/<int:test_id>', UpdateTestStatus.as_view(), name='update-test-status'),
    path('tests', ViewTestList.as_view(), name='view-tests'),
    path('specimen-image/<int:specimen_id>', ViewSpecimenImage.as_view(), name='view-specimen-image'),
    path('create-test-type', CreateLabTestType.as_view(), name='create_lab_test_type'),
    path('edit-test-type/<int:id>', EditLabTestType.as_view(), name='edit_lab_test_type'),
    path('remove-test-type/<int:id>', RemoveLabTestType.as_view(), name='remove_lab_test_type'),
    path('edit-result-type/<int:id>', EditLabTestResultType.as_view(), name='edit_lab_test_result_type'),
    path('remove-result-type/<int:id>', RemoveResultType.as_view(), name='remove_lab_test_result_type'),
    path('add-sample-type', AddSampleType.as_view(), name='add_sample_type'),
    path('add-normal-range/<int:id>', AddNormalRange.as_view(), name='add_normal_range'),
    path('report', ReportPage.as_view(), name='lis_report'),

    path('lab_result_ranges/<int:result_type_id>', LabResultRanges.as_view(), name='lab_result_ranges'),
    path('lab_results/<int:patient_id>', LabResults.as_view(), name='lab_results'),

    path('laboratory_list', LaboratoryList, name='laboratory_list'),
    path('assign_lab_employee', AssignLabEmployee, name='assign_lab_employee'),

    path('add_specimen_to_test/<int:patient_id>', AddSpecimenToTest.as_view(), name='add_specimen_to_test'),
    path('edit_specimen/<int:order_id>/<int:specimen_id>', EditSpecimen.as_view(), name='edit_specimen'),
    path('edit_specimen2/<int:patient_id>/<int:specimen_id>', EditSpecimen2.as_view(), name='edit_specimen2'),
    
    path('delete_specimen/<int:order_id>/<int:specimen_id>', DeleteSpecimen.as_view(), name='delete_specimen'),

    path('specimens/<int:patient_id>', Specimens.as_view(), name='specimens'),

    path('lab_dashboard/<int:patient_id>', LabDashboard.as_view(), name='lab_dashboard'),
    path('create_lab_test_item/<int:item_id>', CreateLabTestItem.as_view(), name='create_lab_test_item'),

]
