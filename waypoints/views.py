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

from .models import Waypoint

class WaypointView(View):

    template_name = "waypoints/waypoint.html"

    def get(self, request, *args, **kwargs):

        waypoint_id = kwargs.get("waypoint_id", None)
        logger.info("WaypointView %s" % waypoint_id)
        waypoint = get_object_or_404(Waypoint, pk=waypoint_id)
        track = waypoint.track
        from .forms import WaypointForm
        form = WaypointForm(instance=waypoint)


        # tracks= find_near_tracks(waypoint,1)

        # ids=""
        # for t in tracks:
        #     ids+=str(t.pk)+"_"
        # if(len(ids))>0:
        #     ids=ids[:-1]    #removes last underscore

        # print (ids)

        return render(
            request,
            self.template_name,
            {
                "waypoint": waypoint,
                "track": track,
                "form":form
                # "geom":json.dumps(waypoint.geom),
                # "tracks":tracks,
                # "ids":ids
            },
        )

    def post(self, request, *args, **kwargs):
        from .forms import WaypointForm
        from datetime import datetime

        waypoint_id = kwargs.get("waypoint_id", None)
        instance = get_object_or_404(Waypoint, pk=waypoint_id)
        form = WaypointForm(request.POST or None, instance=instance)

        if form.is_valid():
            f = form.save()

            return HttpResponseRedirect(
                reverse("waypoint_detail", kwargs={"waypoint_id": waypoint_id})
            )
        else:
            logger.error("Form Waypoint")
            return render(
                request, self.template_name, {"form": form, "has_error": True}
            )

class AllWaypointsView(View):

    template_name = "waypoints/waypoint_map.html"

    def get(self, request, *args, **kwargs):

        logger.debug("AllWaypointsView")

        from .forms import FindGroupForm, FindTracksForm, FindWaypointsForm

        name=request.GET.get("name","")
        n_days=request.GET.get("n_days","")
        year=request.GET.get("year","")
        country=request.GET.get("country","")
        q=request.GET.get("q","")
        min_date=request.GET.get("min_date","")
        max_date=request.GET.get("max_date","")
        group_pk=request.GET.get("group_pk","")
        group_form=FindGroupForm(initial={"group_pk":group_pk})
        how_many=request.GET.get("how_many","")
        lat=request.GET.get("lat","")
        lng=request.GET.get("lng","")
        dist=request.GET.get("dist","")
        time_zone = request.GET.get('time_zone', "")
        by_id = request.GET.get('by_id', None)
        address = request.GET.get('address', "")
        track_ids = request.GET.get('track_ids', None)
        wps_ids = request.GET.get('wps_ids', None)


        ## option to avoid doing any search (for page initialization)
        no_search = request.GET.get('no_search', "")

        ## General remark: "None" is to filter for objects with the given field null or empty
        ## "" is no filtering for the given field

        country_options =  list(set(Waypoint.objects.values_list('country',flat=True).distinct()))
        country_options = list(set([str(y) if y else "None" for y in country_options]))
        country_options.sort()
        if "" not in country_options:
            country_options = [""]+country_options

        year_options =  set(Waypoint.objects.values_list('time__year',flat=True).distinct())
        year_options = [str(y) if y else "None" for y in year_options]
        year_options.sort(reverse=True)
        if "" not in year_options:
            year_options = [""]+year_options

        timezone_options =  set(Waypoint.objects.values_list('time_zone',flat=True).distinct())
        timezone_options = [str(y) if y else "None" for y in timezone_options]
        timezone_options.sort()
        if "" not in timezone_options:
            timezone_options = [""]+timezone_options

        if lat and lng and not dist:
            dist=3

        from .forms import FindTracksForm
        if track_ids:
            ids_list=[int(i) for i in track_ids.split("_")]
            track_form = FindTracksForm(initial={"tracks":ids_list})
            track_form.fields['tracks'].initial=ids_list
        else:
            track_form = FindTracksForm()

        from .forms import FindWaypointsForm
        if wps_ids:
            ids_list=[int(i) for i in wps_ids.split("_")]
            wps_form = FindWaypointsForm(initial={"waypoints":ids_list})
            wps_form.fields['waypoints'].initial=ids_list
        else:
            wps_form = FindWaypointsForm()


        return render(
            request,
            self.template_name,
            {
             "request":request.GET.urlencode(),
             "name":name,
             "n_days":n_days,
             "year":year,
             "country":country,
             "q":q,
             "min_date":min_date,
             "max_date":max_date,
             "group_pk":group_pk,
             "group_form":group_form,
             "country_options": country_options,
             "how_many":how_many,
             "year_options":year_options,
             "lat":lat,
             "lng":lng,
             "dist":dist,
             "time_zone":time_zone,
             "timezone_options":timezone_options,
             "by_id":by_id,
             "address":address,
             "track_form":track_form,
             "wps_form":wps_form,
             "wps_ids":wps_ids
             },
        )


class WaypointListView(View):

    template_name = "waypoints/waypoint_index.html"

    def get(self, request, *args, **kwargs):

        logger.debug("WaypointListView")

        return render(
            request,
            self.template_name,
            {
            # "all_wps": Waypoint.objects.filter(inizio=False),
             "request": request.GET.urlencode()},
        )

