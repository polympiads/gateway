
from io import StringIO
import os
import sys
from typing import Dict, List, Tuple
from django.test import Client, TestCase, override_settings

from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry import trace
from prometheus_client import REGISTRY
import requests

from gatecli.core.api import BaseAPI
from gatecli.core.secret import SecretManager
from gateway.utils import get_default_span_exporter
from gatecli.runner import main as gatecli_main

def override_init ():
    return override_settings( GATEWAY_PRODUCTION = False )
def override_production ():
    return override_settings( GATEWAY_PRODUCTION = True )

def get_test_span_exporter () -> InMemorySpanExporter:
    return get_default_span_exporter()
def using_telemetry (func):
    def wrapped (*args, **kwargs):
        exporter = get_test_span_exporter()
        exporter.clear()
        
        return func(*args, **kwargs)
    wrapped.__qualname__ = func.__qualname__
    wrapped.__name__ = func.__name__
    return wrapped

def get_secret_file ():
    tests_dir = os.path.dirname(__file__)
    gtway_dir = os.path.dirname( os.path.dirname(tests_dir) )
    root_dir  = os.path.dirname(gtway_dir)
    gtcli_dir = os.path.join( root_dir, "gatecli" )

    return os.path.join( gtcli_dir, "gatecli", "secret.txt" )
def using_secret_manager (func):
    def wrapper (*args, **kwargs):
        secret = get_secret_file()
        if os.path.exists(secret):
            os.remove( secret )

        if SecretManager.SINGLETON is not None:
            SecretManager.SINGLETON.secret = None
            SecretManager.SINGLETON.secret_file = None
            SecretManager.SINGLETON.__init__()
        
        return func(*args, **kwargs)
    wrapper.__qualname__ = func.__qualname__
    wrapper.__name__     = func.__name__
    return wrapper

def check_telemetry (*telemetry: "Tuple[str, Dict[str, str], List[Exception], trace.StatusCode, bool]"):
    spans = get_test_span_exporter().get_finished_spans()
    
    assert len(spans) == len(telemetry)
    
    for span, data in zip(spans, telemetry):
        name, attrs, events, code, has_parent = data
        if attrs is not None:
            assert span.attributes == attrs
        assert span.name == name
        assert span.status.status_code == code
        assert len(span.events) == len(events)

        for sevent, exception in zip(span.events, events):
            assert sevent.name == "exception"
            assert sevent.attributes["exception.message"] == str(exception)
            
            _ex_type = exception.__module__ + "." + str(type(exception).__name__)

            assert sevent.attributes["exception.type"] == _ex_type

        assert has_parent == (span.parent is not None)

class MockedAPI (BaseAPI):
    def __init__(self, response: requests.Response):
        self._response = response
    def get(self, url, *args, **kwargs):
        return self._response

class DjangoClientAPI (BaseAPI):
    def __init__(self):
        self.client = Client()
        super().__init__("localhost")
    def get(self, url, *args, **kwargs):
        if len(url) == 0 or url[0] != '/':
            url = f'/{url}'
        return self.client.get(url, *args, **self.prepare_kwargs(kwargs))

def call_gatecli_command (*command: str, api = DjangoClientAPI()):
    def create_api (host: str):
        assert host == "127.0.0.1:8000"
        return api
    return gatecli_main( [ "--host", "127.0.0.1:8000" ] + list(command), create_api )

def create_response (content: str, status_code = 200):
    response = requests.Response()
    response.status_code = status_code
    response._content = content
    return response

class capture_stdouterr:
    def __enter__ (self, *args, **kwargs):
        self.stdout_copy = sys.stdout
        self.stderr_copy = sys.stderr

        self.stdout = sys.stdout = StringIO()
        self.stderr = sys.stderr = StringIO()

        return self
    def __exit__ (self, *args, **kwargs):
        sys.stdout = self.stdout_copy
        sys.stderr = self.stderr_copy

        del self.stdout_copy
        del self.stderr_copy

class PrometheusTestCase(TestCase):
    def setUp(self):
        self.clear_metrics()
    def tearDown(self):
        self.clear_metrics()
    def get_metric (self, name: str, **kwargs):
        result = REGISTRY.get_sample_value(name, None if len(kwargs.keys()) == 0 else kwargs)
        return result
    def clear_metrics (self):
        collectors = tuple(REGISTRY._collector_to_names.keys())
        for collector in collectors:
            try:
                collector._metrics.clear()
                collector._metric_init()
            except AttributeError:
                pass