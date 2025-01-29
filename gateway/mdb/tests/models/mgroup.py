
from django.test import TestCase
from gateway.tests import override_init
from mdb.models.mgroup import MachineGroup

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
