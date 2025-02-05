

from django.test import TestCase

from gatecli.core.api import API, BaseAPI

class GateCLIAPITestCase (TestCase):
    def setUp(self):
        self.google_base = BaseAPI("https://google.com/")
        self.google      = API("https://google.com")
        self.google_inse = API("http://google.com/")
        self.google_empt = API("google.com")
    def test_host (self):
        assert self.google_base.host == "https://google.com"
        assert self.google     .host == "https://google.com"
        assert self.google_inse.host == "http://google.com"
        assert self.google_empt.host == "http://google.com"
    def test_host_home (self):
        assert self.google_base.server_url("/") == "https://google.com/"
        assert self.google     .server_url("/") == "https://google.com/"
        assert self.google_inse.server_url("")  == "http://google.com/"
        assert self.google_empt.server_url("")  == "http://google.com/"
    def test_host_random (self):
        assert self.google_base.server_url("/abcde")  == "https://google.com/abcde"
        assert self.google     .server_url("/abcde/") == "https://google.com/abcde/"
        assert self.google_inse.server_url("abcde")   == "http://google.com/abcde"
        assert self.google_empt.server_url("abcde/")  == "http://google.com/abcde/"
    def test_base_api_get (self):
        with self.assertRaises( NotImplementedError ):
            self.google_base.get( "/" )
    def test_api_get (self):
        assert self.google.get("/").status_code == 200