
from typing import Dict, List, Tuple
from django.test import override_settings

from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry import trace

from gateway.utils import get_default_span_exporter

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
