import os

from django.core.files import File
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Specimen
from .utils import generate_barcode_image, generate_unique_int_id


@receiver(post_save, sender=Specimen)
def set_barcode(sender, **kwargs):
    instance:Specimen = kwargs.get('instance')
    if not instance.accession_number:
        acc_no = str(generate_unique_int_id())
        instance.accession_number = acc_no
        generate_barcode_image(acc_no)
        image_file = open(acc_no, 'rb')
        instance.barcode_image = File(image_file)
        instance.save()
        image_file.close()
        os.remove(image_file.name)


def update_status(sender, **kwargs):
    pass
