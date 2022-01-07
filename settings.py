import os
from dotenv import load_dotenv
load_dotenv()

REPO_URL = os.getenv("REPO_URL")
REPO_BRANCH = os.getenv("REPO_BRANCH", "master")
NETBOX_URL = os.getenv("NETBOX_URL")
NETBOX_TOKEN = os.getenv("NETBOX_TOKEN")
IGNORE_SSL_ERRORS = (os.getenv("IGNORE_SSL_ERRORS", "False") == "True")

# optionally load vendors through a comma separated list as env var
VENDORS = list(filter(None, os.getenv("VENDORS", "").split(",")))

# optionally load device types through a space separated list as env var
SLUGS = os.getenv("SLUGS", "").split()


MANDATORY_ENV_VARS = ["REPO_URL", "NETBOX_URL", "NETBOX_TOKEN"]

for var in MANDATORY_ENV_VARS:
    if var not in os.environ:
        raise EnvironmentError("Failed because {} is not set.".format(var))
