#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
from pathlib import Path
import sys

from opentelemetry.instrumentation.django import DjangoInstrumentor

from opentelemetry.sdk.resources import SERVICE_NAME, Resource

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

from gateway import metrics
from gateway.utils import get_default_span_exporter

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway.settings.init')
    # os.chdir(Path(__file__).cwd().parent)

    """Instrumentation"""
    from django.conf import settings
    
    if settings.INSTRUMENTATION_ENABLED:
        instrumentor = DjangoInstrumentor()
        instrumentor.instrument()

        resource = Resource(attributes={
            SERVICE_NAME: settings.OTEL_SERVICE
        })
        traceProvider = TracerProvider(resource=resource)
        processor = settings.OTEL_SPAN_PROCESSOR_CLASS( get_default_span_exporter() )
        traceProvider.add_span_processor(processor)
        trace.set_tracer_provider(traceProvider)
    if settings.TESTING_ENABLED:
        sys.path.append( os.path.join(Path(__file__).parents[1], "gatecli" ) )
    else:
        metrics.launch_thread()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    try:
        execute_from_command_line(sys.argv)
    finally:
        if not settings.TESTING_ENABLED:
            metrics.stop_thread()


if __name__ == '__main__':
    main()