class DeleteWaypoints(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages
        from .models import Waypoint

        Waypoint.objects.all().delete()

        message = "OK delete waypoints"

        logger.info(message)

        messages.success(request, message)

        return redirect(reverse("waypoint_index"))

class CreateWaypointView(View):

    template_name = "waypoints/waypoint_edit.html"

    def get(self, request, *args, **kwargs):
        from .forms import WaypointForm

        waypoint_id = kwargs.get("waypoint_id", None)

        formclass = WaypointForm

        lat = float(request.GET.get("lat", 0))
        long = float(request.GET.get("lng", 0))
        track_pk = float(request.GET.get("track_pk", 0))
        alt = 0

        logger.debug("CreateWaypointView %s %s" %(lat,long))

        if not track_pk==-1:
            try:
                track=Track.all_objects.get(pk=track_pk)
            except:
                track=None
        else:
            track=None

        if waypoint_id:
            waypoint_ = Waypoint.objects.get(pk=waypoint_id)
            form = formclass(instance=waypoint_)
            return render(
                request,
                self.template_name,
                {"waypoint": waypoint_, "waypoint_id": waypoint_id, "form": form,  "track":track},
            )
        else:
            form = formclass(
                {
                    "lat": lat,
                    "long": long,
                    "alt": alt,
                    "name": "waypoint at (%s,%s)" % (str(lat), str(long)),
                    "track":track
                }
            )
            form.created_by_hand = True
            form.track=track
            return render(
                request, self.template_name, {"form": form, "waypoint_id": waypoint_id, "track":track}
            )

    def post(self, request, *args, **kwargs):
        from .forms import WaypointForm
        from datetime import datetime

        waypoint_id = kwargs.get("waypoint_id", None)
        formclass = WaypointForm


        track_pk = float(request.GET.get("track_pk", 0))
        if not track_pk==-1:
            try:
                track=Track.all_objects.get(pk=track_pk)
            except:
                track=None
        else:
            track=None

        if waypoint_id:
            instance = get_object_or_404(Waypoint, pk=waypoint_id)
            form = formclass(request.POST or None, instance=instance)
            new = False
            logger.info("Modify waypoint %s" %waypoint_id)
        else:
            form = formclass(request.POST)
            new = True
            logger.info("Create waypoint")

        if form.is_valid():
            f = form.save()
            waypoint_id = f.pk
            logger.info("Waypoint pk %s" %f.pk)

            waypoint = Waypoint.objects.get(pk=waypoint_id)
            waypoint.track=track
            waypoint.set_timezone()

            if new:
                waypoint.created_by_hand = True
                waypoint.time = datetime.now()

            #this is made to avoid the join on track and made the loading faster
            if waypoint.track:
                waypoint.track_name = waypoint.track.name_wo_path_wo_ext
                waypoint.track_pk = waypoint.track.pk

                waypoint.save()

            return HttpResponseRedirect(
                reverse("waypoint_detail", kwargs={"waypoint_id": waypoint_id})
            )
        else:
            logger.error("Form Waypoint")
            return render(
                request, self.template_name, {"form": form, "has_error": True}
            )

class DeleteWaypointView(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages
        from .models import Waypoint

        waypoint_id = kwargs.get("waypoint_id", None)
        waypoint = get_object_or_404(Waypoint, pk=waypoint_id)
        waypoint_name = waypoint.name

        waypoint.delete()

        message = "Waypoint " + waypoint_name + " deleted"

        messages.success(request, message)

        logger.info(message)

        return redirect(reverse("waypoint_index"))



class WaypointListGeneralView(View):

    template_name = "waypoints/waypoint_index_gen.html"

    def get(self, request, *args, **kwargs):

        logger.debug("WaypointListGeneralView")
        import datetime
        from datetime import datetime, timedelta
        today=datetime.today()

        from .utils import filter_waypoints

        #by date
        n_days=[1,7,30,120,365,9999]

        count_dict={
            d : filter_waypoints({"n_days":d}).count() for d in n_days
        }

        all_waypoints=Waypoint.objects.all().count()
        nulldate_waypoints = filter_waypoints({"n_days":-1}).count()

        #by year
        times = set(Waypoint.objects.values_list('time', flat=True))
        years = set([t.year for t in times if t])
        #years = sorted(list(years))
        count_years_list=[
            {"year":y,"n_waypoints": filter_waypoints({"year":y}).count()}
        for y in years
        ]

        # by country
        countries=set(Waypoint.objects.values_list('country', flat=True))
        if "" in countries and None in countries:
            countries = countries - set([""])
        countries = list(countries)
        if None in countries:
            countries.remove(None)
            countries.append("None")
        if "" in countries:
            countries.remove("")
            countries.append("None")

        count_country_dict={
            c : filter_waypoints({"country":c}).count() for c in countries
        }

        return render(request, self.template_name, {"count_dict": count_dict,
                                                    "all_waypoints":all_waypoints,
                                                    "nulldate_waypoints":nulldate_waypoints,
                                                    "count_years_list":count_years_list,
                                                    "count_country_dict":count_country_dict
                                                    })

## autocomplete
from dal import autocomplete

class WaypointAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !

        qs = Waypoint.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q).order_by("-pk")

        return qs

                                                