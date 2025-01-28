
from django.db import models

from gateway.rules import require_not_in_production

class MachineGroup (models.Model):
    name = models.CharField( max_length=32, unique=True, verbose_name="Group Name" )

    def save(self, *args, **kwargs):
        require_not_in_production( "Modifications to machine groups are not allowed in production" )
        return super().save(*args, **kwargs)
    def delete(self, *args, **kwargs):
        require_not_in_production( "Deleting machine groups is not allowed in production" )
        return super().delete(*args, **kwargs)

    def __str__(self):
        return f"<Machine Group '{self.name}'>"
    def __repr__(self):
        return str(self)
