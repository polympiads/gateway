from django.core.management.base import BaseCommand, CommandError

from dhcp.models import IpSet
from dhcp.utils import int2ip
from gateway.rules import require_not_in_production

from .utils import parse_ip_set

class Command(BaseCommand):
    help = "Delete an existing ipset in the database. Will error out if the ipset does not exists, or if there are many matching ipsets."

    def add_arguments(self, parser):
        parser.add_argument('ip_base', help="The base ip. Should be in IPv4 format.")

    def handle(self, *args, **options):
        require_not_in_production("Can't modify the ipset from the production server", CommandError)

        ip_base, _ = parse_ip_set(options['ip_base'], None, require_submask=False)
        ip_base_str = int2ip(ip_base)

        matching_ipsets = IpSet.objects.filter(ipv4_base=ip_base_str)
        if not matching_ipsets.exists():
            raise CommandError(f"Error : no ipsets exists with the ip base {ip_base_str}")

        print(f"Deleting : {matching_ipsets}")

        matching_ipsets.delete()
        