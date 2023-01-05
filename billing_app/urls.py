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

	path('invoices/', Invoices.as_view(), name="invoices"),
	path('add_invoice/', AddInvoice.as_view(), name="add_invoice"),
	path('edit_invoice/<int:patient_id>', EditInvoice.as_view(), name="edit_invoice"),
	path('edit_invoice2/<int:invoice_id>', EditInvoice2.as_view(), name="edit_invoice2"),

	path('edit_receipt/<int:patient_id>', EditReceipt.as_view(), name="edit_receipt"),

	path('save_invoice/<int:patient_id>', SaveInvoice.as_view(), name="save_invoice"),
	path('recieve_payment/<int:invoice_id>', RecievePayment.as_view(), name="recieve_payment"),

	path('payments/', Payments.as_view(), name="payments"),
	path('receive_prepayment/', ReceivePrePayment.as_view(), name="receive_prepayment"),
	path('reconcile_invoices/', ReconcileInvoices.as_view(), name="reconcile_invoices"),

	path('receipts/', Receipts.as_view(), name="receipts"),
	path('add_receipt/', AddReceipt.as_view(), name="add_receipt"),
	path('save_receipt/<int:patient_id>', SaveReceipt.as_view(), name="save_receipt"),

	path('estimates/', Estimates.as_view(), name="estimates"),
	path('add_estimate/', AddEstimate.as_view(), name="add_estimate"),
	path('edit_estimate/<int:patient_id>', EditEstimate.as_view(), name="edit_estimate"),
	path('save_estimate/<int:patient_id>', SaveEstimate.as_view(), name="save_estimate"),
	path('convert_estimate_to_invoice/<int:invoice_id>', ConvertEstimateToInvoice.as_view(), name="convert_estimate_to_invoice"),

	path('items/', Items.as_view(), name="items"),
	path('create_item/', CreateItem.as_view(), name="create_item"),
	path('create_drug/<int:item_id>', CreateDrug.as_view(), name="create_drug"),
	path('associate_drug_item/<int:item_id>', AssociateDrugItem.as_view(), name="associate_drug_item"),

	path('billing_dashboard/', BillingDashboard.as_view(), name="billing_dashboard"),
	path('patient_billing/<int:patient_id>', PatientBilling.as_view(), name="patient_billing"),
	path('prepare_billable_item/<int:patient_id>', PrepareBillableItem.as_view(), name="prepare_billable_item"),

	path('add_item_sale_info/<str:url_arg>', AddItemSaleInfo.as_view(), name="add_item_sale_info"),
	path('delete_item_sale_info/<int:item_info_id>/<int:patient_id>', DeleteItemSaleInfo.as_view(), name="delete_item_sale_info"),

]