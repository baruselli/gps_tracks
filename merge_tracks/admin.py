from django.contrib import admin
from .models import *
# Register your models here.


class MergedTrackAdmin(admin.ModelAdmin):
    readonly_fields = ("input_tracks","output_track")
admin.site.register(MergedTrack, MergedTrackAdmin)


