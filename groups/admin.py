from django.contrib import admin
from .models import *
# Register your models here.



class GroupAdmin(admin.ModelAdmin):
    readonly_fields = ("tracks",)
admin.site.register(Group, GroupAdmin)

class GroupRuleAdmin(admin.ModelAdmin):
    pass
admin.site.register(GroupRule, GroupRuleAdmin)
