import random

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from gateway.tests import override_init
from mdb.models.machine import ConnectionStatus, Machine
from mdb.models.mgroup import MachineGroup
from mdb.models.room import Room


class MachineTestCase (TestCase):
    def setUp(self):
        with override_init ():
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
    def test_str (self):
        assert str(self.mac1) == "<Machine 'host0' at ff:ff:ff:ff:ff:ff in <Room 'room1'>, <Machine Group 'group1'>>"
        assert repr(self.mac1) == "<Machine 'host0' at ff:ff:ff:ff:ff:ff in <Room 'room1'>, <Machine Group 'group1'>>"

    def test_connection_status(self):
        assert self.mac1.netstat == ConnectionStatus.Connected
    
    def test_connection_status_unknown(self):
        self.mac1.last_ping = timezone.now() - settings.PING_INTERVAL - timezone.timedelta(minutes=2)

        assert self.mac1.netstat == ConnectionStatus.Unknown

    def test_connection_status_disconnected(self):
        self.mac1.last_ping = timezone.now() - 2 * settings.PING_INTERVAL - timezone.timedelta(minutes=2)

        assert self.mac1.netstat == ConnectionStatus.Disconnected

    def test_connection_status_only_accepts_datetime(self):
        with self.assertRaises(AssertionError):
            ConnectionStatus.from_time_elapsed(None)
