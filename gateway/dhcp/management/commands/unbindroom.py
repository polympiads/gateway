from django.core.management.base import BaseCommand, CommandError

from dhcp.models import RoomIpSetBinding
from gateway.rules import require_not_in_production
from mdb.models import Room

class Command(BaseCommand):
    help = "Unbind the given room from it's ipset."

    def add_arguments(self, parser):
        parser.add_argument("room_name", help="The name of the room to bind.")
    
    def handle(self, *args, **options):
        require_not_in_production("Can't unbind in production.")

        try:
            room = Room.objects.get(name=options['room_name'])
        except Room.DoesNotExist:
            raise CommandError(f"No room with the name `{options['room_name']}` exists.")
        
        try:
            room = RoomIpSetBinding.objects.get(name=options['room_name'])
        except Room.DoesNotExist:
            raise CommandError("This room is unbound.")

        room.delete()
        
