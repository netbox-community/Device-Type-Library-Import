from collections import Counter
import pynetbox
import requests
# from pynetbox import RequestError as APIRequestError

class NetBox:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)
        
    def __init__(self, settings):
        self.counter = Counter(
            added=0,
            updated=0,
            manufacturer=0,
            module_added=0,
            module_port_added=0,
        )
        self.url = settings.NETBOX_URL
        self.token = settings.NETBOX_TOKEN
        self.handle = settings.handle
        self.netbox = None
        self.ignore_ssl = settings.IGNORE_SSL_ERRORS
        self.modules = False
        self.connect_api()
        self.verify_compatibility()
        self.existing_manufacturers = self.get_manufacturers()
        self.device_types = DeviceTypes(self.netbox, self.handle, self.counter)
        
    def connect_api(self):
        try:
            self.netbox = pynetbox.api(self.url, token=self.token)
            if self.ignore_ssl:
                self.handle.verbose_log("IGNORE_SSL_ERRORS is True, catching exception and disabling SSL verification.")
                requests.packages.urllib3.disable_warnings()
                self.netbox.http_session.verify = False
        except Exception as e:
            self.handle.exception("Exception", 'NetBox API Error', e)
            
    def get_api(self):
        return self.netbox
    
    def get_counter(self):
        return self.counter
    
    def verify_compatibility(self):
        # nb.version should be the version in the form '3.2'
        version_split = [int(x) for x in self.netbox.version.split('.')]

        # Later than 3.2
        # Might want to check for the module-types entry as well?
        if version_split[0] > 3 or (version_split[0] == 3 and version_split[1] >= 2):
            self.modules = True
            
    def get_manufacturers(self):
        return {str(item): item for item in self.netbox.dcim.manufacturers.all()}
            
    def create_manufacturers(self, vendors):
        to_create = []
        self.existing_manufacturers = self.get_manufacturers()
        for vendor in vendors:
            try:
                manGet = self.existing_manufacturers[vendor["name"]]
                self.handle.verbose_log(f'Manufacturer Exists: {manGet.name} - {manGet.id}')
            except KeyError:
                to_create.append(vendor)
                self.handle.verbose_log(f"Manufacturer queued for addition: {vendor['name']}")
        
        if to_create:
            try:
                created_manufacturers = self.netbox.dcim.manufacturers.create(to_create)
                for manufacturer in created_manufacturers:
                    self.handle.verbose_log(f'Manufacturer Created: {manufacturer.name} - '
                        + f'{manufacturer.id}')
                    self.counter.update({'manufacturer': 1})
            except pynetbox.RequestError as request_error:
                self.handle.log("Error creating manufacturers")
                self.handle.verbose_log(f"Error during manufacturer creation. - {request_error.error}")
                
