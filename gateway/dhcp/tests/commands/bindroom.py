from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError

from dhcp.models import IpSet, RoomIpSetBinding
from mdb.models.room import Room
from gateway.tests.utils import override_production


class BindRoomTestCase(TestCase):
    def setUp(self):
        self.room1 = Room.objects.create(name='room1')
        self.room2 = Room.objects.create(name='room2')

        self.ipset = IpSet.objects.create(ipv4_base='12.12.12.0', submask='255.255.255.0')
    
    @override_production()
    def test_bindroom_does_not_work_in_production(self):
        with self.assertRaises(CommandError):
            call_command("bindroom", "room1", "12.12.12.0")

    def test_bindroom_works(self):
        call_command("bindroom", "room1", "12.12.12.0")

        assert len(RoomIpSetBinding.objects.all()) == 1

    def test_multiple_rooms_can_be_bound_to_same_ipset(self):
        call_command("bindroom", "room1", "12.12.12.0")
        call_command("bindroom", "room2", "12.12.12.0")

        assert len(RoomIpSetBinding.objects.all()) == 2

    def test_room_cannot_be_bound_twice(self):
        call_command("bindroom", "room1", "12.12.12.0")

        with self.assertRaises(CommandError):
            call_command("bindroom", "room1", "12.12.12.0")

    def test_cannot_bind_room_which_does_not_exists(self):
        with self.assertRaises(CommandError):
            call_command("bindroom", "skibidi", "12.12.12.0")

    def test_cannot_bind_room_with_an_ipset_which_does_not_exists(self):
        with self.assertRaises(CommandError):
            call_command("bindroom", "room1", "64.64.64.0")

    def test_bindroom_with_invalid_params(self):
        with self.assertRaises(CommandError):
            call_command("bindroom", "room1", "skibidi")
