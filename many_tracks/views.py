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
from django.shortcuts import render

# Create your views here.

class ManyTracksView(View):

    template_name = "many_tracks/manytracks.html"

    def get(self, request, *args, **kwargs):
        track_ids = request.GET.get('track_ids', None)
        try:
            every = int(request.GET.get('every', 0))
        except:
            every =0
        use_points = int(request.GET.get('use_points', 1))
        reduce_points = request.GET.get('reduce_points', "smooth2")
        do_plots = int(request.GET.get('do_plots', 0))
        with_photos = int(request.GET.get('with_photos', 0))
        with_waypoints = int(request.GET.get('with_waypoints', 0))
        with_global = int(request.GET.get('with_global', 0))
        
        tracks= request.GET.getlist('tracks', [])


        from .forms import FindTracksForm

        ids_list=[int(i) for i in track_ids.split("_")]
#        print(ids_list)

        form = FindTracksForm(initial={"tracks":ids_list})
        form.fields['tracks'].initial=ids_list
        # print(form.fields['tracks'].initial)
        #form.fields['institution'].initial 

        return render(
            request,
            self.template_name,
            {
                "request":request.GET.urlencode(),
                "track_ids": track_ids,
                "do_plots": do_plots,
                "use_points":use_points,
                "every":every,
                "reduce_points":reduce_points,
                "with_photos": with_photos,
                "with_waypoints":with_waypoints,
                "with_global":with_global,
                "form":form
            },
        )

class ManyTracksPlotsView(View):

    template_name = "many_tracks/manytracks_plot.html"

    def get(self, request, *args, **kwargs):
        track_ids = request.GET.get('track_ids',None)
        from tracks.utils import get_options
        options=get_options()

        return render(
            request,
            self.template_name,
            {
                "track_ids":track_ids,
                "options":options
            },
        )

class ManyTracksAltsView(View):

    template_name = "many_tracks/manytracks_alts.html"

    def get(self, request, *args, **kwargs):
        track_ids = request.GET.get('track_ids', None)

        return render(
            request,
            self.template_name,
            {
                "request":request.GET.urlencode(),
                "track_ids": track_ids,
            },
        )

class DeleteManyTracksView(View):
    def get(self, request, *args, **kwargs):

        track_ids_string = request.GET.get("track_ids", "")

        logger.debug("DeleteManyTracksView %s" %track_ids_string)
        string_list = track_ids_string.split("_")
        track_ids = [int(s) for s in string_list]

        tracks = []
        track_names_string = ""
        for track_id in track_ids:
            track = get_object_or_404(Track.all_objects, pk=track_id)
            tracks.append(track)
            track_name = track.name_wo_path_wo_ext
            track_names_string += track_name + ", "

        # if on delete=set_null is not working, I do this by hand
        # total_photos = 0
        # for tr in tracks:
        #     total_photos += tr.n_photos
        # logger.info("total_photos", total_photos)

        # if total_photos > 0:
        #     for p in Photo.objects.all():
        #         if p.track in tracks:
        #             p.track = None
        #             p.save()

        for track in tracks:
            track_name=track.name_wo_path_wo_ext
            track.delete()
            logger.info("Track %s deleted" %track_name)

        message = "Tracks " + track_names_string + "deleted"

        messages.success(request, message)

        return redirect(reverse("index"))

class ManyTracksMergeView(View):

    def get(self, request, *args, **kwargs):

        track_ids_string = request.GET.get("track_ids", "")

        string_list = track_ids_string.split("_")
        track_ids = [int(s) for s in string_list]

        from merge_tracks.models import MergedTrack
        new_merged_track=MergedTrack(name="_".join([str(a) for a in track_ids]))
        try:
            new_merged_track.save()
        except:
            from datetime import datetime
            now = datetime.now()  # current date and time
            new_merged_track.name+=now.strftime("%Y%m%d_%H:%M:%S")
            new_merged_track.save()
        for i,track_id in enumerate(track_ids):
            track = get_object_or_404(Track.all_objects, pk=track_id)
            new_merged_track.input_tracks.add(track)

        return redirect(reverse("edit_merged_track",  kwargs={'id': new_merged_track.pk}))

class ManyTracksGroupView(View):

    def get(self, request, *args, **kwargs):
        track_ids_string = request.GET.get("track_ids", "")

        string_list = track_ids_string.split("_")
        logger.info("ManyTracksGroupView %s" %string_list)
        track_ids = [int(s) for s in string_list]

        from datetime import datetime
        now=datetime.now().strftime("%Y%m%d%H%MS")
        new_group = Group()
        new_group.name="Group "+ now
        new_group.save()
        for track_id in track_ids:
            track = get_object_or_404(Track.all_objects, pk=track_id)
            new_group.tracks.add(track)

        new_group.save()

        return redirect(reverse("edit_group", kwargs={"group_id":new_group.pk, "form":"quick"}))