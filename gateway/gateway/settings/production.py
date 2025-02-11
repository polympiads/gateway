import os
from .base import *  # noqa: F403

GATEWAY_PRODUCTION = True

SECRET_KEY = os.getenv( 'GATEWAY_SECRET_KEY', 'django-missing' )

class SecretKeyNotProvidedException(Exception):
    def __init__(self):
        super().__init__("No secrets keys we given.")

if SECRET_KEY == 'django-missing':
    raise SecretKeyNotProvidedException()
