from django.contrib import admin
from .models import *
# Register your models here.

class ImportStepAdmin(admin.ModelAdmin):
    list_display = ("id",'name', 'step_code', "step_type")
    list_filter = ("step_type", )

class QuickImportAdmin(admin.ModelAdmin):
    list_display = ("id",'name', 'active')
    list_filter = ("active", )

admin.site.register(ImportStep,ImportStepAdmin)
admin.site.register(QuickImport,QuickImportAdmin)