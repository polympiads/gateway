from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError

from dhcp.models.ipset import IpSet
from gateway.tests.utils import override_production


class DelIpSetTestCase(TestCase):
    def setUp(self):
        IpSet.objects.create(ipv4_base = "12.12.12.0", submask="255.255.255.0")
    
    @override_production()
    def test_del_ip_set_does_not_work_in_production(self):
        with self.assertRaises(CommandError):
            call_command("delipset", "12.12.12.0", "255.255.255.0")

    def test_del_ip_with_shorthand_works(self):
        call_command("delipset", "12.12.12.0/24")

        assert len(IpSet.objects.all()) == 0

    def test_del_ip_with_ip_base_only_works(self):
        call_command("delipset", "12.12.12.0")

        assert len(IpSet.objects.all()) == 0

    def test_del_ipsetwith_no_existant_ip_base_does_not_work(self):
        with self.assertRaises(CommandError):
            call_command("delipset", "12.13.12.0")

    def test_del_ipset_with_invalid_params(self):
        with self.assertRaises(CommandError):
            call_command("delipset", "skibidi")

        with self.assertRaises(CommandError):
            call_command("delipset", "skibidi/skibidi")

        with self.assertRaises(CommandError):
            call_command("delipset", "12.14.12/skibidi")

    