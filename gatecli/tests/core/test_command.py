
from gatecli.core.command import get_all_commands
from gatecli.commands.mdbinit import MDBInitCommand

def test_get_all_commands_cache ():
    commands = get_all_commands()

    assert commands is get_all_commands()
def test_get_all_commands_content ():
    commands = get_all_commands()

    assert len(commands) == 1
    assert commands[0][0] == "mdbinit"
    assert isinstance(commands[0][1], MDBInitCommand)
