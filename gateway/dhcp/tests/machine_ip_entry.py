import random
from django.test import TestCase

from dhcp.models.ipset import IpSet
from dhcp.models.machine_ip_entry import MachineIpEntry, MachineRegisterError
from mdb.models.machine import Machine
from mdb.models.mgroup import MachineGroup
from mdb.models.room import Room


class MachineIpEntryTestCase(TestCase):
    def setUp(self):
        random.seed(42)
            
        self.room1 = Room.objects.create( name = "room1" )
        self.room2 = Room.objects.create( name = "room2" )

        self.group1 = MachineGroup.objects.create( name = "group1" )
        self.group2 = MachineGroup.objects.create( name = "group2" )

        self.mac1 = Machine.objects.create(
            host = "host0",
            mac  = "ff:ff:ff:ff:ff:ff",

            room  = self.room1,
            group = self.group1
        )

        self.ipset = IpSet.objects.create(ipv4_base = '192.168.0.0', submask="255.255.255.252", name = 'room ipset')
        self.ipset2 = IpSet.objects.create(ipv4_base = '192.167.0.0', submask="255.255.255.252", name = 'room ipset')

    def test_machine_register_works(self):
        MachineIpEntry.objects.all().delete()

        machine = MachineIpEntry.register(self.mac1, self.ipset)

        assert MachineIpEntry.objects.contains(machine)

    def test_associate_machine_to_more_than_one_entry_does_not_work(self):
        MachineIpEntry.objects.all().delete()

        MachineIpEntry.register(self.mac1, self.ipset)

        with self.assertRaises(MachineRegisterError):
            MachineIpEntry.register(self.mac1, self.ipset)

        with self.assertRaises(MachineRegisterError):
            MachineIpEntry.register(self.mac1, self.ipset2)
