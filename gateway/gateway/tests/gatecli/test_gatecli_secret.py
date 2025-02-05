
from django.test import TestCase

from gatecli.core.secret import SecretManager
from gateway.tests.utils import get_secret_file, using_secret_manager

SECRET_FILE = get_secret_file()

class GateCLISecretTestCase (TestCase):
    @using_secret_manager
    def test_secret_file (self):
        manager = SecretManager()

        assert manager.secret_file == SECRET_FILE
    @using_secret_manager
    def test_no_secret (self):
        manager = SecretManager()

        with self.assertRaisesMessage( ValueError, "No secret found." ):
            manager.get_secret()
    @using_secret_manager
    def test_set_secret (self):
        manager = SecretManager()
        manager.set_secret("SECRET")

        assert manager.get_secret() == "SECRET"

        with open(SECRET_FILE, "r") as file:
            assert file.read() == "SECRET"
    @using_secret_manager
    def test_set_secret_file (self):
        with open(SECRET_FILE, "w") as file:
            file.write("THENEWSECRET")
        if SecretManager.SINGLETON is not None:
            SecretManager.SINGLETON.secret = None
            SecretManager.SINGLETON.secret_file = None
            SecretManager.SINGLETON.__init__()
        manager = SecretManager()
        assert manager.get_secret() == "THENEWSECRET"
