from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
import json
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from pprint import pprint
import logging
import traceback

logger = logging.getLogger("gps_tracks")
from lines.models import Line
from waypoints.models import Waypoint

class WaypointGeopyView(View):
    def get(self, request, *args, **kwargs):
        from .utils import waypoints_geopy
        import threading

        logger.debug("WaypointGeopyView")
        t = threading.Thread(target=waypoints_geopy)
        t.start()
        keys = []

        message = "Started import in a parallel thread"
        messages.success(request, message)

        return redirect(reverse("import"))


class TrackGeopyView(View):
    def get(self, request, *args, **kwargs):
        from .utils import tracks_geopy
        import threading

        logger.info("TrackGeopyView")
        t = threading.Thread(target=tracks_geopy)
        t.start()

        message = "Started import in a parallel thread"
        messages.success(request, message)

        return redirect(reverse("import"))


class SingleTrackGeopyView(View):
    def get(self, request, *args, **kwargs):
        from .utils import track_geopy
        from tracks.models import Track

        track_id = kwargs.get("track_id", None)
        logger.info("SingleTrackGeopyView %s" %track_id)
        track = get_object_or_404(Track.all_objects, pk=track_id)
        track_geopy(track)

        message = "Done"
        messages.success(request, message)

        return redirect(reverse("track_detail", kwargs={"track_id": track_id}))


class PhotoGeopyView(View):
    def get(self, request, *args, **kwargs):
        from .utils import photos_geopy
        import threading

        logger.info("PhotoGeopyView")
        t = threading.Thread(target=photos_geopy)
        t.start()

        message = "Started import in a parallel thread"
        messages.success(request, message)

        return redirect(reverse("import"))


class SinglePhotoGeopyView(View):
    def get(self, request, *args, **kwargs):
        from .utils import photo_geopy
        from tracks.models import Photo

        photo_id = kwargs.get("photo_id", None)
        logger.info("SinglePhotoGeopyView %s" %photo_id)
        photo = get_object_or_404(Photo, pk=photo_id)
        photo_geopy(photo)

        message = "Done"
        messages.success(request, message)

        return redirect(reverse("photo_detail", kwargs={"photo_id": photo_id}))

class SingleWaypointGeopyView(View):
    def get(self, request, *args, **kwargs):
        from .utils import waypoint_geopy

        waypoint_id = kwargs.get("waypoint_id", None)
        logger.info("SingleWaypointGeopyView %s" %waypoint_id)
        waypoint = get_object_or_404(Waypoint, pk=waypoint_id)
        waypoint_geopy(waypoint)

        message = "Done"
        messages.success(request, message)

        return redirect(reverse("waypoint_detail", kwargs={"waypoint_id": waypoint_id}))


class SingleLineGeopyView(View):
    def get(self, request, *args, **kwargs):
        from .utils import line_geopy

        line_id = kwargs.get("line_id", None)
        logger.info("SingleLineGeopyView %s" %line_id)
        line = get_object_or_404(Line, pk=line_id)
        line_geopy(line)

        message = "Done"
        messages.success(request, message)

        return redirect(reverse("line_detail", kwargs={"line_id": line_id}))

class LineGeopyView(View):
    def get(self, request, *args, **kwargs):
        from .utils import lines_geopy
        import threading

        logger.info("LineGeopyView")
        t = threading.Thread(target=lines_geopy)
        t.start()
        keys = []

        message = "Started import in a parallel thread"
        messages.success(request, message)

        return redirect(reverse("import"))

class SingleTrackOwmView(View):
    def get(self, request, *args, **kwargs):
        from .utils import track_geopy
        from tracks.models import Track

        track_id = kwargs.get("track_id", None)
        logger.info("SingleTrackGeopyView %s" % track_id)
        track = get_object_or_404(Track.all_objects, pk=track_id)
        track_geopy(track)

        message = "Done"
        messages.success(request, message)

        return redirect(reverse("track_detail", kwargs={"track_id": track_id}))

class GetLineAltsView(View):
    def get(self, request, *args, **kwargs):

        line_id = kwargs.get("line_id", None)
        logger.info("GetLineAltsView %s" %line_id)
        line = get_object_or_404(Line, pk=line_id)

        from geopy_app.utils import get_altitude
        alts=[]
        for lat,lon in zip(line.lats,line.long):
            alt=get_altitude(lat,lon)
            alts.append(alt)
        line.alts=alts
        line.alts_text=str(alts)[1:-1]+"," #this is what is shown in the form , without the []
        line.save()

        return HttpResponseRedirect(
                reverse("line_detail", kwargs={"line_id": line_id})
            )