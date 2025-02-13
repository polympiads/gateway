from django.db import models

from dhcp.models.ipset import IpSet
from mdb.models.room import Room

class RoomIpSetBinding(models.Model):
    room = models.OneToOneField(Room, on_delete=models.PROTECT)
    ipset = models.ForeignKey(IpSet, on_delete=models.PROTECT)

