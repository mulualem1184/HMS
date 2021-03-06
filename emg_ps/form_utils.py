from django import forms
from django.forms.models import ModelFormOptions

_old_init = ModelFormOptions.__init__

def _new_init(self, options=None):
    _old_init(self, options)
    self.fieldsets = getattr(options, 'fieldsets', None)

ModelFormOptions.__init__ = _new_init


class Fieldset(object):

    def __init__(self, form, title, fields, classes):
        self.form = form
        self.title = title
        self.fields = fields
        self.classes = classes

    def __iter__(self):
        for field in self.fields:
            yield field

    def fieldsets(self):
        meta = getattr(self, '_meta', None)
        if not meta:
            meta = getattr(self, 'Meta', None)
        if not meta or not meta.fieldsets:
            return
        for name, data in meta.fieldsets:
            yield Fieldset(
                form=self,
                title=name,
                fields=(self[f] for f in data.get('fields',())),
                classes=data.get('classes', ''),
            )
    forms.BaseForm.fieldsets = fieldsets