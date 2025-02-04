from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
)
from django.utils import timezone

from ..models import Machine


def mdbping(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        return HttpResponseBadRequest()

    secret = request.GET.get("secret")
    if secret is None:
        return HttpResponseBadRequest()

    machine = Machine.objects.filter(secret=secret).first()
    if machine is None:
        return HttpResponseBadRequest()

    machine.last_ping = timezone.now()
    machine.save()

    return HttpResponse()
