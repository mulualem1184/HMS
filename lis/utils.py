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