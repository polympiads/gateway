import datetime
import enum
import hashlib
import random
import string
from typing import Self

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from gateway.rules import require_not_in_production
from mdb.models.mgroup import MachineGroup
from mdb.models.room import Room

REGEX_MAC = r"[0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5}"
REGEX_SECRET = r"[0-9a-fA-F]{64}"


@enum.unique
class ConnectionStatus(enum.Enum):
    Connected = enum.auto()
    Unknown = enum.auto()
    Disconnected = enum.auto()

    @classmethod
    def from_time_elapsed(cls, time: datetime.timedelta) -> Self:
        assert isinstance(time, datetime.timedelta)

        if time <= settings.PING_INTERVAL + settings.PING_INTERVAL_TOLERANCE:
            return cls.Connected
        elif time <= 2 * settings.PING_INTERVAL + settings.PING_INTERVAL_TOLERANCE:
            return cls.Unknown
        else:
            return cls.Disconnected


class Machine(models.Model):
    host = models.CharField(max_length=32, unique=True, verbose_name="Host Name")
    mac = models.CharField(
        max_length=17,
        unique=True,
        verbose_name="MAC Address",
        validators=[RegexValidator(regex=REGEX_MAC, message="Enter valid MAC Address")],
    )
    secret = models.CharField(
        max_length=64,
        verbose_name="Secret",
        validators=[RegexValidator(regex=REGEX_SECRET, message="Invalid Secret")],
        null=True,
    )

    room = models.ForeignKey(Room, on_delete=models.PROTECT, verbose_name="Room")
    group = models.ForeignKey(
        MachineGroup, on_delete=models.PROTECT, verbose_name="Group"
    )

    last_ping = models.DateTimeField(verbose_name="Last ping", auto_now_add=True, blank=True)

    def allocate_secret(self):
        if self.secret:
            return

        seed = "".join([random.choice(string.ascii_letters) for _ in range(16)])

        prehash = bytes(self.host + seed, encoding="utf-8")

        self.secret = hashlib.sha256(prehash).hexdigest()

    def save(self, *args, **kwargs):
        if not self.secret:
            self.allocate_secret()
        require_not_in_production("Modifying machines is not allowed in production")
        # Machine data should always be clean
        # Even if it costs some time it is worse
        # As it should only happen when roots do commands
        # Or during initial configuration
        self.full_clean()
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        require_not_in_production("Deleting machines is not allowed in production")
        return super().delete(*args, **kwargs)

    def __str__(self):
        return f"<Machine '{self.host}' at {self.mac} in {self.room}, {self.group}>"

    def __repr__(self):
        return str(self)
    
    @property
    def netstat(self):
        return ConnectionStatus.from_time_elapsed(timezone.now() - self.last_ping)
