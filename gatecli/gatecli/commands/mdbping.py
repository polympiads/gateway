from gatecli.core.command import Command
from gatecli.gatecli.core.secret import SecretManager

HTTP_RESPONSE_OK: int = 200


class PingException(Exception):
    pass


class MDBPingCommand(Command):
    def handle(self, api, args):
        secret = SecretManager().get_secret()

        response = api.get("/api/v1/mdbping", { "secret": secret })
        if response.status_code != HTTP_RESPONSE_OK:
            raise PingException()

