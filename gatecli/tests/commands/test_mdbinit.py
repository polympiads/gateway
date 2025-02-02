
import os
import subprocess

from gatecli.commands.mdbinit import MDBInitCommand, find_mac_addresses
from gatecli.core.secret import SecretManager
from gatecli.runner import main

from tests.core.test_secret import SECRET_FILE
from tests.utils import capture_stdouterr, reset_server_db, using_command, uses_secret_manager

class MockAPI:
    def __init__(self, content, code = 200):
        class F: pass
        self.response = F()
        self.response.content = content
        self.response.status_code = code
    def get (self, url, *args, **kwargs):
        return self.response
class Args:
    def __init__(self, **kwargs):
        for key in kwargs.keys():
            setattr(self, key, kwargs[key])

def mdbinit_db (func):
    @reset_server_db
    def wrapped (*args, **kwargs):
        subprocess.run([ "bash", "/app/init.sh", "addroom",   "room1"  ])
        subprocess.run([ "bash", "/app/init.sh", "addmgroup", "group1" ])
        return func(*args, **kwargs)
    wrapped.__qualname__ = func.__qualname__
    wrapped.__name__ = func.__name__
    return wrapped
def using_mdbinit (func):
    return mdbinit_db( using_command( "bash", "/app/init.sh", "mdbinit", "room1", "group1" )(func) )

def test_find_mac_addresses ():
    assert find_mac_addresses() == "02:42:ac:12:00:02"

@uses_secret_manager
@using_mdbinit
def test_simple_mdbinit ():
    with capture_stdouterr() as capture:
        main([ "--host", "127.0.0.1:8000", "mdbinit", "host" ])

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

BROKEN_SERVER_STDOUT_RESULT = """DANGER, Could not parse the JSON from the response
  Content : Not a JSON

Status code : 200
ERROR : Invalid response content

Causes of the error :
 - JSON Data is invalid
"""

@uses_secret_manager
def test_mdbinit_broken_server ():
    with capture_stdouterr() as capture:
        MDBInitCommand().handle( MockAPI( "Not a JSON" ), Args( hostname="host" ) )

    print(capture.stdout.getvalue())
    assert capture.stdout.getvalue() == BROKEN_SERVER_STDOUT_RESULT
    assert capture.stderr.getvalue() == ""

    assert SecretManager().secret is None

NON_UNIQUE_STDOUT_RESULT = """Status code : 409
ERROR : Machine already exists

Causes of the error :
 - Machine with this Host Name already exists.
 - Machine with this MAC Address already exists.
"""

@uses_secret_manager
@using_mdbinit
def test_mdbinit_non_unique ():
    with capture_stdouterr() as capture1:
        main([ "--host", "127.0.0.1:8000", "mdbinit", "host" ])
    with capture_stdouterr() as capture2:
        main([ "--host", "127.0.0.1:8000", "mdbinit", "host" ])
    assert (capture2.stdout.getvalue()) == NON_UNIQUE_STDOUT_RESULT
    assert (capture2.stderr.getvalue()) == ""

WRONG_FS_ERROR_MESSAGE = """Successfully created machine in MDB
 - Secret :  SECRET
=========================================================================
  DANGER, Could not save the secret inside of the file
   - The secret is  SECRET
   - Either delete the machine from the MDB or save the secret yourself
=========================================================================
[Errno 21] Is a directory: '/app/gatecli/gatecli/secret.txt'
"""

@uses_secret_manager
def test_mdbinit_wrong_fs ():
    api = MockAPI('{"secret": "SECRET"}')

    os.mkdir(SECRET_FILE)
    with capture_stdouterr() as capture:
        try:
            MDBInitCommand().handle( api, Args(hostname="host") )
        except Exception as exception:
            print(exception)

    os.rmdir(SECRET_FILE)
    assert capture.stdout.getvalue() == WRONG_FS_ERROR_MESSAGE

MISSING_JSON_STDOUT_MESSAGE = """Successfully created machine in MDB
Status code : 200
ERROR : Missing secret in JSON

Causes of the error :
 - Malformed JSON {'secrt': 'SECRET'}
"""

@uses_secret_manager
def test_mdbinit_missing_json ():
    api = MockAPI('{"secrt": "SECRET"}')

    os.mkdir(SECRET_FILE)
    with capture_stdouterr() as capture:
        try:
            MDBInitCommand().handle( api, Args(hostname="host") )
        except Exception as exception:
            print(exception)

    os.rmdir(SECRET_FILE)
    assert capture.stdout.getvalue() == MISSING_JSON_STDOUT_MESSAGE

ERR_500_NO_EXPLICIT_ERROR_STDOUT_MESSAGE = """Status code : 500
ERROR : <No 'error' in content>

Causes of the error :
 - <No 'reasons' in content>
"""

@uses_secret_manager
def test_mdbinit_err_500_no_explicit_error ():
    api = MockAPI('{}', 500)

    os.mkdir(SECRET_FILE)
    with capture_stdouterr() as capture:
        try:
            MDBInitCommand().handle( api, Args(hostname="host") )
        except Exception as exception:
            print(exception)

    os.rmdir(SECRET_FILE)
    print(capture.stdout.getvalue())
    assert capture.stdout.getvalue() == ERR_500_NO_EXPLICIT_ERROR_STDOUT_MESSAGE
