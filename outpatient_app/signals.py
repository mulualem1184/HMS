from django.db.models.signals import * 
from .models import *
from django.dispatch import receiver
from datetime import datetime
#from datetime import timezone
from django.utils import timezone
from .forms import *
from django.db.models import Sum





@receiver(post_delete, sender=VisitQueue)
def QueueSignal(sender, **kwargs):
	instance : VisitQueue = kwargs.get('instance')
	queues = VisitQueue.objects.all()
	for queue in queues:
		queue.queue_number = queue.queue_number - 1
		print('\n',queue.queue_number,'\n')
		queue.save()
