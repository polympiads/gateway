
import requests

from typing import Callable

from opentelemetry.propagate import inject

class BaseAPI:
    __host: str = ""

    def __init__(self, host: str):
        self.__host = host
    
    @property
    def host (self):
        host = self.__host
        if host[-1] == '/':
            host = host[:-1]

        if not (host.startswith("http://") or host.startswith("https://")):
            host = f"http://{host}"
        
        return host
    def server_url (self, url: str):
        if len(url) != 0 and url[0] == '/':
            url = url[1:]
        return f"{self.host}/{url}"
    
    def prepare_kwargs (self, kwargs):
        headers = kwargs.get("headers", {})
        inject(headers)
        kwargs["headers"] = headers
        return kwargs
    
    def _get (self, url: str, *args, **kwargs):
        raise NotImplementedError()
    
    def get (self, url: str, *args, **kwargs):
        return self._get( self.server_url( url ), *args, **self.prepare_kwargs( kwargs ) )

class API(BaseAPI):
    def _get(self, url, *args, **kwargs):
        return requests.get(url, *args, **kwargs)
