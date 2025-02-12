
from django.core.management.base import BaseCommand, CommandError

from gateway.utils import get_span, with_start_span
from gateway.rules import require_not_in_production

from mdb.models.mgroup import MachineGroup

MGROUP_NAME_ARG = "group_name"

class Command (BaseCommand):
    help = "Register a new machine groups for the computers"

    def add_arguments(self, parser):
        parser.add_argument( MGROUP_NAME_ARG, help="The name of the new machine group" )
    @with_start_span(__name__, "Handle addmgroup")
    def handle(self, *args, **options):
        group_name = options[MGROUP_NAME_ARG]

        get_span().set_attribute("group.name", group_name)

        require_not_in_production( "Cannot create a machine group in production mode", CommandError )

        rooms = MachineGroup.objects.filter( name = group_name )
        if len(rooms) != 0:
            raise CommandError( "A machine group with this name already exists" )
        
        MachineGroup.objects.create( name = group_name )
