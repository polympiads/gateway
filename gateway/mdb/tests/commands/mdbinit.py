
from contextlib import contextmanager
import os
import sys
import threading
import time
from django.test import TransactionTestCase
from django.core.management import call_command
from django.core.management.base import CommandError

from mdb.models.machine import Machine
from mdb.models.mgroup import MachineGroup
from mdb.models.room import Room

from mdb.management.commands.mdbinit import Command as MDBInitCommand

import requests
import sys

@contextmanager
def suppress_stderr():
    """Temporarily disable stdout."""
    original_stderr = sys.stderr
    sys.stderr = open(os.devnull, 'w')
    try:
        yield
    finally:
        sys.stderr.close()
        sys.stderr = original_stderr

def test_mdbinit (room = "room1", group = "group1", expects_error = False):
    def decorator (test_func):
        def wrapped (self, *args, **kwargs):
            time.sleep(0.25)
            try:
                self.prepare()

                class _MDBThread (threading.Thread):
                    had_error = False
                    error = None
                    def run (self):
                        try:
                            with suppress_stderr():
                                call_command( "mdbinit", room, group )
                        except Exception as err:
                            self.error = err
                            self.had_error = True
                    
                    def shutdown (self):
                        MDBInitCommand.shutdown()
                        self.join()
                
                if not expects_error:
                    thread = _MDBThread()
                    thread.daemon = True
                    thread.start()
                    time.sleep(0.25)
                    test_func(self, *args, **kwargs)
                    thread.shutdown()
                else:
                    thread = _MDBThread()
                    thread.daemon = True
                    thread.start()
                    time.sleep(0.1)
                    thread.shutdown()
                    test_func(self, thread.had_error, thread.error, *args, **kwargs)
            finally:
                self.delete()
        wrapped.__name__ = test_func.__name__
        wrapped.__qualname__ = test_func.__qualname__
        return wrapped
    return decorator

class MDBInitCommandTestCase (TransactionTestCase):
    def prepare(self):
        self.room  = Room.objects.create( name = "room1" )
        self.group = MachineGroup.objects.create( name = "group1" )

        self.server = "http://localhost:8000"
        return super().setUp()
    def delete (self):
        Machine.objects.all().delete()
        MachineGroup.objects.all().delete()
        Room.objects.all().delete()

    @test_mdbinit()
    def test_admin (self):
        assert requests.get(f"{self.server}/admin/login").status_code == 200
    @test_mdbinit()
    def test_mdbinit_host (self):
        assert Machine.objects.count() == 0
        response = requests.get(f"{self.server}/mdbinit/?mac=fa:fb:fc:fd:fe:ff&host=root0")
        assert response.status_code == 200
        assert Machine.objects.count() == 1
        machine = Machine.objects.all()[0]
        assert machine.mac == "fa:fb:fc:fd:fe:ff"
        assert machine.host == "root0"
        assert response.content.decode() == "{\"secret\": \"" + machine.secret + "\"}"
    @test_mdbinit()
    def test_mdbinit_already_exists (self):
        assert Machine.objects.count() == 0
        response = requests.get(f"{self.server}/mdbinit/?mac=fa:fb:fc:fd:fe:ff&host=root0")
        response = requests.get(f"{self.server}/mdbinit/?mac=fa:fb:fc:fd:fe:ff&host=root1")
        assert response.status_code == 409
        assert response.content.decode() == '{"error": "Machine already exists", "reasons": ["Machine with this MAC Address already exists."]}'
        response = requests.get(f"{self.server}/mdbinit/?mac=fa:fb:fc:fd:fe:fe&host=root0")
        assert response.status_code == 409
        assert response.content.decode() == '{"error": "Machine already exists", "reasons": ["Machine with this Host Name already exists."]}'

        assert Machine.objects.count() == 1
        machine = Machine.objects.all()[0]
        assert machine.mac == "fa:fb:fc:fd:fe:ff"
        assert machine.host == "root0"
    @test_mdbinit( "room2", "group1", True )
    def test_mdbinit_wrong_room(self, had_error, error):
        assert had_error
        assert isinstance(error, CommandError)
        assert str(error) == "Could not find the room with the name 'room2'"
    @test_mdbinit( "room1", "group2", True )
    def test_mdbinit_wrong_group(self, had_error, error):
        assert had_error
        assert isinstance(error, CommandError)
        assert str(error) == "Could not find the group with the name 'group2'"

"""
export GATEWAY_SECRET_KEY="secret"
export DJANGO_SETTINGS_MODULE="gateway.settings.init"
cd gateway
python3 manage.py test
"""