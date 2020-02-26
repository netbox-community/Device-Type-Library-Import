import os

NETBOX_URL = str(os.getenv("NETBOX_URL"))
NETBOX_TOKEN = str(os.getenv("NETBOX_TOKEN"))

MANDATORY_ENV_VARS = ["NETBOX_URL", "NETBOX_TOKEN"]

for var in MANDATORY_ENV_VARS:
    if var not in os.environ:
        raise EnvironmentError("Failed because {} is not set.".format(var))