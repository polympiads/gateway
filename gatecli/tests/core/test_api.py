
from gatecli.core.api import API
from tests.utils import using_runserver

def _api (host: str):
    class F: pass
    args = F()
    args.host = host

    return API(args)

def test_api_server_url ():
    assert _api("localhost:8000").server_url( "/some/url" ) == "http://localhost:8000/some/url"
    assert _api("localhost:8000").server_url( "some/url" )  == "http://localhost:8000/some/url"
    assert _api("localhost:8000/").server_url( "some/url" ) == "http://localhost:8000/some/url"
    assert _api( "http://localhost:8000").server_url( "/some/url" ) ==  "http://localhost:8000/some/url"
    assert _api("https://localhost:8000").server_url( "/some/url" ) == "https://localhost:8000/some/url"

@using_runserver
def test_get_requests ():
    api = _api("localhost:8000")

    response = api.get( "/aaa" )
    assert response.status_code == 404
