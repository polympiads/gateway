from enum import StrEnum
from typing import Self

from django.db import models

from mdb.models import Machine
from .ipset import Ip, IpSet

class MachineRegisterErrorKind(StrEnum):
    ALREADY_REGISTERED = "The machine has already been registered."

class MachineRegisterError(Exception):
    def __init__(self, kind: MachineRegisterErrorKind):
        super().__init__(str(kind))

class MachineIpEntry(models.Model):
    ip = models.OneToOneField(Ip, on_delete=models.PROTECT)
    machine = models.OneToOneField(Machine, on_delete=models.CASCADE, primary_key=True, unique=True)
    ip_set = models.ForeignKey(IpSet, on_delete=models.PROTECT)

    @classmethod
    def register(cls, machine: Machine, ip_set: IpSet) -> Self:
        if MachineIpEntry.objects.filter(machine=machine).exists():
            raise MachineRegisterError(MachineRegisterErrorKind.ALREADY_REGISTERED)

        ip = ip_set.get_new_ip()
        out = cls.objects.create(ip=ip, machine=machine, ip_set=ip_set)

        from dhcp import dnsmasq
        dnsmasq.update_dnsmasq_config_file()

        return out
    
    def delete(self):
        super().delete()

        self.ip.delete()

        from dhcp import dnsmasq
        dnsmasq.update_dnsmasq_config_file()