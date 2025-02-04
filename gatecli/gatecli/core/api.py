
import requests

from typing import Callable

class BaseAPI:
    host: str = ""

    def __init__(self, args):
        self.host = args.host

    def server_url (self, url: str):
        if url[0] == '/':
            url = url[1:]
        
        host = self.host
        if host[-1] == '/':
            host = host[:-1]

        if not (host.startswith("http://") or host.startswith("https://")):
            host = f"http://{host}"
        
        return f"{host}/{url}"
    def get(self, url: str, *args, **kwargs):
        raise NotImplementedError()

class API(BaseAPI):
    def get (self, url: str, *args, **kwargs):
        return requests.get( self.server_url( url ), *args, **kwargs )

class MockAPI(BaseAPI):
    def __init__(self, router: Callable[[str], requests.Response], args):
        assert callable(router)
        super().__init__(args)

        self._router = router
    
    def get(self, url, *args, **kwargs):
        return self._router( url, *args, **kwargs )
