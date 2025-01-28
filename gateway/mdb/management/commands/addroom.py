
from django.core.management.base import BaseCommand, CommandError

from gateway.rules import require_not_in_production
from mdb.models.room import Room

ROOM_NAME_ARG = "room_name"

class Command (BaseCommand):
    help = "Register a new room for the computers"

    def add_arguments(self, parser):
        parser.add_argument( ROOM_NAME_ARG, help="The name of the new room" )
    def handle(self, *args, **options):
        room_name = options[ROOM_NAME_ARG]

        require_not_in_production( "Cannot create a room in production mode", CommandError )

        rooms = Room.objects.filter( name = room_name )
        if len(rooms) != 0:
            raise CommandError( "A room with this name already exists" )
        
        Room.objects.create( name = room_name )
