from git import Repo, exc, RemoteProgress
from collections import Counter
import yaml, pynetbox, glob, argparse, os, settings

parser = argparse.ArgumentParser(description='Import Netbox Device Types')
parser.add_argument('--vendor', nargs='+', help="List of vendors to import eg. apc cisco")
parser.add_argument('--url','--git', default='https://github.com/netbox-community/devicetype-library.git', help="Git URL with valid Device Type YAML files")
args = parser.parse_args()

cwd = os.getcwd()
counter = Counter(added=0,updated=0,manufacturer=0)
nbUrl = settings.NETBOX_URL
nbToken = settings.NETBOX_TOKEN

def update_package(path: str):
    try:
        repo = Repo(path)
        if repo.remotes.origin.url.endswith('.git'):
            repo.remotes.origin.pull()
            print("Pulled Repo")
    except exc.InvalidGitRepositoryError:
        pass

def getFiles(vendors=None):
    files = []
    discoveredVendors = []
    if vendors:
        for r, d, f in os.walk('./repo/device-types/'):
            for folder in d:
                for vendor in vendors:
                    if vendor.lower() == folder.lower():
                        discoveredVendors.append({'name': folder, 'slug': folder.lower()})
                        files.extend(glob.glob('./repo/device-types/' + folder + '/*.yaml'))
    else:
        for r, d, f in os.walk('./repo/device-types/'):
            for folder in d:
                if folder.lower() != "Testing":
                    discoveredVendors.append({'name': folder, 'slug': folder.lower()})
        files.extend(glob.glob('./repo/device-types/[!Testing]*/*.yaml'))
    return files, discoveredVendors

def readYAMl(files):
    deviceTypes = []
    manufacturers = []
    for file in files:
        with open(file, 'r') as stream:
            try:
                data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
            manufacturer = data['manufacturer']
            data['manufacturer'] = {}
            data['manufacturer']['name'] = manufacturer
            data['manufacturer']['slug'] = manufacturer.lower()
        deviceTypes.append(data)
        manufacturers.append(manufacturer)
    return deviceTypes

def createManufacturers(vendors, nb):
    for vendor in vendors:
        try:
            manGet = nb.dcim.manufacturers.get(name=vendor["name"])
            if manGet:
                print(f'Manufacturer Exists: {manGet.name} - {manGet.id}')
            else:
                manSuccess = nb.dcim.manufacturers.create(vendor)
                print(f'Manufacturer Created: {manSuccess.name} - {manSuccess.id}')
                counter.update({'manufacturer':1})
        except pynetbox.RequestError as e:
            print(e.error) 

def createInterfaces(interfaces, deviceType, nb):
    for interface in interfaces:
        interface['device_type'] = deviceType
        try:
            ifGet = nb.dcim.interface_templates.get(devicetype_id=deviceType, name=interface["name"])
            if ifGet:
                print(f'Interface Template Exists: {ifGet.name} - {ifGet.type} - {ifGet.device_type.id} - {ifGet.id}')
            else:
                ifSuccess = nb.dcim.interface_templates.create(interface)
                print(f'Interface Template Created: {ifSuccess.name} - {ifSuccess.type} - {ifSuccess.device_type.id} - {ifSuccess.id}')
                counter.update({'updated':1})
        except pynetbox.RequestError as e:
            print(e.error)

def createConsolePorts(consoleports, deviceType, nb):
    for consoleport in consoleports:
        consoleport['device_type'] = deviceType
        try:
            cpGet = nb.dcim.console_port_templates.get(devicetype_id=deviceType, name=consoleport["name"])
            if cpGet:
                print(f'Console Port Template Exists: {cpGet.name} - {cpGet.type} - {cpGet.device_type.id} - {cpGet.id}')
            else:
                cpSuccess = nb.dcim.console_port_templates.create(consoleport)
                print(f'Console Port Created: {cpSuccess.name} - {cpSuccess.type} - {cpSuccess.device_type.id} - {cpSuccess.id}')
                counter.update({'updated':1})
        except pynetbox.RequestError as e:
            print(e.error)

def createPowerPorts(powerports, deviceType, nb):
    for powerport in powerports:
        powerport['device_type'] = deviceType
        try:
            ppGet = nb.dcim.power_port_templates.get(devicetype_id=deviceType, name=powerport["name"])
            if ppGet:
                print(f'Power Port Template Exists: {ppGet.name} - {ppGet.type} - {ppGet.device_type.id} - {ppGet.id}')
            else:
                ppSuccess = nb.dcim.power_port_templates.create(powerport)
                print(f'Power Port Created: {ppSuccess.name} - {ppSuccess.type} - {ppSuccess.device_type.id} - {ppSuccess.id}')
                counter.update({'updated':1})
        except pynetbox.RequestError as e:
            print(e.error)

