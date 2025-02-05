
from django.test import TestCase
from gateway.tests.utils import override_init, override_production
from mdb.models.room import Room

from django.core.exceptions import PermissionDenied

class RoomRulesTestCase(TestCase):
    def setUp(self):
        with override_init():
            self.room1 = Room.objects.create( name = "room1" )
            self.room2 = Room.objects.create( name = "room2" )
    
    @override_production()
    def test_room_save_in_production (self):
        with self.assertRaisesMessage(
            PermissionDenied,
            "Modifications to rooms are not allowed in production"
        ):
            self.room2.name = "room3"
            self.room2.save()
        
        assert Room.objects.count() == 2
        assert list(map(lambda room: room.name, list( Room.objects.all() ) )) == [ "room1", "room2" ]
    @override_production()
    def test_room_delete_in_production (self):
        with self.assertRaisesMessage(
            PermissionDenied,
            "Deleting rooms is not allowed in production"
        ):
            self.room2.delete()
        
        assert Room.objects.count() == 2
        assert list(map(lambda room: room.name, list( Room.objects.all() ) )) == [ "room1", "room2" ]
    @override_init()
    def test_room_save_in_init (self):
        self.room2.name = "room3"
        self.room2.save()
        
        assert Room.objects.count() == 2
        assert list(map(lambda room: room.name, list( Room.objects.all() ) )) == [ "room1", "room3" ]
    @override_init()
    def test_room_delete_in_init (self):
        self.room2.delete()
        
        assert Room.objects.count() == 1
        assert list(map(lambda room: room.name, list( Room.objects.all() ) )) == [ "room1" ]
