
from django.test import TestCase
from django.core.management.base import CommandError
from django.core.management import call_command

from gateway.tests.utils import check_telemetry, get_test_span_exporter, override_init, override_production, using_telemetry
from mdb.models.room import Room
from opentelemetry import trace

import time

class AddRoomCommandTestCase (TestCase):
    @override_production()
    def test_production_addroom_command (self):
        with self.assertRaisesMessage(
            CommandError,
            "Cannot create a room in production mode"
        ):
            call_command( "addroom", "room1" )
    @override_init()
    def test_init_addroom_command (self):
        call_command( "addroom", "room1" )
        assert Room.objects.count() == 1
        assert list(map(lambda room: room.name, list( Room.objects.all() ) )) == [ "room1" ]
        call_command( "addroom", "room2" )
        assert Room.objects.count() == 2
        assert list(map(lambda room: room.name, list( Room.objects.all() ) )) == [ "room1", "room2" ]
    @override_init()
    def test_init_addroom_non_unique (self):
        call_command( "addroom", "room1" )
        with self.assertRaisesMessage(
            CommandError,
            "A room with this name already exists"
        ):
            call_command( "addroom", "room1" )

    @using_telemetry
    @override_init()
    def test_init_addroom_telemetry (self):
        call_command( "addroom", "room1" )
        check_telemetry((
            "Handle addroom", { 'room.name' : 'room1' },
            [  ],
            trace.StatusCode.UNSET, False
        ))
    @using_telemetry
    @override_production()
    def test_prod_addroom_telemetry (self):
        with self.assertRaisesMessage(
            CommandError,
            "Cannot create a room in production mode"
        ):
            call_command( "addroom", "room1" )
        check_telemetry((
            "Handle addroom", { 'room.name' : 'room1' },
            [ CommandError("Cannot create a room in production mode") ],
            trace.StatusCode.ERROR, False
        ))
    @using_telemetry
    @override_init()
    def test_init_addroom_non_unique_telemetry (self):
        call_command( "addroom", "room1" )
        with self.assertRaisesMessage(
            CommandError,
            "A room with this name already exists"
        ):
            call_command( "addroom", "room1" )

        check_telemetry((
            "Handle addroom", { 'room.name' : 'room1' },
            [  ],
            trace.StatusCode.UNSET, False
        ), (
            "Handle addroom", { 'room.name' : 'room1' },
            [ CommandError("A room with this name already exists") ],
            trace.StatusCode.ERROR, False
        ))
