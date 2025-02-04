
from django.core.management.base import BaseCommand, CommandError

from gateway.utils import get_span, with_start_span
from gateway.rules import require_not_in_production
from mdb.models.room import Room

ROOM_NAME_ARG = "room_name"

class Command (BaseCommand):
    help = "Delete a room from the Machine Database"

    def add_arguments(self, parser):
        parser.add_argument( ROOM_NAME_ARG, help="The name of the room to delete" )
    @with_start_span(__name__, "Handle delroom")
    def handle(self, *args, **options):
        room_name = options[ROOM_NAME_ARG]

        get_span().set_attribute("room.name", room_name)

        require_not_in_production( "Cannot delete a room in production mode", CommandError )

        rooms = list( Room.objects.filter( name = room_name ) )
        if len(rooms) == 0:
            raise CommandError( "This room does not exist" )
        
        rooms[0].delete()
