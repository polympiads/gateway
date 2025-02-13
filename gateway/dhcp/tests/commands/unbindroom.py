from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError

from dhcp.models import IpSet, RoomIpSetBinding
from mdb.models.room import Room
from gateway.tests.utils import override_production


class UnbindRoomTestCase(TestCase):
    def setUp(self):
        self.room1 = Room.objects.create(name='room1')
        self.room2 = Room.objects.create(name='room2')

        self.ipset = IpSet.objects.create(ipv4_base='12.12.12.0', submask='255.255.255.0')

        self.binding = RoomIpSetBinding(room=self.room1, ipset=self.ipset)
    
    @override_production()
    def test_unbindroom_does_not_work_in_production(self):
        with self.assertRaises(CommandError):
            call_command("unbindroom", "room1")

    def test_unbindroom_works(self):
        call_command("unbindroom", "room1")

        assert len(RoomIpSetBinding.objects.all()) == 0

    def test_room_cannot_be_unbound_twice(self):
        call_command("bindroom", "room1")

        with self.assertRaises(CommandError):
            call_command("bindroom", "room1")

    def test_cannot_unbind_room_which_does_not_exists(self):
        with self.assertRaises(CommandError):
            call_command("bindroom", "skibidi")
