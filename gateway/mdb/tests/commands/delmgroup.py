
from django.test import TestCase
from django.core.management.base import CommandError
from django.core.management import call_command

from gateway.tests import override_init, override_production
from mdb.models.mgroup import MachineGroup

class DelMachineGroupCommandTestCase (TestCase):
    def setUp(self):
        with override_init():
            self.group1 = MachineGroup.objects.create( name = "group1" )
            self.group2 = MachineGroup.objects.create( name = "group2" )
    @override_production()
    def test_production_delroom_command (self):
        with self.assertRaisesMessage(
            CommandError,
            "Cannot delete a machine group in production mode"
        ):
            call_command( "delmgroup", "group1" )
        assert MachineGroup.objects.count() == 2
        assert list(map(lambda room: room.name, list( MachineGroup.objects.all() ) )) == [ "group1", "group2" ]
    @override_init()
    def test_init_delroom_command (self):
        call_command( "delmgroup", "group1" )
        assert MachineGroup.objects.count() == 1
        assert list(map(lambda room: room.name, list( MachineGroup.objects.all() ) )) == [ "group2" ]
    @override_init()
    def test_init_delroom_does_not_exist_command (self):
        with self.assertRaisesMessage(
            CommandError,
            "This machine group does not exist"
        ):
            call_command( "delmgroup", "group3" )
