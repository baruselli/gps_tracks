from django.contrib import admin

from .models import *

class OptionSetAdmin(admin.ModelAdmin):
    list_display = ["id", "is_active"]

admin.site.register(OptionSet,OptionSetAdmin)