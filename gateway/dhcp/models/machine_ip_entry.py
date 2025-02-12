from enum import StrEnum
from typing import Self

from django.db import models

from mdb.models import Machine
from .ipset import IpSet

class MachineRegisterErrorKind(StrEnum):
    ALREADY_REGISTERED = "The machine has already been registered."

class MachineRegisterError(Exception):
    def __init__(self, kind: MachineRegisterErrorKind):
        super().__init__(str(kind))

class MachineIpEntry(models.Model):
    ip = models.GenericIPAddressField(verbose_name='ip', protocol='IPv4', unique=True)
    machine = models.OneToOneField(Machine, on_delete=models.PROTECT, primary_key=True, unique=True)
    ip_set = models.ForeignKey(IpSet, on_delete=models.PROTECT)

    @classmethod
    def register(cls, machine: Machine, ip_set: IpSet) -> Self:
        if MachineIpEntry.objects.filter(machine=machine).exists():
            raise MachineRegisterError(MachineRegisterErrorKind.ALREADY_REGISTERED)

        all_registered_ips = [entry.ip for entry in MachineIpEntry.objects.filter(ip_set=ip_set)]

        ip = ip_set.get_new_ip(all_registered_ips)

        return cls.objects.create(ip=ip, machine=machine, ip_set=ip_set)