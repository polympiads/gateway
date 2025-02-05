
from typing import Tuple
from wsgiref.simple_server import make_server
from django.core.management.base import BaseCommand, CommandError
from django.forms import ValidationError
from django.http import JsonResponse
from django.test import override_settings
from django.views import View
from django.urls import path
from django.contrib import admin
from django.core.wsgi import get_wsgi_application

from gateway.utils import get_span, with_start_span
from mdb.models.machine import Machine
from mdb.models.mgroup import MachineGroup
from mdb.models.room import Room
from gateway.rules import require_not_in_production

from opentelemetry import trace

class MachineInitView (View):
    room  : "Room | None" = None
    group : "Room | None" = None

    def unpack_parameters (self) -> "Tuple[Room, MachineGroup]":
        assert MachineInitView.room  is not None
        assert MachineInitView.group is not None
        return (MachineInitView.room, MachineInitView.group)
    @with_start_span(__name__, "Machine Initialization")
    def get (self, request, *args, **kwargs):
        require_not_in_production( "Machine Init View should only be started in the mdbinit command." )

        room, group = self.unpack_parameters()

        mac  = request.GET['mac']
        host = request.GET['host']
        
        get_span().set_attribute('machine.host', host)
        get_span().set_attribute('machine.mac',  mac)
        
        try:
            machine = Machine.objects.create(
                mac = mac,
                host = host,

                room = room,
                group = group
            )

            get_span().set_attribute('machine.secretprefix', machine.secret[:8])
        except ValidationError as error:
            trace.get_current_span().set_status( trace.StatusCode.ERROR )
            return JsonResponse({
                "error"   : "Machine already exists",
                "reasons" : error.messages
            }, status = 409)

        return JsonResponse({ "secret": machine.secret })

urlpatterns = [
    path('admin/',   admin.site.urls),
    path('mdbinit/', MachineInitView.as_view())
]

class Command (BaseCommand):
    help = "Initialization procedure of the MDB for a room and a group"

    server = None

    @staticmethod
    def shutdown ():
        if Command.server is not None:
            Command.server.shutdown()
            Command.server = None

    def add_arguments(self, parser):
        parser.add_argument("room",  help="The name of the room being initialized")
        parser.add_argument("group", help="The name of the group being initialized")
    def create_server (self):
        Command.server = make_server( '127.0.0.1', 8000, get_wsgi_application() )
    def prepare_options (self, *args, **options):
        require_not_in_production( "Cannot initialize MDB in production", CommandError )

        room_name  = options["room"]
        group_name = options["group"]

        rooms = Room.objects.filter(name = room_name)
        if len(rooms) == 0:
            raise CommandError(f"Could not find the room with the name '{room_name}'")
        groups = MachineGroup.objects.filter(name = group_name)
        if len(groups) == 0:
            raise CommandError(f"Could not find the group with the name '{group_name}'")

        room  = rooms[0]
        group = groups[0]

        MachineInitView.room  = room
        MachineInitView.group = group

        self.create_server()

    def handle(self, *args, **options):
        self.prepare_options(*args, **options)
        
        with override_settings(
            ROOT_URLCONF = "mdb.management.commands.mdbinit"
        ):
            Command.server.serve_forever()