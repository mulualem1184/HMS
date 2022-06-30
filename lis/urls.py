from django.urls.conf import path

from .views import (AddSpecimen, CancelOrder, CreateOrder, EditTestResult, EnterTestResult, MarkMultipleOrdersAsPaid, MarkOrderAsPaid, MyOrders,
                    OrderForPatient, SetSpecimenForTest, ToggleTestPaidStatus, UpdateTestStatus, ViewOrder,
                    ViewOrderList, ViewSpecimenImage, ViewTest, ViewTestList, ViewTestResult)

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
]
