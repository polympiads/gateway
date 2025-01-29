
from django.test import TestCase
from django.core.management.base import CommandError
from django.core.management import call_command

from gateway.tests import override_init, override_production
from mdb.models.room import Room

class DelRoomCommandTestCase (TestCase):
    def setUp(self):
        with override_init():
            self.room1 = Room.objects.create( name = "room1" )
            self.room2 = Room.objects.create( name = "room2" )
    @override_production()
    def test_production_delroom_command (self):
        with self.assertRaisesMessage(
            CommandError,
            "Cannot delete a room in production mode"
        ):
            call_command( "delroom", "room1" )
        assert Room.objects.count() == 2
        assert list(map(lambda room: room.name, list( Room.objects.all() ) )) == [ "room1", "room2" ]
    @override_init()
    def test_init_delroom_command (self):
        call_command( "delroom", "room1" )
        assert Room.objects.count() == 1
        assert list(map(lambda room: room.name, list( Room.objects.all() ) )) == [ "room2" ]
    @override_init()
    def test_init_delroom_does_not_exist_command (self):
        with self.assertRaisesMessage(
            CommandError,
            "This room does not exist"
        ):
            call_command( "delroom", "room3" )
