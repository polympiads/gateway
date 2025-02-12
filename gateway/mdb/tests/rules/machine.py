
from django.forms import ValidationError
from django.test import TestCase
from gateway.tests.utils import override_init, override_production
from mdb.models import Room, MachineGroup, Machine

from django.core.exceptions import PermissionDenied

import random
import string
import hashlib

class MachineRulesTestCase (TestCase):
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

        self.mac1.allocate_secret()
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
