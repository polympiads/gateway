from gatecli.core.command import Command

HTTP_RESPONSE_OK: int = 200


class PingException(Exception):
    pass


class MDBPingCommand(Command):
    def handle(self, api, _):
        response = api.get("/api/v1/mdbping", { "secret": "secret" })
        if response.status_code != HTTP_RESPONSE_OK:
            raise PingException()

