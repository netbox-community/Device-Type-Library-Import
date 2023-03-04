import pynetbox
import requests
# from pynetbox import RequestError as APIRequestError

class NetBox:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)
        
    def __init__(self, settings):
        self.url = settings.NETBOX_URL
        self.token = settings.NETBOX_TOKEN
        self.handle = settings.handle
        self.connection = None
        self.ignore_ssl = settings.IGNORE_SSL_ERRORS
        self.modules = False
        self.connect_api()
        self.verify_compatibility()
        
    def connect_api(self):
        try:
            self.connection = pynetbox.api(self.url, token=self.token)
            if self.ignore_ssl:
                print("IGNORE_SSL_ERRORS is True, catching exception and disabling SSL verification.")
                requests.packages.urllib3.disable_warnings()
                self.connection.http_session.verify = False
        except Exception as e:
            self.handle.exception("Exception", 'NetBox API Error', e)
            
    def get_api(self):
        return self.connection
    
    def verify_compatibility(self):
        # nb.version should be the version in the form '3.2'
        version_split = [int(x) for x in self.connection.version.split('.')]

        # Later than 3.2
        # Might want to check for the module-types entry as well?
        if version_split[0] > 3 or (version_split[0] == 3 and version_split[1] >= 2):
            self.modules = True
