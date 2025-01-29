
from django.test import override_settings

def override_init ():
    return override_settings( GATEWAY_PRODUCTION = False )
def override_production ():
    return override_settings( GATEWAY_PRODUCTION = True )
