# Netbox Device Type Import

This library is intended to be your friend and help you import all the device-types defined within the the [NetBox Device Type Library Repository](https://github.com/netbox-community/devicetype-library).

## 🪄 Description

This script will clone a copy of the `netbox-community/devicetype-library` repository to your machine to allow it to import the device types you would like without copy and pasting them into the Netbox UI.

## 🚀 Getting Started

1. This script is written in Python, so lets setup a virtual environment.

```
git clone https://github.com/netbox-community/Device-Type-Library-Import.git
cd Device-Type-Library-Import
python3 -m venv venv
source venv/bin/activate
```

2. Now that we have the basics setup, we'll need to install the requirements.

```
pip install -r requirements.txt
```

3. There are two variables that are required when using this script to import device types into your Netbox installation. (1) Your Netbox instance URL and (2) a token with **write rights**.

Copy the existing `.env.example` to your own `.env` file, and fill in the variables.

```
cp .env.example .env
vim .env
```

Finally, we are able to execute the script and import some device templates!

## 🔌 Usage

To use the script, simply execute the script as follows. Make sure you're still in the activated virtual environment we created before.

```
./nb-dt-import.py
```

This will clone the latest master branch from the `netbox-community/devicetype-library` from Github and install it into the `repo` subdirectory. If this directory already exists, it will perform a `git pull` to update the repository instead.

Next, it will loop over every manufacturer and every device of every manufacturer and begin checking if your Netbox install already has them, and if not, creates them. It will skip preexisting manufacturers, devices, interfaces, etc. so as to not end up with duplicate entries in your Netbox instance.

### 🧰 Arguments

This script currently accepts a list of vendors as an argument, so that you can selectively import devices.

To import only device by APC, for example:

```
./nb-dt-import.py --vendors apc
```

`--vendors` can also accept a comma separated list of vendors if you want to import multiple.

```
./nb-dt-import.py --vendors apc,juniper
```

## Docker build

It's possible to use this project as a docker container.

To build :

```
docker build -t netbox-devicetype-import-library .
```

Alternatively you can pull a pre-built image from Github Container Registry (ghcr.io):

```
docker pull ghcr.io/minitriga/netbox-device-type-library-import
```

The container supports the following env var as configuration :

- `REPO_URL`, the repo to look for device types (defaults to _https://github.com/netbox-community/devicetype-library.git_)
- `REPO_BRANCH`, the branch to check out if appropriate, defaults to master.
- `NETBOX_URL`, used to access netbox
- `NETBOX_TOKEN`, token for accessing netbox
- `VENDORS`, a comma-separated list of vendors to import (defaults to None)

To run :

```
docker run -e "NETBOX_URL=http://netbox:8080/" -e "NETBOX_TOKEN=98765434567890" ghcr.io/minitriga/netbox-device-type-library-import
```

## 🧑‍💻 Contributing

We're happy about any pull requests!

## 📜 License

MIT
