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
from .models import Line

class CreateLineView(View):
    template_name = "lines/line_edit.html"

    def get(self, request, *args, **kwargs):
        from .forms import LineForm

        # set center of map
        try:
            logger.debug("CreateLineView")
            location_name = request.GET.get("search", "")
            logger.info(location_name)
            if location_name != "":
                from geopy import geocoders
                from geopy.geocoders import Nominatim
                geolocator = Nominatim(user_agent="gps_tracks")
                location = geolocator.geocode(location_name)
                logger.info(location.raw)
                lat = location.raw["lat"]
                long = location.raw["lon"]
            else:
                import urllib.request, json
                external_ip = json.load(urllib.request.urlopen("http://ipinfo.io/json"))
                lat, long = external_ip["loc"].split(",")
                address = external_ip["city"] + ", " + external_ip["region"] + ", " + external_ip["country"]
        except:
            lat, long = 0, 0
        logger.info("%s %s" % (lat, long))

        # get line
        line_id = kwargs.get("line_id", None)

        lats_text = request.GET.get("lats", "")
        long_text = request.GET.get("lngs", "")
        alts_text = request.GET.get("alts", "")
        logger.debug("%s %s" % (lats_text, long_text))

        if line_id:
            logger.info("Line %s" % line_id)
            line_ = Line.objects.get(pk=line_id)
            form = LineForm(instance=line_)
            return render(
                request,
                self.template_name,
                {"line": line_, "line_id": line_id, "form": form},
            )
        else:
            logger.info("No line")
            form = LineForm(
                {
                    "lats_text": lats_text,
                    "long_text": long_text,
                    "alts_text": alts_text,
                    # "name": "Line starting at (%s,%s)" % (str(lats[0]), str(long[0])),
                    "name": "Line"
                }
            )
            return render(
                request, self.template_name, {"form": form, "line_id": line_id, "lat": lat, "long": long}
            )

    def post(self, request, *args, **kwargs):
        from .forms import LineForm
        from datetime import datetime

        line_id = kwargs.get("line_id", None)
        logger.info("CreateLineView %s" % line_id)

        if line_id:
            instance = get_object_or_404(Line, pk=line_id)
            form = LineForm(request.POST or None, instance=instance)
            new = False
        else:
            form = LineForm(request.POST)
            new = True

        if form.is_valid():
            f = form.save()
            line_id = f.pk

            line = Line.objects.get(pk=line_id)
            if new:
                line.time = datetime.now()

            # set colors from type
            colors = {"path": "brown",
                      "canal": "blue",
                      "border": "yellow",
                      "river": "blue",
                      "other": "grey"}
            try:
                line.color = colors[line.line_type]
            except:
                line.color = "grey"

            logger.info("Line color %s" % line.color)

            lats_list = eval("[" + line.lats_text + "]")
            long_list = eval("[" + line.long_text + "]")
            alts_list = eval("[" + line.alts_text + "]")
            line.n_points = len(lats_list)
            if line.closed and line.n_points > 2:
                lats_list.append(lats_list[0])
                long_list.append(long_list[0])
                alts_list.append(alts_list[0])
            line.lats = lats_list
            line.long = long_list
            line.alts = alts_list

            # compute distances
            if line.n_points > 1:
                import geopy.distance
                dists = []
                dist = 0
                for n in range(0, len(lats_list) - 1):
                    logger.info(n)
                    new_dist = geopy.distance.vincenty(
                        [lats_list[n], long_list[n]], [lats_list[n + 1], long_list[n + 1]]
                    ).km
                    dists.append(new_dist)
                    dist += new_dist
                line.lengths = dists
                line.total_length = dist

            line.save()

            return HttpResponseRedirect(
                reverse("line_detail", kwargs={"line_id": line_id})
            )
        else:
            return render(
                request, self.template_name, {"form": form, "has_error": True}
            )


class LineView(View):
    template_name = "lines/line.html"

    def get(self, request, *args, **kwargs):
        line_id = kwargs.get("line_id", None)
        line = get_object_or_404(Line, pk=line_id)

        logger.debug("LineView %s" % line.pk)

        return render(
            request,
            self.template_name,
            {
                "line": line,
                # "track": track,
                # "geom":json.dumps(waypoint.geom),
                # "tracks":tracks,
                # "ids":ids
            },
        )


class LineListView(View):
    template_name = "lines/line_index.html"

    def get(self, request, *args, **kwargs):
        logger.debug("LineListView")
        return render(
            request,
            self.template_name,
            {"all_lines": Line.objects.all()},
        )


class DeleteLinesView(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages

        logger.info("DeleteLinesView")
        Line.objects.all().delete()

        message = "OK delete lines"
        logger.info(message)
        messages.success(request, message)

        return redirect(reverse("line_index"))


class DeleteLineView(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages

        line_id = kwargs.get("line_id", None)
        logger.info("DeleteLineView %s" % line_id)
        line = get_object_or_404(Line, pk=line_id)
        line_name = line.name

        line.delete()

        message = "Line " + line_name + " deleted"

        messages.success(request, message)

        logger.info(message)
        return redirect(reverse("line_index"))


class AllLinesView(View):
    template_name = "lines/line_all.html"

    def get(self, request, *args, **kwargs):
        logger.debug("AllLinesView")
        return render(
            request,
            self.template_name,
            {
                "all_lines": Line.objects.all(),
            },
        )



class TrackToLineView(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages
        from tracks.models import Track
        from .models import Line
        from .utils import create_line

        track_id = kwargs.get("track_id", None)

        track = get_object_or_404(Track.all_objects, pk=track_id)
        logger.info("TrackToLineView %s" % track.pk)

        smoothed_arrays=track.get_arrays_smooth3()
        lats_smooth3=smoothed_arrays["lats_smooth3"]
        long_smooth3=smoothed_arrays["long_smooth3"]
        alts_smooth3=smoothed_arrays["alts_smooth3"]

        line, created = create_line(lats_smooth3, long_smooth3, alts_smooth3,track.name_wo_path_wo_ext)
        line.line_type = "path"
        line.track = track
        line.save()

        return redirect(reverse("line_detail", args=(line.pk,)))

