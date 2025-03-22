from django.core.management.base import BaseCommand, CommandError
from django.forms import ValidationError

from dhcp import utils
from dhcp.models.ipset import IpSet
from gateway.rules import require_not_in_production
from .utils import parse_ip_set

class Command(BaseCommand):
    help = "Register a new ipset in the database. Will error out if the new ipset intersect with an already registered ipset."

    def add_arguments(self, parser):
        parser.add_argument('ip_base', help="The base ip. Can include the submask shorthand. Should be in IPv4 format.")
        parser.add_argument('submask', help="The ip submask, used to generate the sub ips. Should be in IPv4 format. Override the shorthand if provided.", nargs='?')

    def handle(self, *args, **options):
        require_not_in_production("Can't modify the ipset from the production server", CommandError)

        ip_base, submask = parse_ip_set(options['ip_base'], options['submask'])

        if not ((ip_base & submask) == ip_base):
            raise CommandError("Error : ip_base & submask != ip_base")
        
        try:
            IpSet.objects.create(ipv4_base=utils.int2ip(ip_base), submask=utils.int2ip(submask))
        except ValidationError as e:
            raise CommandError(f"Error : failed to create the ipset : {e}")


