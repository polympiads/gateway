import random
from io import StringIO

from django.test import TestCase
from gateway.settings.base import DHCP_CONFIG_LEASE_DURATION
from mdb.models.machine import Machine
from mdb.models.mgroup import MachineGroup
from mdb.models.room import Room

from dhcp.dnsmasq import DnsmasqConfigFile
from dhcp.models.ipset import IpSet
from dhcp.models.machine_ip_entry import MachineIpEntry


class DnsmasqTestCase(TestCase):
    def setUp(self):
        self.file_io = StringIO()
        self.context = DnsmasqConfigFile(self.file_io)

        random.seed(42)
            
        self.room1 = Room.objects.create( name = "room1" )
        self.room2 = Room.objects.create( name = "room2" )

        self.group1 = MachineGroup.objects.create( name = "group1" )
        self.group2 = MachineGroup.objects.create( name = "group2" )

        self.mac1 = Machine.objects.create(
            host = "host1",
            mac  = "ff:ff:ff:ff:ff:ff",

            room  = self.room1,
            group = self.group1
        )
        self.mac2 = Machine.objects.create(
            host = "host2",
            mac  = "fa:fa:fa:fa:fa:fa",

            room  = self.room2,
            group = self.group1
        )

        self.ipset = IpSet.objects.create(ipv4_base = '192.168.0.0', submask="255.255.255.252", name = 'room ipset')
        self.ipset2 = IpSet.objects.create(ipv4_base = '192.167.0.0', submask="255.255.255.252", name = 'room ipset')

    def test_update_dnsmasq_works_when_no_machines_are_present(self):
        self.context.update_dnsmasq_config_file()
        self.assertEquals("", self.file_io.getvalue())


    def test_update_dnsmasq_works_with_one_machine(self):
        machine = MachineIpEntry.register(self.mac1, self.ipset)

        self.context.update_dnsmasq_config_file()

        expected = [f"dhcp-host={machine.machine.mac},{machine.ip.as_str()},{DHCP_CONFIG_LEASE_DURATION}m"]
        self.assertEquals(expected, self.file_io.getvalue().splitlines())

    
    def test_update_dnsmasq_works_with_multiple_machines(self):
        machine = MachineIpEntry.register(self.mac1, self.ipset)
        machine2 = MachineIpEntry.register(self.mac2, self.ipset)

        self.context.update_dnsmasq_config_file()

        expected = [
            f"dhcp-host={machine.machine.mac},{machine.ip.as_str()},{DHCP_CONFIG_LEASE_DURATION}m"
            f"dhcp-host={machine2.machine.mac},{machine2.ip.as_str()},{DHCP_CONFIG_LEASE_DURATION}m"
        ]
        self.assertEquals(expected, self.file_io.getvalue().splitlines())

    def test_update_dnsmasq_works_when_a_machine_is_unregistered(self):
        machine = MachineIpEntry.register(self.mac1, self.ipset)
        machine2 = MachineIpEntry.register(self.mac2, self.ipset)

        self.context.update_dnsmasq_config_file()
        machine2.delete()
        self.context.update_dnsmasq_config_file()

        expected = [
            f"dhcp-host={machine.machine.mac},{machine.ip.as_str()},{DHCP_CONFIG_LEASE_DURATION}m"
        ]
        self.assertEquals(expected, self.file_io.getvalue().splitlines())

    
