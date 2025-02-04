
import argparse
import sys

from gatecli.core.command import add_commands_to_parser
from gatecli.core.api import API, BaseAPI
from gatecli.core.secret import SecretManager

from typing import Callable, Any

def main (args = sys.argv[1:], api_generator: Callable[[Any], BaseAPI] = lambda args : API(args)):
    manager = SecretManager()
    parser = argparse.ArgumentParser( "Gateway Client" )
    parser.add_argument( "--api",  help = "API Key" )
    parser.add_argument( "--host", help = "Gateway Hostname" )
    
    commands = add_commands_to_parser(parser)

    args = parser.parse_args( args )

    api = api_generator(args)
    
    for name, command in commands:
        if name == args.command_name:
            command.handle( api, args )
