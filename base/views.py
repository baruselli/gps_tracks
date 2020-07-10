from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.contrib import messages
import logging
logger = logging.getLogger("gps_tracks")

from waypoints.models import Waypoint
from tracks.models import Track
from photos.models import Photo
from groups.models import Group
from lines.models import Line
from geojson_obj.models import GeoJsonObject
from users.models import User
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect

###tracks, photos, groups
class MenuView(View):

    template_name = "base/index.html"

    def get(self, request, *args, **kwargs):

        #print(request.user)
        logger.info("MenuView")

        from .forms import TrackSearchForm,GroupSearchForm
        track_form=TrackSearchForm()
        group_form=GroupSearchForm()

        tracks =  Track.objects.exclude(date__isnull=True).order_by("-date")[:7]
        waypoints = Waypoint.objects.exclude(time__isnull=True).exclude(auto_generated=True).order_by("-time")[:5]
        photos = Photo.objects.exclude(time__isnull=True).order_by("-time")[:8]
        groups = Group.objects.exclude(modified__isnull=True).exclude(is_path_group=True).order_by("-modified")[:5]

        from timeline.utils import get_tracks_n_years_ago
        year_track_dates=[]
        for n_year in range(1,10):
            dict_ytd=get_tracks_n_years_ago(n_years=n_year,n_days=3,just_one=True)
            dict_ytd["n_year"]=n_year
            year_track_dates.append(dict_ytd)
            dict_ytd["min_date"]=min(dict_ytd["dates"]).strftime("%Y-%m-%d")
            dict_ytd["max_date"]=max(dict_ytd["dates"]).strftime("%Y-%m-%d")

        return render(
            request,
            self.template_name,
            {"tracks": tracks, "waypoints": waypoints, "photos": photos,"groups":groups,
            "track_form":track_form,
            "group_form":group_form,
            "year_track_dates":year_track_dates
            },
        )
    
    def post(self, request, *args, **kwargs):

        # track choice
        if ("track_form" in request.POST):
            track_ids = request.POST.getlist("track",None)

            # one track redirect to its page
            if len(track_ids)==1:
                track_id=track_ids[0]
                return redirect(reverse("track_detail", kwargs={"track_id": int(track_id)}))
            # many tracks: redirect to many tracks view
            elif len(track_ids)>1:
                track_ids_string="_".join(track_ids)
                import urllib.parse
                url = reverse("many_tracks")
                params = urllib.parse.urlencode({
                    "track_ids":track_ids_string, 
                    "reduce_points":"every",
                    "every":"0",
                    "do_plots":"0"
                })
                return HttpResponseRedirect(url + "?%s" % params)
            else:
                return redirect(reverse("index"))
        # group choice
        elif ("group_form" in request.POST):
            group_id = request.POST.get("group",None)
            if group_id:
                return redirect(reverse("group_detail", kwargs={"group_id": int(group_id)}))
            else:
                return redirect(reverse("index"))
        # shouldn't happen
        else:
            return redirect(reverse("index"))


class EmptyMap(View):

    template_name = "base/emptymap.html"

    def get(self, request, *args, **kwargs):
        logger.debug("EmptyMap")
        location_name = request.GET.get('location_name', "")
        if location_name:
            from geopy import geocoders
            from geopy.geocoders import Nominatim
            geolocator = Nominatim(user_agent="gps_tracks")
            location = geolocator.geocode(location_name)
            try:
                logger.info(location.raw)
                lat = location.raw["lat"]
                long = location.raw["lon"]
                min_lat, max_lat, min_long, max_long = location.raw["boundingbox"]
                address = location.address
            except:
                min_lat, max_lat, min_long, max_long = None, None, None, None
                import urllib.request, json
                external_ip = json.load(urllib.request.urlopen("http://ipinfo.io/json"))
                logger.info(external_ip)
                lat, long = external_ip["loc"].split(",")
                address = external_ip["city"] + ", " + external_ip["region"] + ", " + external_ip["country"]
                message = "Cannot find location!"
                logger.info(message)
                messages.success(request, message)
        else:
            min_lat=max_lat=min_long=max_long=None
            try:
                from .utils import get_coords_from_ip
                lat, long , address= get_coords_from_ip(cached=False)
            except:
                lat, long , address= 0,0,""

        return render(request, self.template_name, {
            "lat": lat, "long": long, "address": address,
            "min_lat": min_lat, "max_lat": max_lat,"min_long": min_long, "max_long": max_long,
            "location_name":location_name})

