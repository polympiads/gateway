
from django.core.management.base import BaseCommand, CommandError

from gateway.utils import get_span, with_start_span
from mdb.models.mgroup import MachineGroup
from gateway.rules import require_not_in_production

MGROUP_NAME_ARG = "group_name"

class Command (BaseCommand):
    help = "Delete a machine group from the Machine Database"

    def add_arguments(self, parser):
        parser.add_argument( MGROUP_NAME_ARG, help="The name of the machine group to delete" )
    @with_start_span(__name__, "Handle delmgroup")
    def handle(self, *args, **options):
        group_name = options[MGROUP_NAME_ARG]

        get_span().set_attribute("group.name", group_name)

        require_not_in_production( "Cannot delete a machine group in production mode", CommandError )

        groups = list( MachineGroup.objects.filter( name = group_name ) )
        if len(groups) == 0:
            raise CommandError( "This machine group does not exist" )
        
        groups[0].delete()
