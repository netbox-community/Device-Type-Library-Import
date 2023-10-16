from collections import Counter
import pynetbox
import requests
import os
import glob
# from pynetbox import RequestError as APIRequestError

class NetBox:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, settings):
        self.counter = Counter(
            added=0,
            updated=0,
            manufacturer=0,
            device_role=0,
            module_added=0,
            module_port_added=0,
            images=0,
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
        self.device_types = DeviceTypes(self.netbox, self.handle, self.counter, self.ignore_ssl)

    def connect_api(self):
        try:
            self.netbox = pynetbox.api(self.url, token=self.token)
            if self.ignore_ssl:
                self.handle.verbose_log("IGNORE_SSL_ERRORS is True, catching exception and disabling SSL verification.")
                #requests.packages.urllib3.disable_warnings()
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

    def get_device_roles(self):
        return {str(item): item for item in self.netbox.dcim.device_roles.all()}

    def create_device_roles(self, roles):
        to_create = []
        self.existing_device_roles = self.get_device_roles()
        for role in roles:
            try:
                rolGet = self.existing_device_roles[role["name"]]
                self.handle.verbose_log(f'Device Roles Exists: {rolGet.name} - {rolGet.id}')
            except KeyError:
                to_create.append(role)
                self.handle.verbose_log(f"Device Role queued for addition: {role['name']}")

        if to_create:
            try:
                created_device_roles = self.netbox.dcim.device_roles.create(to_create)
                for role in created_device_roles:
                    self.handle.verbose_log(f'Device Role Created: {role.name} - '
                        + f'{role.id}')
                    self.counter.update({'device_role': 1})
            except pynetbox.RequestError as request_error:
                self.handle.log("Error creating device role")
                self.handle.verbose_log(f"Error during device role creation. - {request_error.error}")

    def create_device_types(self, device_types_to_add):
        for device_type in device_types_to_add:

            # Remove file base path
            src_file = device_type["src"]
            del device_type["src"]

            # Pre-process front/rear_image flag, remove it if present
            saved_images = {}
            image_base = os.path.dirname(src_file).replace("device-types","elevation-images")
            for i in ["front_image","rear_image"]:
                if i in device_type:
                    if device_type[i]:
                        image_glob = f"{image_base}/{device_type['slug']}.{i.split('_')[0]}.*"
                        images = glob.glob(image_glob, recursive=False)
                        if images:
                          saved_images[i] = images[0]
                        else:
                          self.handle.log(f"Error locating image file using '{image_glob}'")
                    del device_type[i]

            try:
                dt = self.device_types.existing_device_types[device_type["model"]]
                self.handle.verbose_log(f'Device Type Exists: {dt.manufacturer.name} - '
                    + f'{dt.model} - {dt.id}')
            except KeyError:
                try:
                    dt = self.netbox.dcim.device_types.create(device_type)
                    self.counter.update({'added': 1})
                    self.handle.verbose_log(f'Device Type Created: {dt.manufacturer.name} - '
                        + f'{dt.model} - {dt.id}')
                except pynetbox.RequestError as e:
                    self.handle.log(f'Error {e.error} creating device type:'
                                    f' {device_type["manufacturer"]["name"]} {device_type["model"]}')
                    continue

            if "interfaces" in device_type:
                self.device_types.create_interfaces(device_type["interfaces"], dt.id)
            if "power-ports" in device_type:
                self.device_types.create_power_ports(device_type["power-ports"], dt.id)
            if "power-port" in device_type:
                self.device_types.create_power_ports(device_type["power-port"], dt.id)
            if "console-ports" in device_type:
                self.device_types.create_console_ports(device_type["console-ports"], dt.id)
            if "power-outlets" in device_type:
                self.device_types.create_power_outlets(device_type["power-outlets"], dt.id)
            if "console-server-ports" in device_type:
                self.device_types.create_console_server_ports(device_type["console-server-ports"], dt.id)
            if "rear-ports" in device_type:
                self.device_types.create_rear_ports(device_type["rear-ports"], dt.id)
            if "front-ports" in device_type:
                self.device_types.create_front_ports(device_type["front-ports"], dt.id)
            if "device-bays" in device_type:
                self.device_types.create_device_bays(device_type["device-bays"], dt.id)
            if self.modules and 'module-bays' in device_type:
                self.device_types.create_module_bays(device_type['module-bays'], dt.id)

            # Finally, update images if any
            if saved_images:
                self.device_types.upload_images(self.url, self.token, saved_images, dt.id)

    def create_module_types(self, module_types):
        all_module_types = {}
        for curr_nb_mt in self.netbox.dcim.module_types.all():
            if curr_nb_mt.manufacturer.slug not in all_module_types:
                all_module_types[curr_nb_mt.manufacturer.slug] = {}

            all_module_types[curr_nb_mt.manufacturer.slug][curr_nb_mt.model] = curr_nb_mt


        for curr_mt in module_types:
            try:
                module_type_res = all_module_types[curr_mt['manufacturer']['slug']][curr_mt["model"]]
                self.handle.verbose_log(f'Module Type Exists: {module_type_res.manufacturer.name} - '
                    + f'{module_type_res.model} - {module_type_res.id}')
            except KeyError:
                try:
                    module_type_res = self.netbox.dcim.module_types.create(curr_mt)
                    self.counter.update({'module_added': 1})
                    self.handle.verbose_log(f'Module Type Created: {module_type_res.manufacturer.name} - '
                        + f'{module_type_res.model} - {module_type_res.id}')
                except pynetbox.RequestError as exce:
                    self.handle.log(f"Error '{exce.error}' creating module type: " +
                        f"{curr_mt}")

            if "interfaces" in curr_mt:
                self.device_types.create_module_interfaces(curr_mt["interfaces"], module_type_res.id)
            if "power-ports" in curr_mt:
                self.device_types.create_module_power_ports(curr_mt["power-ports"], module_type_res.id)
            if "console-ports" in curr_mt:
                self.device_types.create_module_console_ports(curr_mt["console-ports"], module_type_res.id)
            if "power-outlets" in curr_mt:
                self.device_types.create_module_power_outlets(curr_mt["power-outlets"], module_type_res.id)
            if "console-server-ports" in curr_mt:
                self.device_types.create_module_console_server_ports(curr_mt["console-server-ports"], module_type_res.id)
            if "rear-ports" in curr_mt:
                self.device_types.create_module_rear_ports(curr_mt["rear-ports"], module_type_res.id)
            if "front-ports" in curr_mt:
                self.device_types.create_module_front_ports(curr_mt["front-ports"], module_type_res.id)

class DeviceTypes:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, netbox, handle, counter, ignore_ssl):
        self.netbox = netbox
        self.handle = handle
        self.counter = counter
        self.existing_device_types = self.get_device_types()
        self.ignore_ssl = ignore_ssl

    def get_device_types(self):
        return {str(item): item for item in self.netbox.dcim.device_types.all()}

    def get_power_ports(self, device_type):
        return {str(item): item for item in self.netbox.dcim.power_port_templates.filter(devicetype_id=device_type)}

    def get_rear_ports(self, device_type):
        return {str(item): item for item in self.netbox.dcim.rear_port_templates.filter(devicetype_id=device_type)}

    def get_module_power_ports(self, module_type):
        return {str(item): item for item in self.netbox.dcim.power_port_templates.filter(moduletype_id=module_type)}

    def get_module_rear_ports(self, module_type):
        return {str(item): item for item in self.netbox.dcim.rear_port_templates.filter(moduletype_id=module_type)}

    def get_device_type_ports_to_create(self, dcim_ports, device_type, existing_ports):
        to_create = [port for port in dcim_ports if port['name'] not in existing_ports]
        for port in to_create:
            port['device_type'] = device_type

        return to_create

    def get_module_type_ports_to_create(self, module_ports, module_type, existing_ports):
        to_create = [port for port in module_ports if port['name'] not in existing_ports]
        for port in to_create:
            port['module_type'] = module_type

        return to_create

    def create_interfaces(self, interfaces, device_type):
        existing_interfaces = {str(item): item for item in self.netbox.dcim.interface_templates.filter(
            devicetype_id=device_type)}
        to_create = self.get_device_type_ports_to_create(
            interfaces, device_type, existing_interfaces)

        if to_create:
            try:
                self.counter.update({'updated':
                                     self.handle.log_device_ports_created(
                                         self.netbox.dcim.interface_templates.create(to_create), "Interface")
                                     })
            except pynetbox.RequestError as excep:
                self.handle.log(f"Error '{excep.error}' creating Interface")

    def create_power_ports(self, power_ports, device_type):
        existing_power_ports = self.get_power_ports(device_type)
        to_create = self.get_device_type_ports_to_create(power_ports, device_type, existing_power_ports)

        if to_create:
            try:
                self.counter.update({'updated':
                                     self.handle.log_device_ports_created(
                                         self.netbox.dcim.power_port_templates.create(to_create), "Power Port")
                                     })
            except pynetbox.RequestError as excep:
                self.handle.log(f"Error '{excep.error}' creating Power Port")

    def create_console_ports(self, console_ports, device_type):
        existing_console_ports = {str(item): item for item in self.netbox.dcim.console_port_templates.filter(devicetype_id=device_type)}
        to_create = self.get_device_type_ports_to_create(console_ports, device_type, existing_console_ports)

        if to_create:
            try:
                self.counter.update({'updated':
                                     self.handle.log_device_ports_created(
                                         self.netbox.dcim.console_port_templates.create(to_create), "Console Port")
                                     })
            except pynetbox.RequestError as excep:
                self.handle.log(f"Error '{excep.error}' creating Console Port")

    def create_power_outlets(self, power_outlets, device_type):
        existing_power_outlets = {str(item): item for item in self.netbox.dcim.power_outlet_templates.filter(devicetype_id=device_type)}
        to_create = self.get_device_type_ports_to_create(power_outlets, device_type, existing_power_outlets)

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
                                     self.handle.log_device_ports_created(
                                         self.netbox.dcim.power_outlet_templates.create(to_create), "Power Outlet")
                                     })
            except pynetbox.RequestError as excep:
                self.handle.log(f"Error '{excep.error}' creating Power Outlet")

    def create_console_server_ports(self, console_server_ports, device_type):
        existing_console_server_ports = {str(item): item for item in self.netbox.dcim.console_server_port_templates.filter(devicetype_id=device_type)}
        to_create = self.get_device_type_ports_to_create(console_server_ports, device_type, existing_console_server_ports)

        if to_create:
            try:
                self.counter.update({'updated':
                                     self.handle.log_device_ports_created(
                                         self.netbox.dcim.console_server_port_templates.create(to_create), "Console Server Port")
                                     })
            except pynetbox.RequestError as excep:
                self.handle.log(f"Error '{excep.error}' creating Console Server Port")

    def create_rear_ports(self, rear_ports, device_type):
        existing_rear_ports = self.get_rear_ports(device_type)
        to_create = self.get_device_type_ports_to_create(rear_ports, device_type, existing_rear_ports)

        if to_create:
            try:
                self.counter.update({'updated':
                                     self.handle.log_device_ports_created(
                                         self.netbox.dcim.rear_port_templates.create(to_create), "Rear Port")
                                     })
            except pynetbox.RequestError as excep:
                self.handle.log(f"Error '{excep.error}' creating Rear Port")

    def create_front_ports(self, front_ports, device_type):
        existing_front_ports = {str(item): item for item in self.netbox.dcim.front_port_templates.filter(devicetype_id=device_type)}
        to_create = self.get_device_type_ports_to_create(front_ports, device_type, existing_front_ports)

        if to_create:
            all_rearports = self.get_rear_ports(device_type)
            for port in to_create:
                try:
                    rear_port = all_rearports[port["rear_port"]]
                    port['rear_port'] = rear_port.id
                except KeyError:
                    self.handle.log(f'Could not find Rear Port for Front Port: {port["name"]} - '
                        + f'{port["type"]} - {device_type}')

            try:
                self.counter.update({'updated':
                                     self.handle.log_device_ports_created(
                                         self.netbox.dcim.front_port_templates.create(to_create), "Front Port")
                                     })
            except pynetbox.RequestError as excep:
                self.handle.log(f"Error '{excep.error}' creating Front Port")

    def create_device_bays(self, device_bays, device_type):
        existing_device_bays = {str(item): item for item in self.netbox.dcim.device_bay_templates.filter(devicetype_id=device_type)}
        to_create = self.get_device_type_ports_to_create(device_bays, device_type, existing_device_bays)

        if to_create:
            try:
                self.counter.update({'updated':
                                     self.handle.log_device_ports_created(
                                         self.netbox.dcim.device_bay_templates.create(to_create), "Device Bay")
                                     })
            except pynetbox.RequestError as excep:
                self.handle.log(f"Error '{excep.error}' creating Device Bay")

    def create_module_bays(self, module_bays, device_type):
        existing_module_bays = {str(item): item for item in self.netbox.dcim.module_bay_templates.filter(devicetype_id=device_type)}
        to_create = self.get_device_type_ports_to_create(module_bays, device_type, existing_module_bays)

        if to_create:
            try:
                self.counter.update({'updated':
                                     self.handle.log_device_ports_created(
                                         self.netbox.dcim.module_bay_templates.create(to_create), "Module Bay")
                                     })
            except pynetbox.RequestError as excep:
                self.handle.log(f"Error '{excep.error}' creating Module Bay")

    def create_module_interfaces(self, module_interfaces, module_type):
        existing_interfaces = {str(item): item for item in self.netbox.dcim.interface_templates.filter(moduletype_id=module_type)}
        to_create = self.get_module_type_ports_to_create(module_interfaces, module_type, existing_interfaces)

        if to_create:
            try:
                self.counter.update({'updated':
                                     self.handle.log_module_ports_created(
                                         self.netbox.dcim.interface_templates.create(to_create), "Module Interface")
                                     })
            except pynetbox.RequestError as excep:
                self.handle.log(f"Error '{excep.error}' creating Module Interface")

    def create_module_power_ports(self, power_ports, module_type):
        existing_power_ports = self.get_module_power_ports(module_type)
        to_create = self.get_module_type_ports_to_create(power_ports, module_type, existing_power_ports)

        if to_create:
            try:
                self.counter.update({'updated':
                                     self.handle.log_module_ports_created(
                                         self.netbox.dcim.power_port_templates.create(to_create), "Module Power Port")
                                     })
            except pynetbox.RequestError as excep:
                self.handle.log(f"Error '{excep.error}' creating Module Power Port")

    def create_module_console_ports(self, console_ports, module_type):
        existing_console_ports = {str(item): item for item in self.netbox.dcim.console_port_templates.filter(moduletype_id=module_type)}
        to_create = self.get_module_type_ports_to_create(console_ports, module_type, existing_console_ports)

        if to_create:
            try:
                self.counter.update({'updated':
                                     self.handle.log_module_ports_created(
                                         self.netbox.dcim.console_port_templates.create(to_create), "Module Console Port")
                                     })
            except pynetbox.RequestError as excep:
                self.handle.log(f"Error '{excep.error}' creating Module Console Port")

    def create_module_power_outlets(self, power_outlets, module_type):
        existing_power_outlets = {str(item): item for item in self.netbox.dcim.power_outlet_templates.filter(moduletype_id=module_type)}
        to_create = self.get_module_type_ports_to_create(power_outlets, module_type, existing_power_outlets)

        if to_create:
            existing_power_ports = self.get_module_power_ports(module_type)
            for outlet in to_create:
                try:
                    power_port = existing_power_ports[outlet["power_port"]]
                    outlet['power_port'] = power_port.id
                except KeyError:
                    pass

            try:
                self.counter.update({'updated':
                                     self.handle.log_module_ports_created(
                                         self.netbox.dcim.power_outlet_templates.create(to_create), "Module Power Outlet")
                                     })
            except pynetbox.RequestError as excep:
                self.handle.log(f"Error '{excep.error}' creating Module Power Outlet")

    def create_module_console_server_ports(self, console_server_ports, module_type):
        existing_console_server_ports = {str(item): item for item in self.netbox.dcim.console_server_port_templates.filter(moduletype_id=module_type)}
        to_create = self.get_module_type_ports_to_create(console_server_ports, module_type, existing_console_server_ports)

        if to_create:
            try:
                self.counter.update({'updated':
                                     self.handle.log_module_ports_created(
                                         self.netbox.dcim.console_server_port_templates.create(to_create), "Module Console Server Port")
                                     })
            except pynetbox.RequestError as excep:
                self.handle.log(f"Error '{excep.error}' creating Module Console Server Port")

    def create_module_rear_ports(self, rear_ports, module_type):
        existing_rear_ports = self.get_module_rear_ports(module_type)
        to_create = self.get_module_type_ports_to_create(rear_ports, module_type, existing_rear_ports)

        if to_create:
            try:
                self.counter.update({'updated':
                                     self.handle.log_module_ports_created(
                                         self.netbox.dcim.rear_port_templates.create(to_create), "Module Rear Port")
                                     })
            except pynetbox.RequestError as excep:
                self.handle.log(f"Error '{excep.error}' creating Module Rear Port")

    def create_module_front_ports(self, front_ports, module_type):
        existing_front_ports = {str(item): item for item in self.netbox.dcim.front_port_templates.filter(moduletype_id=module_type)}
        to_create = self.get_module_type_ports_to_create(front_ports, module_type, existing_front_ports)

        if to_create:
            existing_rear_ports = self.get_module_rear_ports(module_type)
            for port in to_create:
                try:
                    rear_port = existing_rear_ports[port["rear_port"]]
                    port['rear_port'] = rear_port.id
                except KeyError:
                    self.handle.log(f'Could not find Rear Port for Front Port: {port["name"]} - '
                        + f'{port["type"]} - {module_type}')

            try:
                self.counter.update({'updated':
                                     self.handle.log_module_ports_created(
                                         self.netbox.dcim.front_port_templates.create(to_create), "Module Front Port")
                                     })
            except pynetbox.RequestError as excep:
                self.handle.log(f"Error '{excep.error}' creating Module Front Port")

    def upload_images(self,baseurl,token,images,device_type):
        '''Upload front_image and/or rear_image for the given device type

        Args:
        baseurl: URL for Netbox instance
        token: Token to access Netbox instance
        images: map of front_image and/or rear_image filename
        device_type: id for the device-type to update

        Returns:
        None
        '''
        url = f"{baseurl}/api/dcim/device-types/{device_type}/"
        headers = { "Authorization": f"Token {token}" }

        files = { i: (os.path.basename(f), open(f,"rb") ) for i,f in images.items() }
        response = requests.patch(url, headers=headers, files=files, verify=(not self.ignore_ssl))

        self.handle.log( f'Images {images} updated at {url}: {response}' )
        self.counter["images"] += len(images)
