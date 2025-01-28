
import hashlib
import random
import string
from django.db import IntegrityError
from django.forms import ValidationError
from django.test import TestCase, override_settings

from django.core.exceptions import PermissionDenied
from django.core.management import call_command

from django.core.management.base import CommandError

from mdb.models.machine import Machine
from mdb.models.mgroup import MachineGroup
from mdb.admin import ReadOnlyAdmin
from mdb.models.room import Room

def override_init ():
    return override_settings( GATEWAY_PRODUCTION = False )
def override_production ():
    return override_settings( GATEWAY_PRODUCTION = True )

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

class RoomProtectionTestCase(TestCase):
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
    @override_production()
    def test_room_admin_protection (self):
        admin = ReadOnlyAdmin( Room, None )

        assert not admin.has_add_permission( None )
        assert not admin.has_change_permission( None )
        assert not admin.has_delete_permission( None )

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

class MachineGroupTestCase (TestCase):
    def setUp(self):
        with override_init():
            self.group1 = MachineGroup.objects.create( name = "group1" )
            self.group2 = MachineGroup.objects.create( name = "group2" )
    
    def test_room_str (self):
        assert str (self.group1) == "<Machine Group 'group1'>"
        assert str (self.group2) == "<Machine Group 'group2'>"
        assert repr(self.group1) == "<Machine Group 'group1'>"
        assert repr(self.group2) == "<Machine Group 'group2'>"

class MachineGroupProtectionTestCase(TestCase):
    def setUp(self):
        with override_init():
            self.group1 = MachineGroup.objects.create( name = "group1" )
            self.group2 = MachineGroup.objects.create( name = "group2" )
    
    @override_production()
    def test_room_save_in_production (self):
        with self.assertRaisesMessage(
            PermissionDenied,
            "Modifications to machine groups are not allowed in production"
        ):
            self.group2.name = "room3"
            self.group2.save()
        
        assert MachineGroup.objects.count() == 2
        assert list(map(lambda room: room.name, list( MachineGroup.objects.all() ) )) == [ "group1", "group2" ]
    @override_production()
    def test_room_delete_in_production (self):
        with self.assertRaisesMessage(
            PermissionDenied,
            "Deleting machine groups is not allowed in production"
        ):
            self.group2.delete()
        
        assert MachineGroup.objects.count() == 2
        assert list(map(lambda room: room.name, list( MachineGroup.objects.all() ) )) == [ "group1", "group2" ]
    @override_init()
    def test_room_save_in_init (self):
        self.group2.name = "group3"
        self.group2.save()
        
        assert MachineGroup.objects.count() == 2
        assert list(map(lambda room: room.name, list( MachineGroup.objects.all() ) )) == [ "group1", "group3" ]
    @override_init()
    def test_room_delete_in_init (self):
        self.group2.delete()
        
        assert MachineGroup.objects.count() == 1
        assert list(map(lambda room: room.name, list( MachineGroup.objects.all() ) )) == [ "group1" ]
    @override_production()
    def test_room_admin_protection (self):
        admin = ReadOnlyAdmin( MachineGroup, None )

        assert not admin.has_add_permission( None )
        assert not admin.has_change_permission( None )
        assert not admin.has_delete_permission( None )

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

class MachineProtectionTestCase (TestCase):
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
    def test_machine_secret (self):
        random.seed(42)

        host = "host0"

        L = [ random.choice(string.ascii_letters) for _ in range(16) ]

        vs = bytes( host + "".join(L), encoding="utf-8" )
        sec = hashlib.sha256( vs ).hexdigest()

        assert self.mac1.secret == sec
    @override_production()
    def test_machine_save_protection (self):
        with self.assertRaisesMessage(
            PermissionDenied,
            "Modifying machines is not allowed in production"
        ):
            self.mac1.host = "newhost0"
            self.mac1.save()
        assert Machine.objects.count() == 1
        assert Machine.objects.filter( host = "host0" ).count() == 1
    @override_production()
    def test_machine_delete_protection (self):
        with self.assertRaisesMessage(
            PermissionDenied,
            "Deleting machines is not allowed in production"
        ):
            self.mac1.delete()
        assert Machine.objects.count() == 1
        assert Machine.objects.filter( host = "host0" ).count() == 1
    @override_init()
    def test_machine_save (self):
        self.mac1.host = "newhost0"
        self.mac1.save()
        assert Machine.objects.count() == 1
        assert Machine.objects.filter( host = "newhost0" ).count() == 1
    @override_init()
    def test_machine_delete (self):
        self.mac1.delete()
        assert Machine.objects.count() == 0
    @override_init()
    def test_machine_wrong_mac (self):
        with self.assertRaisesMessage(
            ValidationError,
            "{'mac': ['Enter valid MAC Address']}"
        ):
            Machine.objects.create(
                host = "host",
                mac  = "ffff:ff:ff:ff:ff",

                room  = self.room1,
                group = self.group1
            )
    @override_init()
    def test_machine_wrong_secret (self):
        with self.assertRaisesMessage(
            ValidationError,
            "{'secret': ['Invalid Secret']}"
        ):
            self.mac1.secret = "secret"
            self.mac1.save()
    @override_init()
    def test_machine_non_unique (self):
        with self.assertRaisesMessage(ValidationError, "{'host': ['Machine with this Host Name already exists.']}"):
            Machine.objects.create( host = "host0", mac = "ff:ff:ff:ff:ff:fa", room = self.room1, group = self.group1 )
        with self.assertRaisesMessage(ValidationError, "{'mac': ['Machine with this MAC Address already exists.']}"):
            Machine.objects.create( host = "host1", mac = "ff:ff:ff:ff:ff:ff", room = self.room1, group = self.group1 )
