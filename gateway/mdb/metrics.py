
import gateway.metrics as metrics

from prometheus_client  import Gauge
from mdb.models.machine import Machine, ConnectionStatus

from opentelemetry import trace

import logging

__logger = logging.getLogger(__name__)
__tracer = trace.get_tracer("mdbping.tracer")

__netstat_machine_gauge = Gauge('gateway_mdb_machine_netstat', documentation="The status of the machines.", labelnames=['hostname', 'status'])
__netstat_amount_gauge  = Gauge('gateway_mdb_machine_count', documentation='Amount of machines connected', labelnames=['status'])

def mdb_update_gauge_machine():
    with __tracer.start_as_current_span("MDB Metrics Update"):
        __logger.debug("Updating metrics...")
        with __tracer.start_as_current_span('Database Query'):
            machines = Machine.objects.all()

        for possible_status in ConnectionStatus:
            total_count = 0

            for machine in machines:
                netstat = machine.netstat
                
                value = 1 if possible_status.value == netstat.value else 0
                __netstat_machine_gauge.labels(hostname = machine.host, status=possible_status).set(value)

                total_count += value
            
            __netstat_amount_gauge.labels(status = possible_status).set(total_count)

metrics.register_update_function(mdb_update_gauge_machine)
