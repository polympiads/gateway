import random
from django.forms import ValidationError
from django.test import TestCase

from dhcp.models.ipset import IpSet, IpSetFullException
from mdb.models.machine import Machine
from mdb.models.mgroup import MachineGroup
from mdb.models.room import Room


class IpSetTestCase(TestCase):
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

    def test_ip_set_generate_correctly(self):
        expected = [
            "192.168.0.2",
            "192.168.0.1",
            "192.168.0.0",
        ]

        actual = []
        for _ in range(3):
            actual.append(self.ipset.get_new_ip(actual))

        self.assertEqual(expected, actual)

        with self.assertRaises(IpSetFullException):
            self.ipset.get_new_ip(actual)

    def test_create_ipset_with_not_good_settings_is_valid(self):
        with self.assertRaises(ValidationError):
            IpSet.objects.create(ipv4_base='128.153.13.1', submask='255.255.0.0', name='skibidi')

        instance = IpSet.objects.create(ipv4_base='128.153.0.0', submask='255.255.0.0', name='skibidi')
        instance.delete()

    def test_creating_ipset_with_intersections_does_not_work_same_ip(self):
        with self.assertRaises(ValidationError):
            IpSet.objects.create(ipv4_base = '192.168.0.2', submask="255.255.255.254", name = 'room ipset')

        with self.assertRaises(ValidationError):
            IpSet.objects.create(ipv4_base = '192.168.0.0', submask="255.255.0.0", name = 'room ipset')

        with self.assertRaises(ValidationError):
            IpSet.objects.create(ipv4_base = '192.0.0.0', submask="255.0.0.0", name = 'room ipset')