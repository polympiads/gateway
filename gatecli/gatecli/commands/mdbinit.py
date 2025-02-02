
import json
from gatecli.core.command import Command

from scapy.all import conf, get_if_hwaddr

from gatecli.core.secret import SecretManager

def find_mac_addresses ():
    default_iface = conf.iface

    return get_if_hwaddr( default_iface )

class MDBInitCommand (Command):
    def add_arguments(self, parser):
        parser.add_argument( "hostname", help = "Name of the machine for the MDB" )
    def handle(self, api, args):
        mac_address = find_mac_addresses()
        hostname    = args.hostname

        response = api.get( "/mdbinit/", { "mac": mac_address, "host": hostname } )

        valid = True
        
        try:
            content = json.loads(response.content)
        except Exception:
            print("DANGER, Could not parse the JSON from the response")
            print("  Content :", response.content)

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
                content = { "error": "Missing secret in JSON", "reason": [ f"Malformed JSON {content}"] }
        
        print("Status code :", response.status_code)
        print("ERROR :", content.get( "error", "<No 'error' in content>" ))

        print()
        print("Causes of the error :")
        for reason in content.get('reasons', [ "<No 'reasons' in content>" ]):
            print(" -", reason)
