## https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    max_heartrate = models.FloatField(null=True,verbose_name="Maximum Heartrate",default=190)
    is_default = models.BooleanField(default=False, verbose_name="Default User")
    name =  models.CharField(max_length=255, verbose_name="Name", null=False, blank=False,unique=True)
    modified = models.DateTimeField(auto_now=True, verbose_name="Date of modification", null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name="Date of creation", null=True, blank=True)

    # @receiver(post_save, sender=User)
    # def create_user_profile(sender, instance, created, **kwargs):
    #     if created:
    #         Profile.objects.create(user=instance,name=instance.username)

    # @receiver(post_save, sender=User)
    # def save_user_profile(sender, instance, **kwargs):
    #     instance.profile.save()

    class Meta:
        verbose_name = "Profile"
        ordering = ["pk"]
        #app_label = "tracks"

    def __unicode__(self):
        return "Profile " + str(self.name)

    def __repr__(self):
        return "Profile " + str(self.name)

    def __str__(self):
        return str(self.name)