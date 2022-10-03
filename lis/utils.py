from typing import Sequence
from lis.models import LaboratoryTest, LaboratoryTestType, Order
from barcode import EAN13
from barcode.writer import ImageWriter
import uuid
import time


def generate_barcode_image(hash_id:str, file_name:str=''):
    file_name = hash_id if not file_name else file_name
    with open(file_name, 'wb') as f:
        EAN13(hash_id, writer=ImageWriter()).write(f)
    return hash_id

def generate_unique_int_id() -> int:
    uid:int = int(time.time()) + uuid.uuid4().int & (1<<64)-1
    return uid


class GeneralReport:

    def __init__(self, test_type:LaboratoryTestType, start_date=None, end_date=None):
        self.test_type = test_type
        order_list:Sequence[Order] = Order.objects.all()
        test_list = LaboratoryTest.objects.filter(test_type=self.test_type, status='COMPLETED')
        order_list = [Order.objects.get(id=elt['order']) for elt in test_list.values('order').distinct()]
        time_frame = len(order_list) or 1
        try:
            time_frame = (order_list[-1].ordered_at - order_list[0].ordered_at).days
        except:pass
        test_list = test_list.filter(order__ordered_at__gte=start_date) 
        test_list = test_list.filter(order__ordered_at__lte=end_date)
        self.no_patient = test_list.values('order__patient').distinct().count()
        self.test_list = test_list
        self.time_frame = time_frame
        self.total_no_tests = len(test_list)
        self.avg_per_day = self.total_no_tests/self.time_frame
        self.total_price = self.test_type.price * self.total_no_tests