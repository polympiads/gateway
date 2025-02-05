import logging
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
)
from django.utils import timezone

from opentelemetry import trace
from prometheus_client import Gauge

from gateway import metrics
from mdb.models.machine import ConnectionStatus

from ..models import Machine

__logger = logging.getLogger(__name__)
__tracer = trace.get_tracer("mdbping.tracer")

__netstat_amount_gauge = Gauge('gateway_mdb_machine_count', documentation='Amount of machines connected', labelnames=['status'])

def __update_gauges():
    __logger.debug("Updating metrics...")
    with __tracer.start_as_current_span('DB Query'):
        machines = Machine.objects.all()

    with __tracer.start_as_current_span('Computations'):
        connected_amount = [machine for machine in machines if machine.netstat == ConnectionStatus.Connected]
        unknown_amount = [machine for machine in machines if machine.netstat == ConnectionStatus.Unknown]
        disconnected_amount = [machine for machine in machines if machine.netstat == ConnectionStatus.Disconnected]

        __netstat_amount_gauge.labels(status='connected').set(len(connected_amount))
        __netstat_amount_gauge.labels(status='unknown').set(len(unknown_amount))
        __netstat_amount_gauge.labels(status='disconnected').set(len(disconnected_amount))

metrics.register_update_function(__update_gauges)


def mdbping(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        return HttpResponseBadRequest()

    secret = request.GET.get("secret")
    if secret is None:
        return HttpResponseBadRequest()

    with __tracer.start_as_current_span("DB Query"):
        machine = Machine.objects.filter(secret=secret).first()
    if machine is None:
        return HttpResponseBadRequest()

    __logger.info(f"{machine} has pinged.")
    machine.last_ping = timezone.now()

    with __tracer.start_as_current_span("DB Save"):
        machine.save()

    return HttpResponse()
