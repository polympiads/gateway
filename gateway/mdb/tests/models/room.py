
from django.test import TestCase

from mdb.models.room import Room
from gateway.tests.utils import override_init


class RoomTestCase (TestCase):
    def setUp(self):
        with override_init():
            self.room1 = Room.objects.create( name = "room1" )
            self.room2 = Room.objects.create( name = "room2" )
    
    def test_room_str (self):
        assert str (self.room1) == "<Room 'room1'>"
        assert str (self.room2) == "<Room 'room2'>"
        assert repr(self.room1) == "<Room 'room1'>"
        assert repr(self.room2) == "<Room 'room2'>"
