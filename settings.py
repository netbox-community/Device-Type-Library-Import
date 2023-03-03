from argparse import ArgumentParser
from sys import exit as system_exit
import os

from dotenv import load_dotenv
load_dotenv()


def handle_exception(exception_type, exception, stack_trace=None):
    exception_dict = {
        "EnvironmentError": f'Environment variable "{exception}" is not set.',
        "SSLError": f'SSL verification failed. IGNORE_SSL_ERRORS is {exception}. EXITING.',
        "GitCommandError": f'The repo "{exception}" is not a valid git repo.',
        "GitInvalidRepositoryError": f'The repo "{exception}" is not a valid git repo.',
        "Exception": f'An unknown error occurred: "{exception}"'
    }
    if args.verbose and stack_trace:
        print(stack_trace)
    print(exception_dict[exception_type])
    system_exit(1)


REPO_URL = os.getenv("REPO_URL",
                     default="https://github.com/netbox-community/devicetype-library.git")
REPO_BRANCH = os.getenv("REPO_BRANCH", default="master")
NETBOX_URL = os.getenv("NETBOX_URL")
NETBOX_TOKEN = os.getenv("NETBOX_TOKEN")
IGNORE_SSL_ERRORS = (os.getenv("IGNORE_SSL_ERRORS", default="False") == "True")
REPO_PATH = "./repo"

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
parser.add_argument('--verbose', action='store_true',
                    help="Print verbose output")

args = parser.parse_args()

# Evaluate environment variables and exit if one of the mandatory ones are not set
MANDATORY_ENV_VARS = ["REPO_URL", "NETBOX_URL", "NETBOX_TOKEN"]
for var in MANDATORY_ENV_VARS:
    if var not in os.environ:
        handle_exception("EnvironmentError", var, f'Environment variable "{var}" is not set.\n\nMANDATORY_ENV_VARS: {str(MANDATORY_ENV_VARS)}.\n\nCURRENT_ENV_VARS: {str(os.environ)}')