class Statistics(View):
    template_name = "base/statistics.html"

    def get(self, request, *args, **kwargs):
        from tracks.models import Track
        from django_pandas.io import read_frame

        logger.debug("Statistics")
        #tracks = Track.objects.all()
        #df = read_frame(tracks)  # read_frame(tracks)

        # results = {}
        # results["files_per_year"] = df.groupby(df.beginning.dt.year).size().to_json()
        # results["km_per_year"] = (
        #     df.groupby(df.beginning.dt.year)["length_3d"].sum().to_json()
        # )

        n_tracks = Track.objects.count()
        first_track = Track.objects.filter(beginning__isnull=False).order_by("beginning").first()
        last_track = Track.objects.filter(beginning__isnull=False).order_by("beginning").last()
        n_photos = Photo.objects.count()
        first_photo = Photo.objects.filter(time__isnull=False).order_by("time").first()
        last_photo = Photo.objects.filter(time__isnull=False).order_by("time").last()
        n_waypoints = Waypoint.objects.count()
        n_groups = Group.objects.count()
        n_lines = Line.objects.count()
        n_geojson = GeoJsonObject.objects.count()
        n_users = User.objects.count()



        # return render(request, self.template_name, {"all_tracks":Track.objects.all().order_by('date')})
        return render(
            request,
            self.template_name,
            {
                # "all_tracks":tracks,
                "n_tracks": n_tracks,
                "first_track":first_track,
                "last_track":last_track,
                "n_photos": n_photos,
                "first_photo":first_photo,
                "last_photo": last_photo,
                "n_waypoints":n_waypoints,
                "n_groups":n_groups,
                "n_lines": n_lines,
                "n_geojson": n_geojson,
                "n_users": n_users
            },
        )

###test
class TestView(View):
    def get(self, request, *args, **kwargs):

        for track in Track.objects.all():
            import numpy as np
            try:
                track.min_alt = np.min(track.td.alts)
                track.max_alt = np.max(track.td.alts)
            except:
                pass
            #if t.date:
            #    t.year=t.date.year
            track.save()
    #     print ("done")
    #         t.set_path_groups()
    #    for g in Group.objects.all():
    #        if g.name.startswith("_"):
    #            g.name="|"+g.name[1:]
    #            g.save()

        return None


# context processor
def context_base_settings(request):
    """Insert some additional information into the template context
    from the settings.
    """
    from django.conf import settings
    from options.models import OptionSet

    try:
        mapbox_token = OptionSet.get_option("MAPBOX_TOKEN")
    except:
        mapbox_token=""
    try:
        default_radius = OptionSet.get_option("DEFAULT_POINT_RADIUS")
    except:
        default_radius=10
    try:
        options_pk = OptionSet.objects.get(is_active=True).pk
    except:
        options_pk = -1
    try:
        basemaps = OptionSet.get_option("BASEMAPS")
        if basemaps:
            basemaps = eval(basemaps)
        else:
            basemaps=[]
    except Exception as e:
        import traceback

        traceback.print_exc()
        logger.error("Cannot get basemaps from options: %s" %e)
        basemaps = []
    try:
        basemaps_mapbox = OptionSet.get_option("BASEMAPS_MAPBOX")
        if basemaps_mapbox:
            basemaps_mapbox=basemaps_mapbox.split(",")
        else:
            basemaps_mapbox=None
    except Exception as e:
        logger.error("Cannot get basemaps_mapbox from options: %s" %e)
        basemaps_mapbox = []

    show_todo=settings.SHOW_TODO
    show_google_maps=int(settings.SHOW_GOOGLE_MAPS)

    additions = {
        'mapbox_token': mapbox_token,
        "options_pk": options_pk,
        "default_radius": default_radius,
        "basemaps": basemaps,
        "basemaps_mapbox":basemaps_mapbox,
        "show_todo":show_todo,
        "show_google_maps":show_google_maps
    }
    return additions

# class PointView(View):

#     template_name = "base/point.html"

#     def get(self, request, *args, **kwargs):

#         from geopy.geocoders import Nominatim
#         geolocator = Nominatim(user_agent="gps_tracks")
#         lat = float(request.GET.get("lat", 0))
#         long = float(request.GET.get("lng", 0))
#         dist = float(request.GET.get("dist", 10))
#         logger.info("PointView %s %s" %(lat,long))

#         try:
#             location = geolocator.reverse([lat, long])
#         except:
#             location = "Service not available"
#         return render(
#             request,
#             self.template_name,
#             {
#                 "lat": lat,
#                 "long": long,
#                 "distance": dist,
#                 "location": location,
#                 "request": request.GET.urlencode(),
#             },
#         )

###test
class Todo(View):
    template_name = "base/todo.html"
    def get(self, request, *args, **kwargs):



        return render(
            request,
            self.template_name,
        )