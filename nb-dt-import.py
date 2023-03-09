#!/usr/bin/env python3
from collections import Counter
from datetime import datetime
import yaml
import pynetbox
from glob import glob
import os

import settings
from netbox_api import NetBox

counter = Counter(
            added=0,
            updated=0,
            manufacturer=0,
            module_added=0,
            module_port_added=0,
        )


    
def create_module_interfaces(interfaces, module_type, nb):
    all_interfaces = {str(item): item for item in nb.dcim.interface_templates.filter(moduletype_id=module_type)}
    need_interfaces = []
    for interface in interfaces:
        try:
            if_res = all_interfaces[interface["name"]]
            settings.handle.verbose_log(f'Module Interface Template Exists: {if_res.name} - {if_res.type}'
                  + f' - {if_res.module_type.id} - {if_res.id}')
        except KeyError:
            interface['module_type'] = module_type
            need_interfaces.append(interface)

    if not need_interfaces:
        return

    try:
        ifSuccess = nb.dcim.interface_templates.create(need_interfaces)
        for intf in ifSuccess:
            settings.handle.verbose_log(f'Module Interface Template Created: {intf.name} - '
              + f'{intf.type} - {intf.module_type.id} - '
              + f'{intf.id}')
            counter.update({'module_port_added': 1})
    except pynetbox.RequestError as e:
        print(e.error)


def create_module_console_ports(consoleports, module_type, nb):

    all_consoleports = {str(item): item for item in nb.dcim.console_port_templates.filter(moduletype_id=module_type)}
    need_consoleports = []
    for consoleport in consoleports:
        try:
            cpGet = all_consoleports[consoleport["name"]]
            settings.handle.verbose_log(f'Console Port Template Exists: {cpGet.name} - '
                  + f'{cpGet.type} - {cpGet.module_type.id} - {cpGet.id}')
        except KeyError:
            consoleport['module_type'] = module_type
            need_consoleports.append(consoleport)

    if not need_consoleports:
        return

    try:
        cpSuccess = nb.dcim.console_port_templates.create(need_consoleports)
        for port in cpSuccess:
            settings.handle.verbose_log(f'Console Port Created: {port.name} - {port.type} - ' +
                f'{port.module_type.id} - {port.id}')
            counter.update({'module_port_added': 1})
    except pynetbox.RequestError as e:
        print(f"Error creating module console port: {e.error}")


def create_module_power_ports(powerports, module_type, nb):
    all_power_ports = {str(item): item for item in nb.dcim.power_port_templates.filter(moduletype_id=module_type)}
    need_power_ports = []
    for powerport in powerports:
        try:
            ppGet = all_power_ports[powerport["name"]]
            settings.handle.verbose_log(f'Power Port Template Exists: {ppGet.name} - ' +
                f'{ppGet.type} - {ppGet.module_type.id} - {ppGet.id}')
        except KeyError:
            powerport['module_type'] = module_type
            need_power_ports.append(powerport)

    if not need_power_ports:
        return

    try:
        ppSuccess = nb.dcim.power_port_templates.create(need_power_ports)
        for pp in ppSuccess:
            settings.handle.verbose_log(f'Power port template created: {pp.name} - '
              + f'{pp.type} - {pp.module_type.id} - {pp.id}')
            counter.update({'module_port_added': 1})
    except pynetbox.RequestError as e:
        print(e.error)
        

def create_module_console_server_ports(consoleserverports, module_type, nb):
    all_consoleserverports = {str(item): item for item in nb.dcim.console_server_port_templates.filter(moduletype_id=module_type)}
    need_consoleserverports = []
    for csport in consoleserverports:
        try:
            cspGet = all_consoleserverports[csport["name"]]
            settings.handle.verbose_log(f'Console Server Port Template Exists: {cspGet.name} - '
                  + f'{cspGet.type} - {cspGet.module_type.id} - '
                  + f'{cspGet.id}')
        except KeyError:
            csport['module_type'] = module_type
            need_consoleserverports.append(csport)

    if not need_consoleserverports:
        return

    try:
        cspSuccess = nb.dcim.console_server_port_templates.create(
            need_consoleserverports)
        for csp in cspSuccess:
            settings.handle.verbose_log(f'Console Server Port Created: {csp.name} - '
                  + f'{csp.type} - {csp.module_type.id} - '
                  + f'{csp.id}')
            counter.update({'module_port_added': 1})
    except pynetbox.RequestError as e:
        print(e.error)



