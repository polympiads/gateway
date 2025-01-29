
from django.test import TestCase

from mdb.admin import ReadOnlyAdmin
from mdb.models import *

class AdminTestCase (TestCase):
    def test_room_admin (self):
        admin = ReadOnlyAdmin( Room, None )

        assert not admin.has_add_permission()
        assert not admin.has_change_permission()
        assert not admin.has_delete_permission()
    def test_mgroup_admin (self):
        admin = ReadOnlyAdmin( MachineGroup, None )

        assert not admin.has_add_permission()
        assert not admin.has_change_permission()
        assert not admin.has_delete_permission()
    def test_machine_admin (self):
        admin = ReadOnlyAdmin( Machine, None )

        assert not admin.has_add_permission()
        assert not admin.has_change_permission()
        assert not admin.has_delete_permission()
