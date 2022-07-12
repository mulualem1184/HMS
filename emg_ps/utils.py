from typing import Sequence

class Fieldset:
    def __init__(self, title:str, field_names:Sequence[str], form):
        self.title = title
        self.field_names:Sequence[str] = field_names
        self.form = form
        self.fields = []
        self.process_form()

    def process_form(self):
        for x in self.field_names:
            try:
                self.fields.append(self.form[x])
            except:pass

