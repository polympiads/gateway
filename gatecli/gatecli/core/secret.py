
import os


class SecretManager:
    SINGLETON : "SecretManager | None" = None

    secret_file : "str | None" = None
    secret      : "str | None" = None

    def __new__(cls):
        if  SecretManager.SINGLETON is None:
            SecretManager.SINGLETON = super().__new__(cls)
        return SecretManager.SINGLETON
    def __init__(self):
        self.secret_file = os.path.join( os.path.dirname( os.path.dirname(__file__) ), "secret.txt" )

        if os.path.exists(self.secret_file):
            with open( self.secret_file, "r" ) as file:
                self.secret = file.read()

    def get_secret (self) -> str:
        if self.secret is None:
            raise ValueError("No secret found.")
        return self.secret
    def set_secret (self, value: str):
        self.secret = value
        with open( self.secret_file, "w" ) as file:
            file.write(value)
