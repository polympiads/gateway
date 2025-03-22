from typing import IO

from gateway.settings.base import DHCP_CONFIG_LEASE_DURATION, DHCP_CONFIG_PATH
from .models.machine_ip_entry import MachineIpEntry

class DnsmasqConfigFile:
    def __init__(self, file: IO):
        assert file is not None

        self._file = file

    def update_dnsmasq_config_file(self):
        # apparently truncating doesn't move the cursor of StringIO objects back to zero...
        self._file.truncate(0)
        self._file.seek(0)

        for entry in MachineIpEntry.objects.all():
            mac = entry.machine.mac
            ip = entry.ip.as_str()

            self._file.write(f"dhcp-host={mac},{ip},{DHCP_CONFIG_LEASE_DURATION}m")


__default_config = None
if DHCP_CONFIG_PATH:
    __default_config = DnsmasqConfigFile(open(DHCP_CONFIG_PATH, 'w')) # pragma: no cover

def update_dnsmasq_config_file():
    
    if __default_config: # pragma: no cover
        __default_config.update_dnsmasq_config_file()
