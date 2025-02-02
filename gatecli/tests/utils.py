
from io import StringIO
import os
import signal
import sys
import subprocess
import time

from gatecli.core.secret import SecretManager

class capture_stdouterr:
    def __enter__ (self, *args, **kwargs):
        self.stdout_copy = sys.stdout
        self.stderr_copy = sys.stderr

        self.stdout = sys.stdout = StringIO()
        self.stderr = sys.stderr = StringIO()

        return self
    def __exit__ (self, *args, **kwargs):
        sys.stdout = self.stdout_copy
        sys.stderr = self.stderr_copy

        del self.stdout_copy
        del self.stderr_copy
        return self

def reset_server_db (func):
    def wrapper (*args, **kwargs):
        subprocess.run([ "bash", "/app/resetdb.sh" ])
        return func(*args, **kwargs)
    wrapper.__qualname__ = func.__qualname__
    wrapper.__name__     = func.__name__
    return wrapper
def uses_secret_manager (func):
    def wrapper (*args, **kwargs):
        tests_dir = os.path.dirname(__file__)
        gtcli_dir = os.path.dirname(tests_dir)

        secret = os.path.join( gtcli_dir, os.path.join( "gatecli", "secret.txt" ) )
        if os.path.exists(secret):
            os.remove( secret )

        if SecretManager.SINGLETON is not None:
            SecretManager.SINGLETON.secret = None
            SecretManager.SINGLETON.secret_file = None
            SecretManager.SINGLETON.__init__()
        
        return func(*args, **kwargs)
    wrapper.__qualname__ = func.__qualname__
    wrapper.__name__     = func.__name__
    return wrapper
def using_command (*cmd):
    def decorator (func):
        def wrapper (*args, **kwargs):
            proc = subprocess.Popen( cmd )
            time.sleep(1)

            res = func(*args, **kwargs)

            proc.send_signal( signal.SIGINT )
            proc.send_signal( signal.SIGINT )
            time.sleep(1)
            proc.kill()
            proc.terminate()
            proc.wait()
            return res
        wrapper.__qualname__ = func.__qualname__
        wrapper.__name__     = func.__name__
        return wrapper
    return decorator
def using_runserver (func):
    return using_command("bash", "/app/manage.sh", "runserver")(func)
