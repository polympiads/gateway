
from django.test import TestCase
from django.core.management.base import CommandError
from django.core.management import call_command

from gateway.tests.utils import check_telemetry, get_test_span_exporter, override_init, override_production, using_telemetry
from mdb.models.mgroup import MachineGroup
from opentelemetry import trace

class DelMachineGroupCommandTestCase (TestCase):
    def setUp(self):
        with override_init():
            self.group1 = MachineGroup.objects.create( name = "group1" )
            self.group2 = MachineGroup.objects.create( name = "group2" )
    @override_production()
    def test_production_delgroup_command (self):
        with self.assertRaisesMessage(
            CommandError,
            "Cannot delete a machine group in production mode"
        ):
            call_command( "delmgroup", "group1" )
        assert MachineGroup.objects.count() == 2
        assert list(map(lambda room: room.name, list( MachineGroup.objects.all() ) )) == [ "group1", "group2" ]
    @override_init()
    def test_init_delgroup_command (self):
        call_command( "delmgroup", "group1" )
        assert MachineGroup.objects.count() == 1
        assert list(map(lambda room: room.name, list( MachineGroup.objects.all() ) )) == [ "group2" ]
    @override_init()
    def test_init_delgroup_does_not_exist_command (self):
        with self.assertRaisesMessage(
            CommandError,
            "This machine group does not exist"
        ):
            call_command( "delmgroup", "group3" )

    @using_telemetry
    @override_init()
    def test_init_delgroup_telemetry (self):
        call_command( "delmgroup", "group1" )
        
        check_telemetry((
            "Handle delmgroup", { 'group.name' : 'group1' },
            [  ],
            trace.StatusCode.UNSET, False
        ))
    @using_telemetry
    @override_production()
    def test_prod_delgroup_telemetry (self):
        with self.assertRaisesMessage(
            CommandError,
            "Cannot delete a machine group in production mode"
        ):
            call_command( "delmgroup", "group1" )
        
        check_telemetry((
            "Handle delmgroup", { 'group.name' : 'group1' },
            [ CommandError("Cannot delete a machine group in production mode") ],
            trace.StatusCode.ERROR, False
        ))
    @using_telemetry
    @override_init()
    def test_init_delgroup_does_not_exists_telemetry (self):
        with self.assertRaisesMessage(
            CommandError,
            "This machine group does not exist"
        ):
            call_command( "delmgroup", "group3" )
        
        check_telemetry((
            "Handle delmgroup", { 'group.name' : 'group3' },
            [ CommandError("This machine group does not exist") ],
            trace.StatusCode.ERROR, False
        ))