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

from waypoints.models import Waypoint
from tracks.models import Track
from photos.models import Photo
from groups.models import Group
from blacklists.models import Blacklist

# Create your views here.


class BlacklistListView(View):
    template_name = "blacklists/blacklist_index.html"

    def get(self, request, *args, **kwargs):

        blacklist_objs=Blacklist.objects.all()
        context = {'blacklist_objs': blacklist_objs}

        return render(
            request,
            self.template_name,
            context
        )

class BlacklistObjView(View):

    template_name = "blacklists/blacklist_edit.html"
    from .forms import BlacklistForm

    def get(self, request, *args, **kwargs):
        from .forms import BlacklistForm

        blo_id = kwargs.get("blo_id", None)

        logger.debug("CreateBlacklistView")


        if blo_id:
            blo_ = Blacklist.objects.get(pk=blo_id)
            form = BlacklistForm(instance=blo_)
            return render(
                request,
                self.template_name,
                {"blo": blo_, "blo_id": blo_id, "form": form},
            )
        else:
            form = BlacklistForm(
                {
                    "name": "",
                    "comment":""
                }
            )
            form.created_by_hand = True
            return render(
                request, self.template_name, {"form": form, "blo_id": blo_id}
            )

    def post(self, request, *args, **kwargs):
        from .forms import BlacklistForm
        from datetime import datetime

        blo_id = kwargs.get("blo_id", None)

        if blo_id:
            instance = get_object_or_404(Blacklist, pk=blo_id)
            form = BlacklistForm(request.POST or None, instance=instance)
            new = False
            logger.info("Modify blacklist %s" %blo_id)
        else:
            form = BlacklistForm(request.POST)
            new = True
            logger.info("Create blacklist")

        if form.is_valid():
            f = form.save()
            blo_id = f.pk
            logger.info("Blacklist pk %s" %f.pk)

            # instance = get_object_or_404(Blacklist, pk=blo_id)
            # instance.save()

            return HttpResponseRedirect(
                reverse("index_blacklist")
            )
        else:
            logger.error("Form Blacklist")
            return render(
                request, self.template_name, {"form": form, "has_error": True}
            )

class DeleteBlo(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages

        blo_id = kwargs.get("blo_id", None)
        blo = get_object_or_404(Blacklist, pk=blo_id)
        blo_name = blo.file_name
        logger.info("Delete blacklist object %s" %blo_id)

        blo.delete()

        message = "Blacklisted rule " + str(blo_name) + " deleted"

        logger.info(message)

        messages.success(request, message)

        return redirect(reverse("index_blacklist"))

class DeleteTrackAndBlacklist(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages

        track_id = kwargs.get("track_id", None)
        track = get_object_or_404(Track.all_objects, pk=track_id)
        track_name = track.name_wo_path_wo_ext
        logger.info("Delete track %s with files and blacklist" %track_id)

        track.delete()

        message= "Deleted Track " + track_name

        blacklist,created=Blacklist.objects.get_or_create(file_name=track_name)
        if created:
            blacklist.file_name=track_name
            blacklist.save()
            message+=", %s blacklisted" %track_name


        logger.info(message)

        messages.success(request, message)

        #return redirect(reverse("track_index"))
        return redirect(reverse("blacklist_obj",args=(blacklist.pk,)))

class BlacklistAllFilesView(View):
    template_name = "blacklists/blacklist_all.html"
    def get(self, request, *args, **kwargs):

        result=Blacklist.all_test_files(full_report=True)

        return render(
                request, self.template_name, {"result": result}
            )
