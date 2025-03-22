
from .init import *  # noqa: F403

from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

def OTEL_SPAN_EXPORTER_FUNCTION(*args):
    return InMemorySpanExporter()
OTEL_SPAN_PROCESSOR_CLASS   = SimpleSpanProcessor

TESTING_ENABLED = True
