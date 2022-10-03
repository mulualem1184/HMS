from typing import Sequence
from outpatient_app.models import OutpatientChiefComplaint, VisitQueue, ServiceRoom
from barcode import EAN13
from barcode.writer import ImageWriter
import uuid
import time

def return_triaged_patient():
	allocated_patient_array = []
	patient_compliant = OutpatientChiefComplaint.objects.filter(active=True)
	for patient in patient_compliant:
		allocated_patient_array.append(patient.patient.id)
		print('\n', patient.patient,'\n')
	return allocated_patient_array

def return_room_queue():
	room_array = []
	queue_amount_array = []
	rooms = ServiceRoom.objects.all()
	for room in rooms:
		queue = VisitQueue.objects.filter(visit__service_room=room, visit__visit_status='Pending')
		queue_amount = queue.count()
		queue_amount_array.append(queue_amount)
		#temp_quantity = room['service_room']
		room_array.append(room)

	room_zip = zip(room_array,queue_amount_array)
	return (room_zip)