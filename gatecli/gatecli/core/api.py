
import requests

from typing import Callable

from opentelemetry.propagate import inject

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
    def prepare_kwargs (self, kwargs):
        headers = kwargs.get("headers", {})
        inject(headers)
        kwargs["headers"] = headers
        return kwargs
    def _get (self, url: str, *args, **kwargs):
        raise NotImplementedError()
    def get(self, url: str, *args, **kwargs):
        return self._get(
            self.server_url(url), *args, **self.prepare_kwargs( kwargs )
        )

class API(BaseAPI):
    def _get (self, url: str, *args, **kwargs):
        return requests.get( url, *args, **kwargs )

class MockAPI(BaseAPI):
    def __init__(self, router: Callable[[str], requests.Response], args):
        assert callable(router)
        super().__init__(args)

        self._router = router
    
    def _get(self, url, *args, **kwargs):
        return self._router( url, *args, **kwargs )
