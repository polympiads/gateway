from django.core.management.base import CommandError

from dhcp import utils

def parse_ip_set(ip_base_str: str, submask: str | None, require_submask: bool = True):
    try:
        parts = ip_base_str.split('/')
        if not 1 <= len(parts) <= 2:
            raise CommandError("Invalid ip base")

        ip_base = utils.ip2int(parts[0])
        if submask is not None:
            submask = utils.ip2int(submask)
        elif len(parts) == 2:
            try:
                submask_len = int(parts[1])
            except ValueError:
                raise CommandError("Invalid sub_mask len")
            
            if submask_len > 32:
                raise CommandError("Invalid sub_mask len")

            submask = 2**32 - 2**(32 - submask_len)
        else:
            if require_submask:
                raise CommandError("Please provide the submask.")
            else:
                submask = None
            
    except OSError:
        raise CommandError("Error : ip_base and / or submask are invalid parameters")
    
    return ip_base, submask