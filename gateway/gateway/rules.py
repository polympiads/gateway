
from django.conf import settings
from django.core.exceptions import PermissionDenied

def require_not_in_production (message = "Expects the server to be in Production", error = PermissionDenied):
    if getattr(settings, "GATEWAY_PRODUCTION", True):
        raise error( message )
