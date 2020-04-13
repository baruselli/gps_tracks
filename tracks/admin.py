from django.contrib import admin

from .models import *

class TrackAdmin(admin.ModelAdmin):
    list_display = ("id", 'name_wo_path_wo_ext', 'beginning', "n_points")

admin.site.register(Track,TrackAdmin)

admin.site.register(TrackDetail)




