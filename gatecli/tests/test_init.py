
from typing import List
from tests.utils import reset_server_db, using_runserver

import importlib
import requests
import os

@reset_server_db
@using_runserver
def test_init():
    assert requests.get("http://127.0.0.1:8000").status_code == 404

def test_import_everything ():
    def traverse_import (path: str, package: List[str], extension=""):
        if os.path.exists(path) and os.path.isfile(path):
            if extension == ".py":
                module = ".".join(package)
                importlib.import_module( module )
            return
        
        for subpath in os.listdir( path ):
            traverse_import( os.path.join(path, subpath), package + [ os.path.splitext(subpath)[0] ], os.path.splitext(subpath)[1] )
    traverse_import( 
        os.path.join( os.path.dirname( os.path.dirname(__file__) ), "gatecli" ), [ "gatecli" ] )