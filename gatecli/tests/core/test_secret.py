
import pytest
from gatecli.core.secret import SecretManager
from tests.utils import uses_secret_manager

SECRET_FILE = "/app/gatecli/gatecli/secret.txt"

@uses_secret_manager
def test_secret_file ():
    manager = SecretManager()

    assert manager.secret_file == SECRET_FILE
@uses_secret_manager
def test_no_secret ():
    manager = SecretManager()

    with pytest.raises( ValueError, match="No secret found." ):
        manager.get_secret()
@uses_secret_manager
def test_set_secret ():
    manager = SecretManager()
    manager.set_secret("SECRET")

    assert manager.get_secret() == "SECRET"

    with open(SECRET_FILE, "r") as file:
        assert file.read() == "SECRET"

@uses_secret_manager
def test_set_secret_file ():
    with open(SECRET_FILE, "w") as file:
        file.write("THENEWSECRET")
    if SecretManager.SINGLETON is not None:
        SecretManager.SINGLETON.secret = None
        SecretManager.SINGLETON.secret_file = None
        SecretManager.SINGLETON.__init__()
    manager = SecretManager()
    assert manager.get_secret() == "THENEWSECRET"
