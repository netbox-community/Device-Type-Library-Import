import os
from dotenv import load_dotenv
load_dotenv()

REPO_URL = str(os.getenv("REPO_URL"))
NETBOX_URL = str(os.getenv("NETBOX_URL"))
NETBOX_TOKEN = str(os.getenv("NETBOX_TOKEN"))

# optionnally load vendors through a space separated list as env var
try:
    VENDORS = os.getenv("VENDORS").split(" ") 
except AttributeError:
    VENDORS = None

MANDATORY_ENV_VARS = ["REPO_URL", "NETBOX_URL", "NETBOX_TOKEN"]

for var in MANDATORY_ENV_VARS:
    if var not in os.environ:
        raise EnvironmentError("Failed because {} is not set.".format(var))
