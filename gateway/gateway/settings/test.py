
from .base import *

from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

GATEWAY_PRODUCTION = False

OTEL_SPAN_EXPORTER_FUNCTION = lambda *args : InMemorySpanExporter()
OTEL_SPAN_PROCESSOR_CLASS   = SimpleSpanProcessor