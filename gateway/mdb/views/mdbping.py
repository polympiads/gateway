import logging
from django.http import (
    HttpRequest,
    JsonResponse,
)
from django.utils import timezone

from opentelemetry import trace

from ..models import Machine

__logger = logging.getLogger(__name__)
__tracer = trace.get_tracer("mdbping.tracer")

def mdbping(request: HttpRequest) -> JsonResponse:
    if request.method != "GET":
        return JsonResponse({ "error": "the request should be GET" }, status = 400)

    secret = request.GET.get("secret")
    if secret is None:
        return JsonResponse({ "error": "missing secret param" }, status = 400)

    with __tracer.start_as_current_span("DB Query"):
        machine = Machine.objects.filter(secret=secret).first()
    if machine is None:
        return JsonResponse({ "error": "unregistered machine in the network" }, status = 400)

    __logger.info(f"{machine} has pinged.")
    machine.last_ping = timezone.now()

    with __tracer.start_as_current_span("DB Save"):
        machine.save()

    return JsonResponse({ "message": "OK" })
