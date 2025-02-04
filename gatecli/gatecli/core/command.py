
from argparse import ArgumentParser
import importlib
import os

from gatecli.core.api import API

COMMAND_SUB_CLASSES = []

CACHED_COMMANDS = False

class CommandError(Exception):
    pass

class Command:
    def __init_subclass__(cls):
        COMMAND_SUB_CLASSES.append(( cls.__module__.split(".")[-1], cls() ))

    def add_arguments (self, parser: ArgumentParser): pass
    def handle (self, api: API, args): pass

def get_all_commands ():
    global CACHED_COMMANDS

    if CACHED_COMMANDS:
        return COMMAND_SUB_CLASSES

    gatecli_dir  = os.path.dirname( os.path.dirname( __file__ ) )
    commands_dir = os.path.join( gatecli_dir, "commands" )

    files = os.listdir(commands_dir)
    for file in files:
        if os.path.splitext( file )[1] == ".py":
            module = "gatecli.commands." + os.path.basename( file )[:-3]
            importlib.import_module(module)

    CACHED_COMMANDS = True

    return COMMAND_SUB_CLASSES

def add_commands_to_parser (argparser: ArgumentParser, dest = "command_name"):
    subparsers = argparser.add_subparsers(dest = dest)
    
    commands = get_all_commands()

    for name, command in commands:
        parser = subparsers.add_parser( name )
        command.add_arguments(parser)
    
    return commands
