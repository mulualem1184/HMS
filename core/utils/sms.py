import requests
from ..models import TextMessage

class SMSAPI:

    def __init__(self, api_key) -> None:
        self.base_url = 'https://sms.hahucloud.com/api'
        self.key = api_key

    def send(self, phone, message):
        url = self.base_url + '/send'
        params = {
            'key': self.key,
            'phone': phone,
            'message': message,
        }
        try:
            r = requests.get(url=url, params=params)
            return 0
        except:
            return 1


sms_api = SMSAPI('61335e988e9135f0541f89b7c466609fcc247b58')

def send_text(phone, message):
    r = sms_api.send('+251'+phone, message)
    if not r:
        TextMessage.objects.create(to=phone, content=message, delivered=True)
    else:
        TextMessage.objects.create(to=phone, content=message, delivered=False)