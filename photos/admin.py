from django.contrib import admin
from .models import *
# Register your models here.


class PhotoAdmin(admin.ModelAdmin):
    list_display = ("id",'name', 'time',"modified", "created", "has_gps", "has_time")
    list_filter = ("has_gps", "has_time")
    readonly_fields=["tracks"]

admin.site.register(Photo,PhotoAdmin)