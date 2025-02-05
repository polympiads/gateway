
import random
from django.test import TestCase

from gateway.tests.utils import override_init
from mdb.models.machine import Machine
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
