import pynetbox
# from pynetbox import RequestError as APIRequestError

class NetBox:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)
        
    def __init__(self, settings):
        self.url = settings.NETBOX_URL
        self.token = settings.NETBOX_TOKEN
        self.handle = settings.handle
        self.connection = self.connect_api()
        
    def connect_api(self):
        try:
            return pynetbox.api(self.url, token=self.token)
        except Exception as e:
            self.handle.exception("Exception", 'NetBox API Error', e)
            
    def get_api(self):
        return self.connection