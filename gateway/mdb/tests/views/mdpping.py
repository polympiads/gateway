import random

from django.http import HttpResponseBadRequest
from django.test import TestCase, Client

from gateway.tests import override_init
from mdb.models.machine import ConnectionStatus, Machine
from mdb.models.mgroup import MachineGroup
from mdb.models.room import Room


class MDPPingTestCase(TestCase):
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

            self.client = Client()

    def test_mdb_ping_invalid_request_on_post(self):
        reponse = self.client.post("/api/v1/mdbping", { "secret": self.mac1.secret })
        assert reponse.status_code == HttpResponseBadRequest().status_code

    def test_mdb_ping_invalid_request_on_invalid_secret(self):
        reponse = self.client.get("/api/v1/mdbping", { "secret": "aaaaa" })
        assert reponse.status_code == HttpResponseBadRequest().status_code

    def test_mdb_ping_invalid_request_on_no_secret_provided(self):
        reponse = self.client.get("/api/v1/mdbping")
        assert reponse.status_code == HttpResponseBadRequest().status_code

    def test_mdb_ping_set_last_ping(self):
        reponse = self.client.get("/api/v1/mdbping", { "secret": self.mac1.secret })

        assert reponse.status_code == 200
        assert self.mac1.netstat == ConnectionStatus.Connected