def create_module_front_ports(frontports, module_type, nb):
    all_frontports = {str(item): item for item in nb.dcim.front_port_templates.filter(moduletype_id=module_type)}
    need_frontports = []
    for frontport in frontports:
        try:
            fpGet = all_frontports[frontport["name"]]
            settings.handle.verbose_log(f'Front Port Template Exists: {fpGet.name} - '
                  + f'{fpGet.type} - {fpGet.module_type.id} - {fpGet.id}')
        except KeyError:
            frontport['module_type'] = module_type
            need_frontports.append(frontport)

    if not need_frontports:
        return

    all_rearports = {str(item): item for item in nb.dcim.rear_port_templates.filter(moduletype_id=module_type)}
    for port in need_frontports:
        try:
            rpGet = all_rearports[port["rear_port"]]
            port['rear_port'] = rpGet.id
        except KeyError:
            print(f'Could not find Rear Port for Front Port: {port["name"]} - '
                  + f'{port["type"]} - {module_type}')

    try:
        fpSuccess = nb.dcim.front_port_templates.create(need_frontports)
        for fp in fpSuccess:
            settings.handle.verbose_log(f'Front Port Created: {fp.name} - '
                  + f'{fp.type} - {fp.module_type.id} - '
                  + f'{fp.id}')
            counter.update({'module_port_added': 1})
    except pynetbox.RequestError as e:
        print(e.error)

def create_module_rear_ports(rearports, module_type, nb):
    all_rearports = {str(item): item for item in nb.dcim.rear_port_templates.filter(moduletype_id=module_type)}
    need_rearports = []
    for rearport in rearports:
        try:
            rpGet = all_rearports[rearport["name"]]
            settings.handle.verbose_log(f'Rear Port Template Exists: {rpGet.name} - {rpGet.type}'
                  + f' - {rpGet.module_type.id} - {rpGet.id}')
        except KeyError:
            rearport['module_type'] = module_type
            need_rearports.append(rearport)

    if not need_rearports:
        return

    try:
        rpSuccess = nb.dcim.rear_port_templates.create(
            need_rearports)
        for rp in rpSuccess:
            settings.handle.verbose_log(f'Rear Port Created: {rp.name} - {rp.type}'
                  + f' - {rp.module_type.id} - {rp.id}')
            counter.update({'module_port_added': 1})
    except pynetbox.RequestError as e:
        print(e.error)


def create_module_power_outlets(poweroutlets, module_type, nb):
    '''Create missing module power outlets.

    Args:
        poweroutlets: YAML power outlet data.
        module_type: Netbox module_type instance.
        nb: pynetbox API instance.

    Returns:
        None

    Raises:
        None
    '''
    all_poweroutlets = {str(item): item for item in nb.dcim.power_outlet_templates.filter(moduletype_id=module_type)}
    need_poweroutlets = []
    for poweroutlet in poweroutlets:
        try:
            poGet = all_poweroutlets[poweroutlet["name"]]
            settings.handle.verbose_log(f'Power Outlet Template Exists: {poGet.name} - {poGet.type}'
                  + f' - {poGet.module_type.id} - {poGet.id}')
        except KeyError:
            poweroutlet["module_type"] = module_type
            need_poweroutlets.append(poweroutlet)

    if not need_poweroutlets:
        return

    all_power_ports = {str(item): item for item in nb.dcim.\
        power_port_templates.filter(moduletype_id=module_type)}
    for outlet in need_poweroutlets:
        try:
            ppGet = all_power_ports[outlet["power_port"]]
            outlet['power_port'] = ppGet.id
        except KeyError:
            pass

    try:
        poSuccess = nb.dcim.power_outlet_templates.create(
            need_poweroutlets)
        for po in poSuccess:
            settings.handle.verbose_log(f'Power Outlet Created: {po.name} - '
                  + f'{po.type} - {po.module_type.id} - '
                  + f'{po.id}')
            counter.update({'module_port_added': 1})
    except pynetbox.RequestError as e:
        print(e.error)

def create_device_types(device_types, netbox):
    all_device_types = netbox.device_types.existing_device_types
    nb = netbox.netbox
    for deviceType in device_types:
        try:
            dt = all_device_types[deviceType["model"]]
            settings.handle.verbose_log(f'Device Type Exists: {dt.manufacturer.name} - '
                  + f'{dt.model} - {dt.id}')
        except KeyError:
            try:
                dt = nb.dcim.device_types.create(deviceType)
                counter.update({'added': 1})
                settings.handle.verbose_log(f'Device Type Created: {dt.manufacturer.name} - '
                      + f'{dt.model} - {dt.id}')
            except pynetbox.RequestError as e:
                print(e.error)

        if "interfaces" in deviceType:
            netbox.device_types.create_interfaces(deviceType["interfaces"], dt.id)
        if "power-ports" in deviceType:
            netbox.device_types.create_power_ports(deviceType["power-ports"], dt.id)
        if "power-port" in deviceType:
            netbox.device_types.create_power_ports(deviceType["power-port"], dt.id)
        if "console-ports" in deviceType:
            netbox.device_types.create_console_ports(deviceType["console-ports"], dt.id)
        if "power-outlets" in deviceType:
            netbox.device_types.create_power_outlets(deviceType["power-outlets"], dt.id)
        if "console-server-ports" in deviceType:
            netbox.device_types.create_console_server_ports(deviceType["console-server-ports"], dt.id)
        if "rear-ports" in deviceType:
            netbox.device_types.create_rear_ports(deviceType["rear-ports"], dt.id)
        if "front-ports" in deviceType:
            netbox.device_types.create_front_ports(deviceType["front-ports"], dt.id)
        if "device-bays" in deviceType:
            netbox.device_types.create_device_bays(deviceType["device-bays"], dt.id)
        if netbox.modules and 'module-bays' in deviceType:
            netbox.device_types.create_module_bays(deviceType['module-bays'], dt.id)