def createConsoleServerPorts(consoleserverports, deviceType, nb):
    for csport in consoleserverports:
        csport['device_type'] = deviceType
        try:
            cspGet = nb.dcim.console_server_port_templates.get(devicetype_id=deviceType, name=csport["name"])
            if cspGet:
                print(f'Console Server Port Template Exists: {cspGet.name} - {cspGet.type} - {cspGet.device_type.id} - {cspGet.id}')
            else:
                cspSuccess = nb.dcim.console_server_port_templates.create(csport)
                print(f'Console Server Port Created: {cspSuccess.name} - {cspSuccess.type} - {cspSuccess.device_type.id} - {cspSuccess.id}')
                counter.update({'updated':1})
        except pynetbox.RequestError as e:
            print(e.error) 

def createFrontPorts(frontports, deviceType, nb):
    for frontport in frontports:
        frontport['device_type'] = deviceType
        try:
            fpGet = nb.dcim.front_port_templates.get(devicetype_id=deviceType, name=frontport["name"])
            if fpGet:
                print(f'Front Port Template Exists: {fpGet.name} - {fpGet.type} - {fpGet.device_type.id} - {fpGet.id}')
            else:
                rpGet = nb.dcim.rear_port_templates.get(devicetype_id=deviceType, name=frontport["rear_port"])
                if rpGet:
                    frontport['rear_port'] = rpGet.id
                    fpSuccess = nb.dcim.front_port_templates.create(frontport)
                    print(f'Front Port Created: {fpSuccess.name} - {fpSuccess.type} - {fpSuccess.device_type.id} - {fpSuccess.id}')
                counter.update({'updated':1})
        except pynetbox.RequestError as e:
            print(e.error) 

def createRearPorts(rearports, deviceType, nb):
    for rearport in rearports:
        rearport['device_type'] = deviceType
        try:
            rpGet = nb.dcim.rear_port_templates.get(devicetype_id=deviceType, name=rearport["name"])
            if rpGet:
                print(f'Rear Port Template Exists: {rpGet.name} - {rpGet.type} - {rpGet.device_type.id} - {rpGet.id}')
            else:
                rpSuccess = nb.dcim.rear_port_templates.create(rearport)
                print(f'Rear Port Created: {rpSuccess.name} - {rpSuccess.type} - {rpSuccess.device_type.id} - {rpSuccess.id}')
                counter.update({'updated':1})
        except pynetbox.RequestError as e:
            print(e.error)

def createDeviceBays(devicebays, deviceType, nb):
    for devicebay in devicebays:
        devicebay['device_type'] = deviceType
        try:
            dbGet = nb.dcim.device_bay_templates.get(devicetype_id=deviceType, name=devicebay["name"])
            if dbGet:
                print(f'Device Bay Template Exists: {dbGet.name} - {dbGet.device_type.id} - {dbGet.id}')
            else:
                dbSuccess = nb.dcim.device_bay_templates.create(devicebay)
                print(f'Device Bay Created: {dbSuccess.name} - {dbSuccess.device_type.id} - {dbSuccess.id}')
                counter.update({'updated':1})
        except pynetbox.RequestError as e:
            print(e.error)

def createPowerOutlets(poweroutlets, deviceType, nb):
    for poweroutlet in poweroutlets:
        try:
            poGet = nb.dcim.power_outlet_templates.get(devicetype_id=deviceType, name=poweroutlet["name"])
            if poGet:
                print(f'Power Outlet Template Exists: {poGet.name} - {poGet.type} - {poGet.device_type.id} - {poGet.id}')
            else:
                try:
                    ppGet = nb.dcim.power_port_templates.get(devicetype_id=deviceType)
                    if ppGet:
                        poweroutlet["power_port"] = ppGet.id
                        poweroutlet["device_type"] = deviceType
                        poSuccess = nb.dcim.power_outlet_templates.create(poweroutlet)
                        print(f'Power Outlet Created: {poSuccess.name} - {poSuccess.type} - {poSuccess.device_type.id} - {poSuccess.id}')
                        counter.update({'updated':1})
                except:
                    poweroutlet["device_type"] = deviceType
                    poSuccess = nb.dcim.power_outlet_templates.create(poweroutlet)
                    print(f'Power Outlet Created: {poSuccess.name} - {poSuccess.type} - {poSuccess.device_type.id} - {poSuccess.id}')
                    counter.update({'updated':1})
        except pynetbox.RequestError as e:
            print(e.error) 

