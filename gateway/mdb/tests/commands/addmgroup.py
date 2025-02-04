
from django.test import TestCase
from django.core.management.base import CommandError
from django.core.management import call_command

from gateway.tests import check_telemetry, get_test_span_exporter, override_init, override_production, using_telemetry
from mdb.models.mgroup import MachineGroup

from opentelemetry import trace

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
        assert list(map(lambda mgroup: mgroup.name, list( MachineGroup.objects.all() ) )) == [ "group1" ]
        call_command( "addmgroup", "group2" )
        assert MachineGroup.objects.count() == 2
        assert list(map(lambda mgroup: mgroup.name, list( MachineGroup.objects.all() ) )) == [ "group1", "group2" ]
    @override_init()
    def test_init_addmgroup_non_unique (self):
        call_command( "addmgroup", "room1" )
        with self.assertRaisesMessage(
            CommandError,
            "A machine group with this name already exists"
        ):
            call_command( "addmgroup", "room1" )

    @using_telemetry
    @override_init()
    def test_init_addmgroup_telemetry (self):
        call_command( "addmgroup", "room1" )

        check_telemetry((
            "Handle addmgroup", { 'group.name' : 'room1' },
            [  ],
            trace.StatusCode.UNSET, False
        ))

    @using_telemetry
    @override_production()
    def test_prod_addmgroup_telemetry (self):
        with self.assertRaisesMessage(
            CommandError,
            "Cannot create a machine group in production mode"
        ):
            call_command( "addmgroup", "room1" )

        check_telemetry((
            "Handle addmgroup", { 'group.name' : 'room1' },
            [ CommandError("Cannot create a machine group in production mode") ],
            trace.StatusCode.ERROR, False
        ))

    @using_telemetry
    @override_init()
    def test_init_addmgroup_non_unique_telemetry (self):
        call_command( "addmgroup", "room1" )
        with self.assertRaisesMessage(
            CommandError,
            "A machine group with this name already exists"
        ):
            call_command( "addmgroup", "room1" )
        
        check_telemetry((
            "Handle addmgroup", { 'group.name' : 'room1' },
            [  ],
            trace.StatusCode.UNSET, False
        ), (
            "Handle addmgroup", { 'group.name' : 'room1' },
            [ CommandError("A machine group with this name already exists") ],
            trace.StatusCode.ERROR, False
        ))
