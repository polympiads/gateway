from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError

from dhcp.models.ipset import IpSet
from gateway.tests.utils import override_production


class AddIpSetTestCase(TestCase):
    def setUp(self):
        IpSet.objects.all().delete()
    
    @override_production()
    def test_add_ip_set_does_not_work_in_production(self):
        with self.assertRaises(CommandError):
            call_command("addipset", "12.13.12.0", "255.255.255.0")


    def test_addipset_works(self):
        call_command("addipset", "12.13.12.0", "255.255.255.0")

        assert len(IpSet.objects.all()) == 1

    def test_addipset_shorthand_works(self):
        call_command("addipset", "12.13.12.0/24")

        assert len(IpSet.objects.all()) == 1

    def test_add_same_ipset_does_not_works_twice(self):
        call_command("addipset", "12.13.12.0", "255.255.255.0")

        with self.assertRaises(CommandError):
            call_command("addipset", "12.13.12.0", "255.255.255.0")

    def test_add_ipset_which_intersect_does_not_work(self):
        call_command("addipset", "12.13.12.0", "255.255.255.0")

        with self.assertRaises(CommandError):
            call_command("addipset", "12.13.0.0", "255.255.0.0")

    def test_add_ipset_with_invalid_params(self):
        with self.assertRaises(CommandError):
            call_command("addipset", "skibidi", "255.255.255.0")

        with self.assertRaises(CommandError):
            call_command("addipset", "12.13.12.13", "255.255.255.0")

        with self.assertRaises(CommandError):
            call_command("addipset", "12.13.12.0", "skibidi")

        with self.assertRaises(CommandError):
            call_command("addipset", "12.13.12.0/skibidi")

        with self.assertRaises(CommandError):
            call_command("addipset", "12.13.12.0/triple/skibidi")

        with self.assertRaises(CommandError):
            call_command("addipset", "12.13.12.0/64")

    def test_add_ipset_require_submask(self):
        with self.assertRaises(CommandError):
            call_command("addipset", "12.13.12.0")

    