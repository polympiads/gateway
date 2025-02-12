
from contextlib import contextmanager
import os
import sys
import threading
import time
from wsgiref.simple_server import WSGIServer
from django.test import Client, TestCase, TransactionTestCase, override_settings
from django.core.management import call_command
from django.core.management.base import CommandError

from gateway.tests.utils import check_telemetry, using_telemetry
from mdb.tests.gatecli.mdbinit import mock_create_server, use_mdbinit_urls
from mdb.models.machine import Machine
from mdb.models.mgroup import MachineGroup
from mdb.models.room import Room

from mdb.management.commands.mdbinit import Command as MDBInitCommand

from opentelemetry import trace

import requests
import sys

class MDBInitCommandTestCase (TestCase):
    @mock_create_server
    def setUp(self):
        self.room  = Room.objects.create( name = "room" )
        self.group = MachineGroup.objects.create( name = "group" )

        self.client = Client()

        MDBInitCommand().prepare_options( room = "room", group = "group" )
    
    @mock_create_server
    @use_mdbinit_urls
    def test_admin (self):
        assert self.client.get(f"/admin/login/").status_code == 200
    @using_telemetry
    @mock_create_server
    @use_mdbinit_urls
    def test_mdbinit_host (self):
        assert Machine.objects.count() == 0
        response = self.client.get(f"/mdbinit/?mac=fa:fb:fc:fd:fe:ff&host=root0")
        assert response.status_code == 200
        assert Machine.objects.count() == 1
        machine = Machine.objects.all()[0]
        assert machine.mac == "fa:fb:fc:fd:fe:ff"
        assert machine.host == "root0"
        assert response.content.decode() == "{\"secret\": \"" + machine.secret + "\"}"

        check_telemetry((
            "Machine Initialization",
            { "machine.host": "root0", "machine.mac": "fa:fb:fc:fd:fe:ff", "machine.secretprefix" : machine.secret[:8] },
            [  ],
            trace.StatusCode.UNSET, True
        ), (
            "GET mdbinit/", None,
            [  ],
            trace.StatusCode.UNSET, False
        ))
    @mock_create_server
    @use_mdbinit_urls
    def test_mdbinit_already_exists (self):
        assert Machine.objects.count() == 0
        response = self.client.get(f"/mdbinit/?mac=fa:fb:fc:fd:fe:ff&host=root0")
        response = self.client.get(f"/mdbinit/?mac=fa:fb:fc:fd:fe:ff&host=root1")
        assert response.status_code == 409
        assert response.content.decode() == '{"error": "Machine already exists", "reasons": ["Machine with this MAC Address already exists."]}'
        response = self.client.get(f"/mdbinit/?mac=fa:fb:fc:fd:fe:fe&host=root0")
        assert response.status_code == 409
        assert response.content.decode() == '{"error": "Machine already exists", "reasons": ["Machine with this Host Name already exists."]}'

        assert Machine.objects.count() == 1
        machine = Machine.objects.all()[0]
        assert machine.mac == "fa:fb:fc:fd:fe:ff"
        assert machine.host == "root0"
    
    @mock_create_server
    def test_mdbinit_wrong_room(self):
        with self.assertRaisesMessage( CommandError, "Could not find the room with the name 'room2'"):
            MDBInitCommand().handle( room = "room2", group = "group" )
    @mock_create_server
    def test_mdbinit_wrong_group(self):
        with self.assertRaisesMessage( CommandError, "Could not find the group with the name 'group2'"):
            MDBInitCommand().handle( room = "room", group = "group2" )
    @mock_create_server
    def test_mdbinit_handle_runs_server (self):
        call_command("mdbinit", "room", "group")

        assert MDBInitCommand.server.called_serve_forever
        assert not MDBInitCommand.server.called_shutdown
    @mock_create_server
    def test_mdbinit_shutdown_stops_server (self):
        MDBInitCommand().prepare_options( room = "room", group = "group" )

        server = MDBInitCommand.server
        assert not server.called_serve_forever
        assert not server.called_shutdown
        MDBInitCommand.shutdown()
        assert not server.called_serve_forever
        assert server.called_shutdown
        assert MDBInitCommand.server is None
        server.called_shutdown = False
        MDBInitCommand.shutdown()
        assert not server.called_serve_forever
        assert not server.called_shutdown
    
    def test_mdbinit_create_server (self):
        MDBInitCommand().create_server()
        assert isinstance(MDBInitCommand.server, WSGIServer)
        assert MDBInitCommand.server.server_port == 8000
        MDBInitCommand.server.server_close()
        
        # Test again to validate that the server was properly closed
        # Useful because github CI sometimes behave differently than
        # Local tests, so we verify that this strange behaviour can't
        # Be started by this test.
        MDBInitCommand().create_server()
        assert isinstance(MDBInitCommand.server, WSGIServer)
        assert MDBInitCommand.server.server_port == 8000
        MDBInitCommand.server.server_close()