class DeviceTypes:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)
        
    def __init__(self, netbox, handle, counter):
        self.netbox = netbox
        self.handle = handle
        self.counter = counter
        self.existing_device_types = self.get_device_types()
        
    def get_device_types(self):
        return {str(item): item for item in self.netbox.dcim.device_types.all()}

    def get_power_ports(self, device_type):
        return {str(item): item for item in self.netbox.dcim.power_port_templates.filter(devicetype_id=device_type)}
    
    def get_rear_ports(self, device_type):
        return {str(item): item for item in self.netbox.dcim.rear_port_templates.filter(devicetype_id=device_type)}
    
    def get_ports_to_create(self, dcim_ports, device_type, existing_ports):
        to_create = [port for port in dcim_ports if port['name'] not in existing_ports]
        for port in to_create:
            port['device_type'] = device_type
            
        return to_create
    
    def create_interfaces(self, interfaces, device_type):
        existing_interfaces = {str(item): item for item in self.netbox.dcim.interface_templates.filter(
            devicetype_id=device_type)}
        to_create = self.get_ports_to_create(
            interfaces, device_type, existing_interfaces)

        if to_create:
            try:
                self.counter.update({'updated':
                                     self.handle.log_ports_created(
                                         self.netbox.dcim.interface_templates.create(to_create), "Interface")
                                     })
            except pynetbox.RequestError as excep:
                self.handle.log(f"Error '{excep.error}' creating Interface")
                
    def create_power_ports(self, power_ports, device_type):
        existing_power_ports = self.get_power_ports(device_type)
        to_create = self.get_ports_to_create(power_ports, device_type, existing_power_ports)
        
        if to_create:
            try:
                self.counter.update({'updated':
                                     self.handle.log_ports_created(
                                         self.netbox.dcim.power_port_templates.create(to_create), "Power Port")
                                     })
            except pynetbox.RequestError as excep:
                self.handle.log(f"Error '{excep.error}' creating Power Port")
                
    def create_console_ports(self, console_ports, device_type):
        existing_console_ports = {str(item): item for item in self.netbox.dcim.console_port_templates.filter(devicetype_id=device_type)}
        to_create = self.get_ports_to_create(console_ports, device_type, existing_console_ports)
        
        if to_create:
            try:
                self.counter.update({'updated':
                                     self.handle.log_ports_created(
                                         self.netbox.dcim.console_port_templates.create(to_create), "Console Port")
                                     })
            except pynetbox.RequestError as excep:
                self.handle.log(f"Error '{excep.error}' creating Console Port")

    def create_power_outlets(self, power_outlets, device_type):
        existing_power_outlets = {str(item): item for item in self.netbox.dcim.power_outlet_templates.filter(devicetype_id=device_type)}
        to_create = self.get_ports_to_create(power_outlets, device_type, existing_power_outlets)

        if to_create:
            existing_power_ports = self.get_power_ports(device_type)
            for outlet in to_create:
                try:
                    power_port = existing_power_ports[outlet["power_port"]]
                    outlet['power_port'] = power_port.id
                except KeyError:
                    pass
                
            try:
                self.counter.update({'updated':
                                     self.handle.log_ports_created(
                                         self.netbox.dcim.power_outlet_templates.create(to_create), "Power Outlet")
                                     })
            except pynetbox.RequestError as excep:
                self.handle.log(f"Error '{excep.error}' creating Power Outlet")

    def create_console_server_ports(self, console_server_ports, device_type):
        existing_console_server_ports = {str(item): item for item in self.netbox.dcim.console_server_port_templates.filter(devicetype_id=device_type)}
        to_create = self.get_ports_to_create(console_server_ports, device_type, existing_console_server_ports)

        if to_create:
            try:
                self.counter.update({'updated':
                                     self.handle.log_ports_created(
                                         self.netbox.dcim.console_server_port_templates.create(to_create), "Console Server Port")
                                     })
            except pynetbox.RequestError as excep:
                self.handle.log(f"Error '{excep.error}' creating Console Server Port")

    def create_rear_ports(self, rear_ports, device_type):
        existing_rear_ports = self.get_rear_ports(device_type)
        to_create = self.get_ports_to_create(rear_ports, device_type, existing_rear_ports)

        if to_create:
            try:
                self.counter.update({'updated':
                                     self.handle.log_ports_created(
                                         self.netbox.dcim.rear_port_templates.create(to_create), "Rear Port")
                                     })
            except pynetbox.RequestError as excep:
                self.handle.log(f"Error '{excep.error}' creating Rear Port")

    def create_front_ports(self, front_ports, device_type):
        existing_front_ports = {str(item): item for item in self.netbox.dcim.front_port_templates.filter(devicetype_id=device_type)}
        to_create = self.get_ports_to_create(front_ports, device_type, existing_front_ports)
        
        if to_create:
            all_rearports = self.get_rear_ports(device_type)
            for port in to_create:
                try:
                    rear_port = all_rearports[port["rear_port"]]
                    port['rear_port'] = rear_port.id
                except KeyError:
                    print(f'Could not find Rear Port for Front Port: {port["name"]} - '
                        + f'{port["type"]} - {device_type}')
            
            try:
                self.counter.update({'updated':
                                     self.handle.log_ports_created(
                                         self.netbox.dcim.front_port_templates.create(to_create), "Front Port")
                                     })
            except pynetbox.RequestError as excep:
                self.handle.log(f"Error '{excep.error}' creating Front Port")

    def create_device_bays(self, device_bays, device_type):
        existing_device_bays = {str(item): item for item in self.netbox.dcim.device_bay_templates.filter(devicetype_id=device_type)}
        to_create = self.get_ports_to_create(device_bays, device_type, existing_device_bays)
        
        if to_create:
            try:
                self.counter.update({'updated':
                                     self.handle.log_ports_created(
                                         self.netbox.dcim.device_bay_templates.create(to_create), "Device Bay")
                                     })
            except pynetbox.RequestError as excep:
                self.handle.log(f"Error '{excep.error}' creating Device Bay")
                
    def create_module_bays(self, module_bays, device_type):
        existing_module_bays = {str(item): item for item in self.netbox.dcim.module_bay_templates.filter(devicetype_id=device_type)}
        to_create = self.get_ports_to_create(module_bays, device_type, existing_module_bays)
        
        if to_create:
            try:
                self.counter.update({'updated':
                                     self.handle.log_ports_created(
                                         self.netbox.dcim.module_bay_templates.create(to_create), "Module Bay")
                                     })
            except pynetbox.RequestError as excep:
                self.handle.log(f"Error '{excep.error}' creating Module Bay")

    