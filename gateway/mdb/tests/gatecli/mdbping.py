
import datetime
from django.test  import TestCase
from django.utils import timezone

from gatecli.commands.mdbping import PingException
from gatecli.core.secret import SecretManager

from mdb.models.machine import ConnectionStatus, Machine
from mdb.models.mgroup import MachineGroup
from mdb.models.room import Room

from gateway.tests.utils import call_gatecli_command

patterns = []

class GateCLIMDBPingTestCase(TestCase):
    def setUp(self):
        self.room  = Room.objects.create(name="room")
        self.group = MachineGroup.objects.create(name="group")

        self.mac = Machine.objects.create(
            host = "host",
            mac  = "ff:ff:ff:ff:ff:ff",
            
            room  = self.room,
            group = self.group
        )

        self.mac.last_ping = timezone.now() - datetime.timedelta( days = 20 )
        self.mac.save()

        return super().setUp()

    def test_simple_mdbping (self):
        SecretManager().set_secret( self.mac.secret )

        call_gatecli_command( "mdbping" )
        self.mac.refresh_from_db()

        assert self.mac.netstat == ConnectionStatus.Connected
    def test_wrong_secret_mdbping (self):
        SecretManager().set_secret( self.mac.secret + "-wrong" )
        
        with self.assertRaises(PingException):
            call_gatecli_command( "mdbping" )
        self.mac.refresh_from_db()

        assert self.mac.netstat == ConnectionStatus.Disconnected
