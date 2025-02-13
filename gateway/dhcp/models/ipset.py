from django.db import models
from django.core.exceptions import ValidationError

from ..utils import ip2int, int2ip

class IpSetFullException(Exception):
    def __init__(self):
        super().__init__("The ip set is full.")


class IpSet(models.Model):
    ipv4_base = models.GenericIPAddressField(verbose_name='ipv4 base', protocol='IPv4', unique=True)
    submask = models.GenericIPAddressField(verbose_name='submask', protocol='IPv4')
    name = models.TextField(verbose_name='ip_set name', default='<ip_set>')

    def clean(self):
        ipv4_raw = ip2int(self.ipv4_base)
        if (ipv4_raw & ip2int(self.submask)) != ipv4_raw:
            raise ValidationError('assertion error : ip & submask != ip')
        
        conflicting_ipset = [ipset for ipset in IpSet.objects.all() if ip2int(ipset.ipv4_base) & ip2int(self.submask) == ip2int(self.ipv4_base) & ip2int(ipset.submask)]
        if len(conflicting_ipset) > 0:
            raise ValidationError(f'{conflicting_ipset}')
        
    def save(self, *args, **kwargs):
        self.full_clean()

        return super().save(*args, **kwargs)

    def get_new_ip(self, already_registered_ips: list[str]) -> str:
        baseip  = ip2int(self.ipv4_base)
        submask = ip2int(self.submask)
        invmask = (2 ** 32 - 1 - submask)

        baseip = baseip & submask

        curmask = (invmask - 1) & invmask
        while True:
            # guess is a potential result that "might work"
            guess_raw = curmask + baseip
            guess = int2ip(curmask + baseip)
            if guess not in already_registered_ips and (guess_raw & 0xFF) != 0xFF:
                return guess
            
            if curmask == 0:
                break
            curmask = (curmask - 1) & invmask

        raise IpSetFullException()
    
    def __str__(self):
        return f"{self.ipv4_base} [{self.submask}]"