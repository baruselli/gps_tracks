from django.db import models

class Log(models.Model):
    infos= models.TextField(verbose_name="Infos", null=True, blank=True, unique=False,default="")
    warnings= models.TextField(verbose_name="Errors", null=True, blank=True, unique=False,default="")
    errors= models.TextField(verbose_name="Errors", null=True, blank=True, unique=False,default="")

    class Meta:
        verbose_name = "Log"
        ordering = ["pk"]
        #app_label = "tracks"

    def __unicode__(self):
        return "Log" + str(self.pk)

    def __repr__(self):
        return "Log"

    def __str__(self):
        if self.track:
            return str(self.track.name_wo_path_wo_ext)
        else:
            return str(self.pk)

    def reset(self):
        self.infos = ""
        self.warnings = ""
        self.errors = ""
        self.save()

    def get_messages(self,level):
        if level=="error":
            msg_list = self.errors.split("\n")
        elif level=="warning":
            msg_list = self.warnings.split("\n")
        elif level=="info":
            msg_list = self.infos.split("\n")
        return [msg for msg in msg_list if msg]