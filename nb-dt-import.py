#!/usr/bin/env python3
from collections import Counter
from datetime import datetime
import yaml
import pynetbox
from glob import glob
import os

import settings
from netbox_api import NetBox


def main():
    startTime = datetime.now()
    args = settings.args

    netbox = NetBox(settings)
    files, vendors = settings.dtl_repo.get_devices(
        f'{settings.dtl_repo.repo_path}/device-types/', args.vendors)

    settings.handle.log(f'{len(vendors)} Vendors Found')
    device_types = settings.dtl_repo.parse_files(files, slugs=args.slugs)
    settings.handle.log(f'{len(device_types)} Device-Types Found')
    files = settings.dtl_repo.get_device_roles(
        f'{settings.dtl_repo.repo_path}/device-roles/')
    device_roles = settings.dtl_repo.parse_device_roles_files(files)
    settings.handle.log(f'{len(device_roles)} Device Roles Found')
    netbox.create_manufacturers(vendors)
    netbox.create_device_roles(device_roles)
    netbox.create_device_types(device_types)

    if netbox.modules:
        settings.handle.log("Modules Enabled. Creating Modules...")
        files, vendors = settings.dtl_repo.get_devices(
            f'{settings.dtl_repo.repo_path}/module-types/', args.vendors)
        settings.handle.log(f'{len(vendors)} Module Vendors Found')
        module_types = settings.dtl_repo.parse_files(files, slugs=args.slugs)
        settings.handle.log(f'{len(module_types)} Module-Types Found')
        netbox.create_manufacturers(vendors)
        netbox.create_module_types(module_types)

    settings.handle.log('---')
    settings.handle.verbose_log(
        f'Script took {(datetime.now() - startTime)} to run')
    settings.handle.log(f'{netbox.counter["added"]} devices created')
    settings.handle.log(f'{netbox.counter["images"]} images uploaded')
    settings.handle.log(
        f'{netbox.counter["updated"]} interfaces/ports updated')
    settings.handle.log(
        f'{netbox.counter["manufacturer"]} manufacturers created')
    settings.handle.log(
        f'{netbox.counter["device_role"]} device roles created')
    if settings.NETBOX_FEATURES['modules']:
        settings.handle.log(
            f'{netbox.counter["module_added"]} modules created')
        settings.handle.log(
            f'{netbox.counter["module_port_added"]} module interface / ports created')


if __name__ == "__main__":
    main()
