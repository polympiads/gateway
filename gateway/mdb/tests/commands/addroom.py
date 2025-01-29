
from django.test import TestCase
from django.core.management.base import CommandError
from django.core.management import call_command

from gateway.tests import override_init, override_production
from mdb.models.room import Room

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
