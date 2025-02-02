
import subprocess
import time

def reset_server_db (func):
    def wrapper (*args, **kwargs):
        subprocess.run([ "bash", "/app/resetdb.sh" ])
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

            proc.kill()
            proc.terminate()
            return res
        wrapper.__qualname__ = func.__qualname__
        wrapper.__name__     = func.__name__
        return wrapper
    return decorator
def using_runserver (func):
    return using_command("bash", "/app/manage.sh", "runserver")(func)
