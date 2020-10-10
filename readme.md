# Netbox Device Type Import

This library is intended to be your friend and help you import all the device-types defined within the the [NetBox Device Type Library Repository](https://github.com/netbox-community/devicetype-library).

> Tested working with 2.7.8, 2.8.8, 2.9.4

## Getting Started

These instructions will get you a copy of the project on your machine to allow you to import the device types you would like without copy and pasting them into the NetBox UI.

### Prerequisites

This script is written in python so this must be installed. 

```
Python3
Python PIP
```

## Using the Repo

Cloning the repo

```
git clone https://github.com/minitriga/Netbox-Device-Type-Library-Import.git
```

Installing the requirements

```
cd Netbox-Device-Type-Library-Import
pip install -r requirements.txt
```

### Setting your variables

There are a number of variables that are required when using this script to import device types into your netbox environment. 

```
export NETBOX_URL=http://netbox.company.com
export NETBOX_TOKEN=0123456789abcdef0123456789abcdef01234567
```

### Using the script

To use the script simply run the following.

```
python nb-dt-import.py
```

This will pull the device-type library from Gitlab and install it into the `.repo` directory. if this directory is already there it will perform a git pull to update the reposity.

#### Arguments

This script currently accepts vendors so that only a few vendors are imported into your NetBox Environment. 

This can be done the following.

```
python nb-dt-import.py --vendor apc
```

`--vendor` also accepts a list of vendors so that multiple vendors could be imported. 

```
python nb-dt-import.py --vendor apc juniper
```
