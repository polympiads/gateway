from django.core.management.base import BaseCommand, CommandError

from dhcp.models import IpSet, RoomIpSetBinding
from dhcp.utils import int2ip
from gateway.rules import require_not_in_production
from mdb.models import Room

from .utils import parse_ip_set

class Command(BaseCommand):
    help = "Bind the room to a certain ipset."

    def add_arguments(self, parser):
        parser.add_argument("room_name", help="The name of the room to bind.")
        parser.add_argument("ipset", help="The base of the ipset to bind it to. Should be in IPv4 format.")
    
    def handle(self, *args, **options):
        require_not_in_production("Can't bind in production.")

        ip_base, _ = parse_ip_set(options['ipset'], None, require_submask=False)

        try:
            room = Room.objects.get(name=options['room_name'])
        except Room.DoesNotExist:
            raise CommandError(f"No room with the name `{options['room_name']}` exists.")

        try:
            ipset = IpSet.objects.get(ipv4_base=int2ip(ip_base))
        except IpSet.DoesNotExist:
            raise CommandError(f"No ipset with the ip base `{int2ip(ip_base)}` exists.")
           
        if RoomIpSetBinding.objects.filter(room=room).exists():
            raise CommandError("This room is already bound.")

        RoomIpSetBinding.objects.create(room=room, ipset=ipset)
        
