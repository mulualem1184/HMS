from django.urls import path
#from django.conf.urls import url
from django.conf.urls import *
from . import views
from .views import *

urlpatterns = [

 	path('drug_supply_report/', views.SupplyReportPage, name="drug_supply_report"),
 	path('drug_profile_form_page/', views.DrugProfileFormPage, name="drug_profile_form_page"),
  path('disease_drug_form/', views.DiseaseDrugFormPage, name="disease_drug_form"),
  path('contraindication_drug_form/', views.ContraIndicationDrugFormPage, name="contraindication_drug_form"),
  path('side_effect_drug_form/', views.SideEffectDrugFormPage, name="side_effect_drug_form"),

 	path('drug_inventory/', views.DrugInventory, name="drug_inventory"),
	path('drug_report/', views.DrugReport, name="drug_report"),
	path('supply_form/', views.SupplyFormPage, name="supply_form"),
  path('stock_supply_form/<int:procurement_pk>', views.StockSupplyFormPage, name="stock_supply_form"),	
  path('drug_related_info/', views.DrugRelatedInfo, name = 'drug_related_info'),
	path('pathological_finding/', views.Disease, name = 'pathological_finding'),
 	path('drug_interaction/', views.DrugInteractionPage, name = 'drug_interaction'),
 	path('alcohol_interaction/', views.AlcoholInteraction, name = 'alcohol_interaction'),
 	path('food_interaction/', views.FoodInteraction, name = 'food_interaction'),
 	path('disease_interaction/', views.DiseaseInteraction, name = 'disease_interaction'),
	path('side_effect/', views.SideEffectPage, name = 'side_effect'),
	path('age_range/', views.AgeRangePage, name = 'age_range'),
	path('weight_range/', views.WeightRangePage, name = 'weight_range'),
	path('intake_mode/', views.IntakeModePage, name = 'intake_mode'),
  path('prescription_form/<int:patient_id>', views.PrescriptionFormPage, name = 'prescription_form'),
#  path('procurement_form', views.ProcurementFormPage, name = 'procurement_form'),
  path('prescription_list', PrescriptionList, name = 'prescription_list'),
  path('inventory_structure', InventoryStructure, name = 'inventory_structure'),
  
  path('dispensary_structure', DispensaryStructure, name = 'dispensary_structure'),

  path('stock_list', StockList, name = 'stock_list'),
  path('stock_shelf_list/<str:pk>/', StockShelfList, name = 'stock_shelf_list'),
  path('stock_slot_list/<str:pk>/', StockSlotList, name = 'stock_slot_list'),
  path('stock_drug_list/<str:pk>/', StockDrugList, name = 'stock_drug_list'),
  path('drug_location/<str:pk>', DrugLocation, name = 'drug_location'),
  path('drug_location_stock_shelf/<str:pk>/<str:pk2>', DrugLocationStockShelf, name = 'drug_location_stock_shelf'),
  path('drug_location_stock_slot/<str:pk>/<str:pk2>', DrugLocationStockSlot, name = 'drug_location_stock_slot'),

  path('procurement', ProcurementPage, name = 'procurement'),
  path('save_procurement_detail/<int:procurement_id>/', SaveProcurementDetail, name = 'save_procurement_detail'),

  path('cancel_procurement/<int:procurement_pk>', CancelProcurement, name = 'cancel_procurement'),
  
  path('procurement_detail/<str:pk>', ProcurementDetailPage, name = 'procurement_detail'),
  path('procurement_batch/<int:procurement_pk>/<int:batch_no>', ProcurementBatch, name = 'procurement_batch'),

  path('bill_form/<str:pk>/<int:pk2>', BillFormPage, name = 'bill_form'),
  path('non_prescription_bill_form/', NonPrescriptionBillForm, name = 'non_prescription_bill_form'),


  path('drug_price_form', DrugPriceFormPage, name = 'drug_price_form'),
  path('dosage_form', DosageFormPage, name = 'dosage_form'),
  path('threshold', ThresholdFormPage, name = 'threshold'),
  path('low_stock_drugs', LowStockDrugs, name = 'low_stock_drugs'),
  path('drug_profile/<str:pk>', DrugProfilePage, name = 'drug_profile'),
  path('drug_image_form/<str:pk>', DrugImageFormPage, name = 'drug_image_form'),
  path('bill_detail/<str:pk>', BillPage, name = 'bill_detail'),

  path('drug_chart/', DrugChart, name = 'drug_chart'),
  path('printed_invoice/<str:pk>', PrintedInvoice, name = 'printed_invoice'),

  path('new_bill_form/<str:pk>/<int:pk2>', NewBillForm, name = 'new_bill_form'),
  
  path('api/data', get_data, name = 'api-data'),
  path('api/chart/data', ChartData.as_view()),
  
  path('chart/', chart, name = 'chart'),
  path('shelf_chart/', ShelfChart, name = 'shelf_chart'),

#  path('api/shelf_chart/data', ShelfChartData.as_view()),
  path('get_board', ShelfChartData.as_view()),
 

  path('drug_sale_chart/', DrugSaleReport, name = 'drug_sale_chart'),
  path('api/drug_sale_chart/data', DrugSaleData.as_view()),
  path('drug_sale_detail/<int:month_no>', DrugSaleDetail, name = 'drug_sale_detail'),
 

  path('monthly_sale_chart/', MonthlySaleReport, name = 'monthly_sale_chart'), 
  path('api/monthly_sale_chart/data', MonthlySaleData.as_view()),

  path('daily_sale_chart/', DailySaleReport, name = 'daily_sale_chart'),   
  path('api/daily_sale_chart/data', DailySaleData.as_view()),

  path('trial', DrugProfileFormPage, name = 'trial'),

  path('dispensary_list', DispensaryList, name = 'dispensary_list'),
  path('chart_trial', ChartTrial, name = 'chart_trial'),

  path('dispensary_shelf_list/<str:pk>', DispensaryShelfList, name = 'dispensary_shelf_list'),

  path('edit_dispensary_shelf/<str:pk>/<str:dispensary_pk>', EditDispensaryShelf, name = 'edit_dispensary_shelf'),
  path('edit_stock_shelf/<str:pk>/<str:stock_pk>', EditStockShelf, name = 'edit_stock_shelf'),
  path('drug_relocation_from_stock', DrugRelocationFromStock, name = 'drug_relocation_from_stock'),
  path('drug_allocation_to_dispensary', DrugAllocationToDispensary, name = 'drug_allocation_to_dispensary'),


]