def createDeviceTypes(deviceTypes, nb):
    for deviceType in deviceTypes:
        try:
            dtGet = nb.dcim.device_types.get(model=deviceType["model"])
            if dtGet:
                print(f'Device Type Exists: {dtGet.manufacturer.name} - {dtGet.model} - {dtGet.id}')
                if "interfaces" in deviceType:
                    createInterfaces(deviceType["interfaces"], dtGet.id, nb)
                if "power-ports" in deviceType:
                    createPowerPorts(deviceType["power-ports"], dtGet.id, nb)
                if "power-port" in deviceType:
                    createPowerPorts(deviceType["power-port"], dtGet.id, nb)
                if "console-ports" in deviceType:
                    createConsolePorts(deviceType["console-ports"], dtGet.id, nb)
                if "power-outlets" in deviceType:
                    createPowerOutlets(deviceType["power-outlets"], dtGet.id, nb)
                if "console-server-ports" in deviceType:
                    createConsoleServerPorts(deviceType["console-server-ports"], dtGet.id, nb)
                if "rear-ports" in deviceType:
                    createRearPorts(deviceType["rear-ports"], dtGet.id, nb)
                if "front-ports" in deviceType:
                    createFrontPorts(deviceType["front-ports"], dtGet.id, nb)
                if "device-bays" in deviceType:
                    createDeviceBays(deviceType["device-bays"], dtGet.id, nb)
            else:
                dtSuccess = nb.dcim.device_types.create(deviceType)
                counter.update({'added':1})
                print(f'Device Type Created: {dtSuccess.manufacturer.name} - {dtSuccess.model} - {dtSuccess.id}')
                if "interfaces" in deviceType:
                    createInterfaces(deviceType["interfaces"], dtSuccess.id, nb)
                if "power-ports" in deviceType:
                    createPowerPorts(deviceType["power-ports"], dtSuccess.id, nb)
                if "power-port" in deviceType:
                    createPowerPorts(deviceType["power-port"], dtSuccess.id, nb)
                if "console-ports" in deviceType:
                    createConsolePorts(deviceType["console-ports"], dtSuccess.id, nb)
                if "power-outlets" in deviceType:
                    createPowerOutlets(deviceType["power-outlets"], dtSuccess.id, nb)
                if "console-server-ports" in deviceType:
                    createConsoleServerPorts(deviceType["console-server-ports"], dtSuccess.id, nb)
                if "rear-ports" in deviceType:
                    createRearPorts(deviceType["rear-ports"], dtSuccess.id, nb)
                if "front-ports" in deviceType:
                    createFrontPorts(deviceType["front-ports"], dtSuccess.id, nb)
                if "device-bays" in deviceType:
                    createDeviceBays(deviceType["device-bays"], dtSuccess.id, nb)
        except pynetbox.RequestError as e:
            print(e.error)

try:
    if os.path.isdir('./repo'):
        msg = 'Package devicetype-library is already installed, updating'
        update_package('./repo')
        print(msg)
    else:
        repo = Repo.clone_from(args.url, os.path.join(cwd, 'repo'))
        print("Package Installed")
except exc.GitCommandError as error:
    print("Couldn't clone {} ({})".format(args.url, error))

nb = pynetbox.api(nbUrl, token=nbToken)

if args.vendor is None:
    print("No Vendor Specified, Gathering All Device-Types")
    files, vendors = getFiles()
    print(str(len(vendors)) + " Vendors Found")
    print(str(len(files)) + " Device-Types Found")
    deviceTypes = readYAMl(files)
    createManufacturers(vendors, nb)
    createDeviceTypes(deviceTypes, nb)

else:
    print("Vendor Specified, Gathering All Matching Device-Types")
    files, vendors = getFiles(args.vendor)
    print(str(len(vendors)) + " Vendors Found")
    print(str(len(files)) + " Device-Types Found")
    deviceTypes = readYAMl(files)
    createManufacturers(vendors, nb)
    createDeviceTypes(deviceTypes, nb)

print('---')
print('{} devices created'.format(counter['added']))
print('{} interfaces/ports updated'.format(counter['updated']))
print('{} manufacturers created'.format(counter['manufacturer']))
