
from django.conf import settings

from opentelemetry import trace

def with_start_span (name: str, span_name: str):
    def decorator (func):
        if not settings.INSTRUMENTATION_ENABLED: return func

        def wrapped (*args, **kwargs):
            tracer = trace.get_tracer_provider().get_tracer( name )
            
            with tracer.start_as_current_span( span_name ):
                return func(*args, **kwargs)
        wrapped.__qualname__ = func.__qualname__
        wrapped.__name__     = func.__name__

        return wrapped
    return decorator

def get_span ():
    return trace.get_current_span()

SPAN_EXPORTER = None

def get_default_span_exporter ():
    global SPAN_EXPORTER
    if SPAN_EXPORTER is None:
        SPAN_EXPORTER = settings.OTEL_SPAN_EXPORTER_FUNCTION(settings.OTEL_SERVER)
    return SPAN_EXPORTER
