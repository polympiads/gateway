from gatecli.core.command import Command

HTTP_RESPONSE_OK: int = 200


class PingException(Exception):
    pass


class MDBPingCommand(Command):
    def add_arguments(self, parser):
        parser.add_argument("hostname", help="Name of the machine")
    
    def handle(self, api, args):
        response = api.get("/api/v1/mdbping", { "secret": "secret" })
        if response.status_code != HTTP_RESPONSE_OK:
            raise PingException()

