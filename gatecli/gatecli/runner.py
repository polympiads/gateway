
import argparse
import logging
import sys
import os
from typing import Callable

from gatecli.core.command import add_commands_to_parser
from gatecli.core.api import API, BaseAPI
from gatecli.core.secret import SecretManager
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

# This forces scapy to stop printing warnings about pcap
# that might interface with stdout / stderr capture
import scapy.config

scapy.config.conf.logLevel = logging.ERROR

from typing import Callable, Any

def add_env_arg ( parser: argparse.ArgumentParser, env: str, *args, **kwargs ):
    value = os.getenv( env, None )
    if value is None:
        parser.add_argument( *args, **kwargs )
    else:
        parser.add_argument( *args, default = value, **kwargs)

def main (args = sys.argv[1:], generate_api: Callable[[str], BaseAPI] = lambda host: API(host)):
    manager = SecretManager()
    parser = argparse.ArgumentParser( "Gateway Client" )
    add_env_arg( parser, "GATEWAY_API_KEY", "--api",  help = "API Key" )
    add_env_arg( parser, "GATEWAY_HOST",    "--host", help = "Gateway HTTP Endpoint")

    add_env_arg( parser, "OTEL_SERVER",  "--otel-server",  help = "Open Telemetry Server" )
    add_env_arg( parser, "OTEL_SERVICE", "--otel-service", help = "Open Telemetry Service" )
    
    commands = add_commands_to_parser(parser)

    args = parser.parse_args( args )

    if args.otel_service is not None and args.otel_server is not None:
        resource = Resource(attributes={
            SERVICE_NAME: args.otel_service
        })
        traceProvider = TracerProvider(resource=resource)
        processor = BatchSpanProcessor( OTLPSpanExporter( args.otel_server ) )
        traceProvider.add_span_processor(processor)
        trace.set_tracer_provider(traceProvider)

    api = generate_api(args.host)
    
    for name, command in commands:
        if name == args.command_name:
            tracer = trace.get_tracer_provider().get_tracer( f"gatecli-{name}" )
            with tracer.start_as_current_span( f"Running command {name}" ):
                command.handle( api, args )
