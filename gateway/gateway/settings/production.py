import os
from .base import *  # noqa: F403

GATEWAY_PRODUCTION = True

SECRET_KEY = os.getenv( 'GATEWAY_SECRET_KEY', 'django-missing' )
DHCP_CONFIG_PATH = os.getenv('DCHP_CONFIG_PATH')

class SecretKeyNotProvidedException(Exception):
    def __init__(self):
        super().__init__("No secrets keys were given.")

if SECRET_KEY == 'django-missing':
    raise SecretKeyNotProvidedException()


class DchpConfigPathNotGiven(Exception):
    def __init__(self):
        super().__init__("No dchp config paths were given.")
class DangerousDchpConfigPath(Exception):
    def __init__(self):
        super().__init__("The path /etc/dnsmasq.conf is dangerous and should not be writen to directly. Write to another file, and reference it in the main config file instead.")

if not DHCP_CONFIG_PATH:
    raise DchpConfigPathNotGiven()
elif DHCP_CONFIG_PATH == "/etc/dnsmasq.conf":
    raise DangerousDchpConfigPath()
