
from typing import Dict
import requests

class API:
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
    def get (self, url: str, *args, **kwargs):
        return requests.get( self.server_url( url ), *args, **kwargs )
