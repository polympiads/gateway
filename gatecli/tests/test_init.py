
from tests.utils import reset_server_db, using_runserver

import requests

@reset_server_db
@using_runserver
def test_init():
    assert requests.get("http://127.0.0.1:8000").status_code == 404
