import datetime

import django
import django.core.exceptions
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
)

from .models import Machine


def mdbping(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        return HttpResponseBadRequest()

    print(request.GET)
    secret = request.GET.get("secret")
    if secret is None:
        return HttpResponseBadRequest()

    try:
        host = request.get_host()
    except django.core.exceptions.DisallowedHost:
        return HttpResponseForbidden()

    machine = Machine.objects.filter(host=host).first()
    if machine is None or machine.secret != secret:
        return HttpResponseBadRequest()

    machine.last_ping = datetime.datetime.today()
    machine.save()

    return HttpResponse()
