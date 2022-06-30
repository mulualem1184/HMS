from django.apps import AppConfig


class PharmacyAppConfig(AppConfig):
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'pharmacy_app'

	def ready(self):
		from .signals import DrugSupplySignal
		from .tasks import low_stock_level_alert
		from template_tags.my_filters import times
#		from .autocomplete_light_registry import
		"""
#   	from .signals import DrugExpiredSignal
#   	from .tasks import RandomCreator

    	from .signals import DrugDispensedSignal

 		""" 	
 	