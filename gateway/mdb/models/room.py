
from django.db import models

from gateway.rules import require_not_in_production

class Room (models.Model):
    name = models.CharField( max_length=32, unique=True, verbose_name="Room Name" )

    def save(self, *args, **kwargs):
        require_not_in_production( "Modifications to rooms are not allowed in production" )
        return super().save(*args, **kwargs)
    def delete(self, *args, **kwargs):
        require_not_in_production( "Deleting rooms is not allowed in production" )
        return super().delete(*args, **kwargs)

    def __str__(self):
        return f"<Room '{self.name}'>"
    def __repr__(self):
        return str(self)
