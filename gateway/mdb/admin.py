
from django.contrib import admin

from mdb.models.machine import Machine
from mdb.models.mgroup import MachineGroup
from mdb.models.room import Room

class ReadOnlyAdmin (admin.ModelAdmin):
    def has_add_permission(self, *args, **kwargs):
        return False
    def has_delete_permission(self, *args, **kwargs):
        return False
    def has_change_permission(self, *args, **kwargs):
        return False

admin.site.register( Room, ReadOnlyAdmin )
admin.site.register( MachineGroup, ReadOnlyAdmin )
admin.site.register( Machine, ReadOnlyAdmin )
