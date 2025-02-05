
from django.test import TestCase
from gateway.tests.utils import override_init, override_production
from mdb.models.mgroup import MachineGroup

from django.core.exceptions import PermissionDenied

class MachineGroupRulesTestCase(TestCase):
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
