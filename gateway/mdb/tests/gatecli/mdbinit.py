
import os
from django.test import TestCase, override_settings
import requests

from gatecli.core.secret import SecretManager
from mdb.models.mgroup import MachineGroup
from mdb.models.room import Room

from mdb.management.commands.mdbinit import Command as MDBInitCommand
from gateway.tests.utils import MockedAPI, call_gatecli_command, capture_stdouterr, create_response, get_secret_file, override_init, using_secret_manager

def use_mdbinit_urls (func):
    with_url = override_settings(ROOT_URLCONF = "mdb.management.commands.mdbinit")(func)

    return override_init()( with_url )

BROKEN_SERVER_STDOUT_RESULT = """DANGER, Could not parse the JSON from the response
  Content : Not a JSON

Status code : 200
ERROR : Invalid response content

Causes of the error :
 - JSON Data is invalid
"""
NON_UNIQUE_STDOUT_RESULT = """Status code : 409
ERROR : Machine already exists

Causes of the error :
 - Machine with this Host Name already exists.
 - Machine with this MAC Address already exists.
"""
MDBINIT_SAVE_SECRET_ERROR_MESSAGE = """Successfully created machine in MDB
 - Secret :  SECRET
=========================================================================
  DANGER, Could not save the secret inside of the file
   - The secret is  SECRET
   - Either delete the machine from the MDB or save the secret yourself
=========================================================================
"""
MISSING_JSON_STDOUT_MESSAGE = """Successfully created machine in MDB
Status code : 200
ERROR : Missing secret in JSON

Causes of the error :
 - Malformed JSON {'secrt': 'SECRET'}
"""
ERR_500_NO_EXPLICIT_ERROR_STDOUT_MESSAGE = """Status code : 500
ERROR : <No 'error' in content>

Causes of the error :
 - <No 'reasons' in content>
"""

class GateCLIMDBInitTestCase (TestCase):
    def setUp(self):
        with override_init():
            self.room = Room.objects.create(name = "room")
            self.group = MachineGroup.objects.create(name = "group")

            MDBInitCommand().prepare_options( room = "room", group = "group" ) 
    
    @using_secret_manager
    @use_mdbinit_urls
    def test_simple_mdbinit (self):
        with capture_stdouterr() as capture:
            call_gatecli_command("mdbinit", "host")

        lines = capture.stdout.getvalue().split("\n")
        assert len(lines) == 3
        assert lines[0] == "Successfully created machine in MDB"
        assert lines[1].startswith(" - Secret :  ")
        assert lines[1].endswith("******************************************************")
        assert len(lines[1]) == 77
        assert lines[2] == ""

        manager = SecretManager()
        assert manager.get_secret().startswith( lines[1][13:23] )
        
        lines = capture.stderr.getvalue().split("\n")
        assert len(lines) == 1
        assert lines[0] == ""
    @using_secret_manager
    def test_mdbinit_broken_server (self):
        with capture_stdouterr() as capture:
            call_gatecli_command( 
                "mdbinit", "host",
                api = MockedAPI( create_response("Not a JSON") )
            )
        
        assert capture.stdout.getvalue() == BROKEN_SERVER_STDOUT_RESULT
        assert capture.stderr.getvalue() == ""

        assert SecretManager().secret is None
    @using_secret_manager
    @use_mdbinit_urls
    def test_mdbinit_non_unique (self):
        with capture_stdouterr() as _:
            call_gatecli_command( "mdbinit", "host" )
        with capture_stdouterr() as capture:
            call_gatecli_command( "mdbinit", "host" )
        assert (capture.stdout.getvalue()) == NON_UNIQUE_STDOUT_RESULT
        assert (capture.stderr.getvalue()) == ""
    @using_secret_manager
    @use_mdbinit_urls
    def test_mdbinit_error_saving_secret (self):
        def custom_set_secret(*args, **kwargs):
            raise Exception("Could not save secret")
        set_secret = SecretManager.set_secret
        SecretManager.set_secret = custom_set_secret

        try:
            api = MockedAPI( create_response('{"secret": "SECRET"}') )
            with capture_stdouterr() as capture:
                with self.assertRaisesMessage(Exception, "Could not save secret"):
                    call_gatecli_command( "mdbinit", "host", api = api )
            assert capture.stdout.getvalue() == MDBINIT_SAVE_SECRET_ERROR_MESSAGE
            assert capture.stderr.getvalue() == ""
        finally:
            SecretManager.set_secret = set_secret
    @using_secret_manager
    def test_mdbinit_missing_json (self):
        api = MockedAPI( create_response('{"secrt": "SECRET"}') )

        with capture_stdouterr() as capture:
            call_gatecli_command( "mdbinit", "host", api = api )
        
        assert capture.stdout.getvalue() == MISSING_JSON_STDOUT_MESSAGE
        assert capture.stderr.getvalue() == ""
    @using_secret_manager
    def test_mdbinit_error_500 (self):
        api = MockedAPI( create_response('{}', 500) )

        with capture_stdouterr() as capture:
            call_gatecli_command( "mdbinit", "host", api = api )
        
        assert capture.stdout.getvalue() == ERR_500_NO_EXPLICIT_ERROR_STDOUT_MESSAGE
        assert capture.stderr.getvalue() == ""