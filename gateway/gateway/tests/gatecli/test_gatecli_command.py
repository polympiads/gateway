
from django.test import TestCase
from gatecli.core.command import get_all_commands

class GateCLICommandTestCase (TestCase):
    def test_get_all_commands_cache (self):
        commands = get_all_commands()

        assert commands is get_all_commands()
