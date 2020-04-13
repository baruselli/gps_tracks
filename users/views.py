from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from tracks.models import *
import json
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from pprint import pprint
import logging
import traceback
logger = logging.getLogger("gps_tracks")

from .models import Profile as Profile

# Create your views here.


class CreateProfileView(View):

    template_name = "users/user_edit.html"
    from .forms import ProfileForm

    def get(self, request, *args, **kwargs):
        from .forms import ProfileForm

        user_id = kwargs.get("user_id", None)
        logger.info("CreateProfileView %s" %user_id)

        if user_id:
            user_ = Profile.objects.get(pk=user_id)
            form = ProfileForm(instance=user_)
            return render(
                request,
                self.template_name,
                {"user": user_, "user_id": user_id, "form": form},
            )
        else:
            form = ProfileForm(
                {
                }
            )
            return render(
                request, self.template_name, {"form": form, "user_id": user_id}
            )

    def post(self, request, *args, **kwargs):
        from .forms import ProfileForm
        from datetime import datetime

        user_id = kwargs.get("user_id", None)
        logger.info("CreateProfileView post %s" %user_id)

        if user_id:
            instance = get_object_or_404(Profile, pk=user_id)
            form = ProfileForm(request.POST or None, instance=instance)
            new = False
        else:
            form = ProfileForm(request.POST)
            new = True

        if form.is_valid():
            f = form.save(commit=False)
            if new:
                from django.contrib.auth.models import User
                django_user = User.objects.create_user(username = f.name,password = f.name,email = '')
                f.user=django_user
            f.save()
            user_id = f.pk
            user_name = f.name
            is_default = f.is_default

            # there_is_a_default=False
            # for u in Profile.objects.all():
            #     if u.is_default:
            #         there_is_a_default = True
            #         break
            # if not  there_is_a_default:
            #     user= Profile.objects.get(pk=user_id)
            #     user.is_default=True
            #     user.save()

            if is_default:
                for u in Profile.objects.all():
                    if u.pk!=user_id:
                        u.is_default=False
                        u.save()

            return HttpResponseRedirect(
                reverse("user_detail", kwargs={"user_id": user_id})
            )
        else:
            return render(
                request, self.template_name, {"form": form, "has_error": True}
            )


class ProfileListView(View):

    template_name = "users/user_index.html"

    def get(self, request, *args, **kwargs):
        logger.debug("ProfileListView")

        return render(
            request,
            self.template_name,
            {"all_users": Profile.objects.all()},
        )

class ProfileView(View):

    template_name = "users/user.html"

    def get(self, request, *args, **kwargs):

        user_id = kwargs.get("user_id", None)
        logger.debug("ProfileView %s" %user_id)
        user = get_object_or_404(Profile, pk=user_id)

        return render(
            request,
            self.template_name,
            {
                "user": user,
            },
        )


class DeleteProfileView(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages

        user_id = kwargs.get("user_id", None)
        logger.info("DeleteProfileView %s" %user_id)
        user = get_object_or_404(Profile, pk=user_id)
        name= user.name

        user.delete()

        message = "Profile " + name + " deleted"
        logger.info("Message")
        messages.success(request, message)

        return redirect(reverse("user_index"))

class AssignTracksProfileView(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages

        user_id = kwargs.get("user_id", None)
        logger.info("AssignTracksProfileView %s" %user_id)
        user = get_object_or_404(Profile, pk=user_id)
        name= user.name

        counter=0
        for t in Track.objects.all():
            if not t.user:
                t.user = user
                t.info("Assigned user %s" %user)
                t.save()
                counter+=1

        message = str(counter) + " free tracks assigned to user " + name

        messages.success(request, message)
        logger.info(message)

        return redirect(reverse("user_detail", args=(user_id,)))
