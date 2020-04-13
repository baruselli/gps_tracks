from django.apps import AppConfig


class BaseConfig(AppConfig):
    name = 'base'

    # def ready(self):
    #     from options.models import OptionSet
    #     if not OptionSet.objects.all():
    #         print ("Cannot find options, creating one")
    #         a = OptionSet()
    #         a.save()
    #     else:
    #         try:
    #             a = OptionSet.objects.get(is_active=True)
    #             print ("Using options %s" %a.pk)
    #         except:
    #             a = OptionSet.objects.all()[0]
    #             a.is_active = True
    #             a.save()
    #             print("Options %s made active" % a.pk)
