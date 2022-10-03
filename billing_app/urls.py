from django.urls import path
#from django.conf.urls import url
from django.conf.urls import *
from . import views
from .views import *

urlpatterns = [

 	path('visiting_card_price/', views.VisitingCardPriceFormPage, name="visiting_card_price"),
 	path('create_visiting_card/', views.CreateVisitingCard, name="create_visiting_card"),
	
 	path('service_form/', views.ServiceFormPage, name="service_form"),
 	path('assign_visiting_card_form/', views.AssignVisitingCardFormPage, name="assign_visiting_card_form"),
	path('visiting_card_list/', views.VisitingCardList, name="visiting_card_list"),
	path('generate_visit_bill/<int:bill_id>', views.GenerateVisitBill, name="generate_visit_bill"),

	path('lab_order_list/', views.LabOrderList, name="lab_order_list"),
	path('view_lab_order_detail/<int:order_id>', views.ViewLabOrderDetail, name="view_lab_order_detail"),
	path('mark_lab_test_as_paid/<int:test_id>', views.MarkLabTestAsPaid, name="mark_lab_test_as_paid"),

	path('visit_bill_detail/<int:bill_id>', views.VisitBillDetailPage, name="visit_bill_detail"),
	path('patient_insurance_form/<int:patient_id>', views.PatientInsuranceFormPage, name="patient_insurance_form"),
	path('give_service/<int:patient_id>', views.GiveService, name="give_service"),
	path('service_bill_list/', views.ServiceBillList, name="service_bill_list"),
	path('generate_service_bill/<int:bill_id>', views.GenerateServiceBill, name="generate_service_bill"),

	path('cashier_list/', views.CashierList, name="cashier_list"),
	path('cashier_debt_list/<int:cashier_id>', views.CashierDebtList, name="cashier_debt_list"),
	path('reconcile_full_debt/<int:debt_id>', views.ReconcileFullDebt, name="reconcile_full_debt"),
	path('partial_reconcilation/<int:debt_id>', views.PartialReconcilation, name="partial_reconcilation"),

]