def create_module_types(module_types, nb):
    '''Create missing module types.

    Args:
        module_types: yaml data from repo.
        nb: pynetbox API instance

    Returns:
        None
    '''

    all_module_types = {}
    for curr_nb_mt in nb.dcim.module_types.all():
        if curr_nb_mt.manufacturer.slug not in all_module_types:
            all_module_types[curr_nb_mt.manufacturer.slug] = {}

        all_module_types[curr_nb_mt.manufacturer.slug][curr_nb_mt.model] = curr_nb_mt


    for curr_mt in module_types:
        try:
            module_type_res = all_module_types[curr_mt['manufacturer']['slug']][curr_mt["model"]]
            settings.handle.verbose_log(f'Module Type Exists: {module_type_res.manufacturer.name} - '
                + f'{module_type_res.model} - {module_type_res.id}')
        except KeyError:
            try:
                module_type_res = nb.dcim.module_types.create(curr_mt)
                counter.update({'module_added': 1})
                settings.handle.verbose_log(f'Module Type Created: {module_type_res.manufacturer.name} - '
                      + f'{module_type_res.model} - {module_type_res.id}')
            except pynetbox.RequestError as exce:
                print(f"Error '{exce.error}' creating module type: " +
                    f"{curr_mt}")

        #module_type_res = all_module_types[curr_mt['manufacturer']['slug']][curr_mt["model"]]

        if "interfaces" in curr_mt:
            create_module_interfaces(curr_mt["interfaces"],
                                     module_type_res.id, nb)
        if "power-ports" in curr_mt:
            create_module_power_ports(curr_mt["power-ports"],
                                      module_type_res.id, nb)
        if "console-ports" in curr_mt:
            create_module_console_ports(curr_mt["console-ports"],
                                        module_type_res.id, nb)
        if "power-outlets" in curr_mt: # No current entries to test
            create_module_power_outlets(curr_mt["power-outlets"],
                                        module_type_res.id, nb)
        if "console-server-ports" in curr_mt: # No current entries to test
            create_module_console_server_ports(curr_mt["console-server-ports"],
                                               module_type_res.id, nb)
        if "rear-ports" in curr_mt:
            create_module_rear_ports(curr_mt["rear-ports"],
                                     module_type_res.id, nb)
        if "front-ports" in curr_mt:
            create_module_front_ports(curr_mt["front-ports"],
                                      module_type_res.id, nb)

def main():
    startTime = datetime.now()
    args = settings.args

    netbox = NetBox(settings)
    nb = netbox.get_api()
    files, vendors = settings.dtl_repo.get_devices(f'{settings.dtl_repo.repo_path}/device-types/', args.vendors)

    settings.handle.log(f'{len(vendors)} Vendors Found')
    device_types = settings.dtl_repo.parse_files(files, slugs=args.slugs)
    settings.handle.log(f'{len(device_types)} Device-Types Found')
    netbox.create_manufacturers(vendors)
    create_device_types(device_types, netbox)

    if netbox.modules:
        settings.handle.log("Modules Enabled. Creating Modules...")
        files, vendors = settings.dtl_repo.get_devices(f'{settings.dtl_repo.repo_path}/module-types/', args.vendors)
        settings.handle.log(f'{len(vendors)} Module Vendors Found')
        module_types = settings.dtl_repo.parse_files(files, slugs=args.slugs)
        settings.handle.log(f'{len(module_types)} Module-Types Found')
        netbox.create_manufacturers(vendors)
        create_module_types(module_types, nb)

    settings.handle.log('---')
    settings.handle.verbose_log(f'Script took {(datetime.now() - startTime)} to run')
    settings.handle.log(f'{counter["added"]} devices created')
    settings.handle.log(f'{counter["updated"]} interfaces/ports updated')
    settings.handle.log(f'{netbox.counter["manufacturer"]} manufacturers created')
    if settings.NETBOX_FEATURES['modules']:
        settings.handle.log(f'{counter["module_added"]} modules created')
        settings.handle.log(f'{counter["module_port_added"]} module interface / ports created')

if __name__ == "__main__":
    main()
