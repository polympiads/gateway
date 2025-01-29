
from django.test import TestCase
from django.core.management.base import CommandError
from django.core.management import call_command

from gateway.tests import override_init, override_production
from mdb.models.mgroup import MachineGroup

class AddMachineGroupCommandTestCase (TestCase):
    @override_production()
    def test_production_addmgroup_command (self):
        with self.assertRaisesMessage(
            CommandError,
            "Cannot create a machine group in production mode"
        ):
            call_command( "addmgroup", "group1" )
    @override_init()
    def test_init_addmgroup_command (self):
        call_command( "addmgroup", "group1" )
        assert MachineGroup.objects.count() == 1
        assert list(map(lambda room: room.name, list( MachineGroup.objects.all() ) )) == [ "group1" ]
        call_command( "addmgroup", "group2" )
        assert MachineGroup.objects.count() == 2
        assert list(map(lambda room: room.name, list( MachineGroup.objects.all() ) )) == [ "group1", "group2" ]
    @override_init()
    def test_init_addmgroup_non_unique (self):
        call_command( "addmgroup", "room1" )
        with self.assertRaisesMessage(
            CommandError,
            "A machine group with this name already exists"
        ):
            call_command( "addmgroup", "room1" )
