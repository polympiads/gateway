import json
from gatecli.core.command import Command, CommandError

from gatecli.core.secret import SecretManager

from opentelemetry import trace

from .. import utils

class MDBInitCommand (Command):
    def add_arguments(self, parser):
        parser.add_argument( "hostname", help = "Name of the machine for the MDB" )
    def handle(self, api, args):
        mac_address = utils.find_mac_addresses()
        hostname    = args.hostname

        span = trace.get_current_span()
        span.set_attribute("local.host", hostname)
        span.set_attribute("local.mac", mac_address)

        with trace.get_tracer_provider().get_tracer("gatecli-mdbinit-gateway") \
            .start_as_current_span( "Sending MDB Init to Gateway" ):
            response = api.get( "/mdbinit/", { "mac": mac_address, "host": hostname } )

            if response.status_code != 200:
                trace.get_current_span().set_status( trace.StatusCode.ERROR )

        valid = True
        
        try:
            content = json.loads(response.content)
        except Exception:
            print("DANGER, Could not parse the JSON from the response")
            print("  Content :", response.content)
            print()

            content = { "error": "Invalid response content", "reasons": [ "JSON Data is invalid" ] }
            valid = False

        if response.status_code == 200 and valid:
            print("Successfully created machine in MDB")

            if "secret" in content:
                secret = content["secret"]
                print(" - Secret : ", secret[:10] + ('*' * (len(secret) - 10)))
                
                try:
                    manager = SecretManager()
                    manager.set_secret( secret )
                except Exception as error:
                    print("=========================================================================")
                    print("  DANGER, Could not save the secret inside of the file")
                    print("   - The secret is ", secret)
                    print("   - Either delete the machine from the MDB or save the secret yourself")
                    print("=========================================================================")
                    raise error
                return
            else:
                content = { "error": "Missing secret in JSON", "reasons": [ f"Malformed JSON {content}"] }
        
        print("Status code :", response.status_code)
        print("ERROR :", content.get( "error", "<No 'error' in content>" ))

        print()
        print("Causes of the error :")
        for reason in content.get('reasons', [ "<No 'reasons' in content>" ]):
            print(" -", reason)

        trace.get_current_span().set_status( trace.StatusCode.ERROR )
