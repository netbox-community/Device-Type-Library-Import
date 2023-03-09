from argparse import ArgumentParser
import os
from log_handler import LogHandler
from repo import DTLRepo
from dotenv import load_dotenv
load_dotenv()

REPO_URL = os.getenv("REPO_URL",
                     default="https://github.com/netbox-community/devicetype-library.git")
REPO_BRANCH = os.getenv("REPO_BRANCH", default="master")
NETBOX_URL = os.getenv("NETBOX_URL")
NETBOX_TOKEN = os.getenv("NETBOX_TOKEN")
IGNORE_SSL_ERRORS = (os.getenv("IGNORE_SSL_ERRORS", default="False") == "True")
REPO_PATH = f"{os.path.dirname(os.path.realpath(__file__))}/repo"

# optionally load vendors through a comma separated list as env var
VENDORS = list(filter(None, os.getenv("VENDORS", "").split(",")))

# optionally load device types through a space separated list as env var
SLUGS = os.getenv("SLUGS", "").split()

NETBOX_FEATURES = {
    'modules': False,
}

parser = ArgumentParser(description='Import Netbox Device Types')
parser.add_argument('--vendors', nargs='+', default=VENDORS,
                    help="List of vendors to import eg. apc cisco")
parser.add_argument('--url', '--git', default=REPO_URL,
                    help="Git URL with valid Device Type YAML files")
parser.add_argument('--slugs', nargs='+', default=SLUGS,
                    help="List of device-type slugs to import eg. ap4431 ws-c3850-24t-l")
parser.add_argument('--branch', default=REPO_BRANCH,
                    help="Git branch to use from repo")
parser.add_argument('--verbose', action='store_true', default=False,
                    help="Print verbose output")

args = parser.parse_args()

args.vendors = [v.lower() for vendor in args.vendors for v in vendor.split(",") if v.strip()]
args.slugs = [s for slug in args.slugs for s in slug.split(",") if s.strip()]

handle = LogHandler(args)
# Evaluate environment variables and exit if one of the mandatory ones are not set
MANDATORY_ENV_VARS = ["REPO_URL", "NETBOX_URL", "NETBOX_TOKEN"]
for var in MANDATORY_ENV_VARS:
    if var not in os.environ:
        handle.exception("EnvironmentError", var, f'Environment variable "{var}" is not set.\n\nMANDATORY_ENV_VARS: {str(MANDATORY_ENV_VARS)}.\n\nCURRENT_ENV_VARS: {str(os.environ)}')

dtl_repo = DTLRepo(args, REPO_PATH, handle)
