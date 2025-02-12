
import datetime

from django.utils import timezone
from django.conf import settings
from gateway.tests.utils import PrometheusTestCase
from mdb.metrics import mdb_update_gauge_machine
from mdb.models.machine import ConnectionStatus, Machine
from mdb.models.mgroup import MachineGroup
from mdb.models.room import Room

class MachineMetricsTestCase (PrometheusTestCase):
    def setUp(self):
        room1  = Room.objects.create( name = "room1" )
        group1 = MachineGroup.objects.create( name = "group1" )

        self.mac1 = Machine.objects.create(host = "mac1", mac = "ff:ff:ff:ff:ff:ff", room = room1, group = group1)
        self.mac2 = Machine.objects.create(host = "mac2", mac = "ff:ff:ff:ff:ff:fe", room = room1, group = group1)
        self.mac3 = Machine.objects.create(host = "mac3", mac = "ff:ff:ff:ff:ff:fd", room = room1, group = group1)

        return super().setUp()

    @property
    def machines (self):
        return [ self.mac1, self.mac2, self.mac3 ]

    def get_netstat (self, host: str, status: ConnectionStatus):
        return self.get_metric("gateway_mdb_machine_netstat", hostname = host, status = str(status))
    def get_machine_count (self, status: ConnectionStatus):
        return self.get_metric("gateway_mdb_machine_count", status = str(status)) 

    def verify_counts (self, count_connected: int, count_unknown: int, count_disconnected: int):
        assert self.get_machine_count( ConnectionStatus.Connected ) == count_connected
        assert self.get_machine_count( ConnectionStatus.Unknown ) == count_unknown
        assert self.get_machine_count( ConnectionStatus.Disconnected ) == count_disconnected
    def verify_machine_netstat (self, machine: Machine, target: ConnectionStatus):
        count_connected, count_unknown, count_disconnected = [
            1 if target == ConnectionStatus.Connected    else 0,
            1 if target == ConnectionStatus.Unknown      else 0,
            1 if target == ConnectionStatus.Disconnected else 0
        ]

        assert self.get_netstat(machine.host, ConnectionStatus.Connected)    == count_connected
        assert self.get_netstat(machine.host, ConnectionStatus.Unknown)      == count_unknown
        assert self.get_netstat(machine.host, ConnectionStatus.Disconnected) == count_disconnected

    def force_into_netstat (self, machine: Machine, target: ConnectionStatus):
        time = timezone.now()

        delta = datetime.timedelta()
        if target == ConnectionStatus.Unknown:
            delta = settings.PING_INTERVAL + settings.PING_INTERVAL_TOLERANCE
        if target == ConnectionStatus.Disconnected:
            delta = 2 * settings.PING_INTERVAL + settings.PING_INTERVAL_TOLERANCE
        
        machine.last_ping = time - delta
        machine.save()

    def test_default_behaviour (self):
        mdb_update_gauge_machine()

        self.verify_counts(3, 0, 0)

        for mac in self.machines:
            self.verify_machine_netstat(mac, ConnectionStatus.Connected)
    def test_forced (self):
        self.force_into_netstat( self.mac1, ConnectionStatus.Connected )
        self.force_into_netstat( self.mac2, ConnectionStatus.Unknown )
        self.force_into_netstat( self.mac3, ConnectionStatus.Disconnected )

        mdb_update_gauge_machine()

        self.verify_counts(1, 1, 1)
        
        self.verify_machine_netstat( self.mac1, ConnectionStatus.Connected )
        self.verify_machine_netstat( self.mac2, ConnectionStatus.Unknown )
        self.verify_machine_netstat( self.mac3, ConnectionStatus.Disconnected )
    def test_forced_then_fixed (self):
        self.force_into_netstat( self.mac1, ConnectionStatus.Connected )
        self.force_into_netstat( self.mac2, ConnectionStatus.Unknown )
        self.force_into_netstat( self.mac3, ConnectionStatus.Disconnected )

        mdb_update_gauge_machine()

        self.verify_counts(1, 1, 1)
        
        self.verify_machine_netstat( self.mac1, ConnectionStatus.Connected )
        self.verify_machine_netstat( self.mac2, ConnectionStatus.Unknown )
        self.verify_machine_netstat( self.mac3, ConnectionStatus.Disconnected )

        self.force_into_netstat( self.mac1, ConnectionStatus.Connected )
        self.force_into_netstat( self.mac2, ConnectionStatus.Connected )
        self.force_into_netstat( self.mac3, ConnectionStatus.Connected )

        mdb_update_gauge_machine()

        self.verify_counts(3, 0, 0)

        for mac in self.machines:
            self.verify_machine_netstat(mac, ConnectionStatus.Connected)