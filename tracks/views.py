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
from django.db.models import Q
from waypoints.models import Waypoint
from tracks.models import Track
from photos.models import Photo
from groups.models import Group


###tracks (+ waypoints, lines, etc.)
##main view
class TrackView(View):

    template_name = "tracks/track.html"

    def get(self, request, *args, **kwargs):

        logger.info("TrackView")
        import time
        start = time.time()

        track_id = kwargs.get("track_id", None)
        track=Track.all_objects.get(pk=track_id)
        every=track.get_every()

        from .forms import TrackGroupForm
        form = TrackGroupForm(instance=track)

        # tracks with no date can be ordered by pk, but it is slow
        if track.beginning:
            try:
                previous_track=Track.get_previous(track)
            except:
                import traceback
                #traceback.print_exc()
                previous_track = None
            try:
                next_track = Track.get_next(track)
            except:
                next_track=None
        else:
            previous_track=None
            next_track=None

        import datetime #used in the saved json
        nan = None
        try:
            splits=eval(str(track.td.splits))
        except Exception as e:
            logger.error("Cannot get splits: %s" %e)
            print(track.td.splits)
            splits=[]
        try:
            import json
            stats_splits=json.loads(track.td.splits_stats)
        except Exception as e:
            logger.error("Cannot get stats splits: %s" %e)
            #print(track.td.splits_stats)
            stats_splits={}
        try:
            laps=eval(track.td.laps)
        except Exception as e:
            logger.error("Cannot get laps: %s" %e)
            #print (track.td.laps)
            laps=[]
        try:
            import json
            stats_laps=json.loads(track.td.laps_stats)
        except Exception as e:
            logger.error("Cannot get stats laps: %s" %e)
            #print(track.td.laps_stats)
            stats_laps={}

        #input files:
        from import_app.utils import find_files_in_dir_by_prefix
        all_input_files = find_files_in_dir_by_prefix(settings.TRACKS_DIR,track.name_wo_path_wo_ext)
        used_files=[]
        for ext in ["gpx", "kml", "kmz", "csv", "tcx"]:
            input_file = getattr(track, ext+"_file")
            if input_file:
                used_files.append(input_file)
        unused_input_files = set(all_input_files) - set(used_files)

        # cardio
        from .utils import get_cardio_colors
        cardio_colors=get_cardio_colors()["colors"]

        ## tracks same day
        if track.date:
            tracks_same_day=Track.all_objects.filter(date=track.date).exclude(pk=track.pk).exclude(date__isnull=True)
        else:
            tracks_same_day=[]


        # find rank in groups -> this could be improved
        groups_dict = {}
        from .utils import get_options
        options=get_options()
        for g in track.groups.filter(auto_update_properties=True):
            try:
                g_json=json.loads(g.properties_json)
                g_json["Tracks"]
            except:
                g.set_attributes()
                g_json=json.loads(g.properties_json)
            group_dict={}
            try:
                n_tracks_group=g.tracks.count()
                for a in g_json["Tracks"]:
                    if a["name"]==track.name_wo_path_wo_ext:
                        for k,v in a.items():
                            if k.endswith("_rank") and v:
                                for ok,ov in options.items():
                                    if "feature_rank" in ov.keys() and ov["feature_rank"]==k:
                                        name=ok
                                        if v<n_tracks_group/3:
                                            color="green"
                                        elif v>2*n_tracks_group/3:
                                            color="red"
                                        else:
                                            color="black"
                                        break
                                group_dict[name]=[v,g.pk,color]
                        groups_dict[g]=group_dict
                        break
            except Exception as e:
                track.error("Error TrackView groups: %s" %e)

        reduce_points = request.GET.get('reduce_points', 'every')

        merged_tracks = track.merged_tracks(manager="all_objects").all()

        end = time.time()
        logger.info("TrackView: %s" %(end - start))

        return render(
            request,
            self.template_name,
            {
                "track": track,
                "splits": splits,
                "stats_splits":stats_splits,
                "cardio_colors": cardio_colors,
                "stats":stats_laps,
                "laps":laps,
                "every":every,
                "groups_dict": groups_dict,
                "tracks_same_day":tracks_same_day,
                "reduce_points": reduce_points,
                "request": request.GET.urlencode(),
                "previous_track":previous_track,
                "next_track": next_track,
                "form":form,
                "merged_tracks": merged_tracks,
                "unused_input_files":unused_input_files
            },
        )
    def post(self, request, *args, **kwargs):
        from .forms import TrackGroupForm

        track_id = kwargs.get("track_id", None)
        logger.info("TrackView post %s" %track_id)
        track = get_object_or_404(Track.all_objects, pk=track_id)
        instance = get_object_or_404(Track.all_objects, pk=track_id)
        form = TrackGroupForm(request.POST or None, instance=instance)

        old_set=set(track.groups.filter(auto_update_properties=True))
        # these are not shown in the from, I add them by hand later
        old_set_path = [g for g in track.groups.all() if g.is_path_group or g.hide_in_forms]

        old_timezone = track.time_zone
        old_starting_index = track.starting_index
        old_ending_index = track.ending_index

        if form.is_valid():
            track = form.save()

            for g in old_set_path:
                track.groups.add(g)
            track.save()

            new_timezone = track.time_zone

            if old_timezone!=new_timezone:
                old_offset = track.get_timezone_offset(timezone=old_timezone)
                new_offset = track.get_timezone_offset(timezone=new_timezone)
                track.info("OLd timezone: %s Old offset: %s New timezone: %s New Offset: %s" %(old_timezone, old_offset, new_timezone, new_offset))
                track.fix_times(offset=new_offset-old_offset, force=True)

            if old_starting_index!=track.starting_index or old_ending_index!=track.ending_index:
                track.starting_index = max(track.starting_index,0)
                track.ending_index = max(track.ending_index,0)
                track.save()
                track.set_all_properties(direct_call=True)


            new_set = set(track.groups.filter(auto_update_properties=True))

            # logger.info(new_set)
            # logger.info(old_set)

            for g in list(new_set-old_set)+list(old_set-new_set):
                import threading
                track.info("Setting attributes for group %s" %g)
                t = threading.Thread(
                    target=g.set_attributes
                )
                t.start()

            track.info("Track modified by form")

            return HttpResponseRedirect(
                reverse("track_detail", kwargs={"track_id": track_id})
            )
        else:
            return render(
                request, self.template_name, {"form": form, "has_error": True}
            )



### only track(s)
## all tracks
class TrackListGeneralView(View):

    template_name = "tracks/track_index_gen.html"

    def get(self, request, *args, **kwargs):

        logger.debug("TrackListGeneralView")
        import datetime
        from datetime import datetime, timedelta
        today=datetime.today()

        # FILTERS

        all_tracks=Track.objects.all().count()

        #by date
        from .utils import filter_tracks
        n_days=[1,7,30,120,365,9999]

        count_dict={
            d : filter_tracks({"n_days":d}).count() for d in n_days
        }

        nulldate_tracks = filter_tracks({"n_days":-1}).count()

        # by extension
        extensions=["gpx","kml","kmz","csv","tcx"]
        count_ext_dict={
            ext : filter_tracks({"extension":ext}).count() for ext in extensions
        }

        #by year
        years = set(Track.objects.values_list('year', flat=True))
        count_years_list=[
            {"year":y or "None","n_tracks": filter_tracks({"year":y or "None"}).count()}
        for y in years
        ]
        count_years_list.sort(key=lambda x:str(x["year"]) or "")

        # by country
        countries1=set(Track.objects.values_list('beg_country', flat=True))
        countries2= set(Track.objects.values_list('end_country', flat=True))
        countries=countries1.union(countries2)
        count_country_list=[
            {"c":c or "None", "n_tracks":filter_tracks({"country":c or "None"}).count()}
            for c in countries
        ]
        count_country_list.sort(key=lambda x: x["c"] or "")

        # by source
        source_options_1 =  list(Track.objects.values_list('csv_source',flat=True).distinct())
        source_options_2 =  list(Track.objects.values_list('gpx_creator',flat=True).distinct())
        source_options_3 =  list(Track.objects.values_list('tcx_creator',flat=True).distinct())
        source_options_4 =  list(Track.objects.values_list('kml_creator',flat=True).distinct())
        source_options = list(set(source_options_1 + source_options_2 + source_options_3 + source_options_4))
        source_options = [str(y) for y in source_options if y]
        source_options.sort()

        count_source_list=[
            {"c":c , "n_tracks":filter_tracks({"source":c }).count()}
            for c in source_options
        ]
        count_source_list.sort(key=lambda x: x["c"])

        #by heartbeat
        import decimal
        count_heart= filter_tracks({"heartbeat":"yes"}).count()
        count_noheart = filter_tracks({"heartbeat":"no"}).count()

        # by no coords
        import decimal
        count_wrong_coords = filter_tracks({"special_search":"wrong_coords"}).count()

        #by speed

        #by photos?

        #by waypoints?

        #duration?

        # return render(request, self.template_name, {"all_tracks":Track.objects.all().order_by('date')})

        return render(request, self.template_name, {"count_dict": count_dict,
                                                    "all_tracks":all_tracks,
                                                    "nulldate_tracks":nulldate_tracks,
                                                    "count_ext_dict": count_ext_dict,
                                                    "count_country_list":count_country_list,
                                                    "count_source_list":count_source_list,
                                                    "count_heart":count_heart,
                                                    "count_noheart":count_noheart,
                                                    "count_years_list":count_years_list,
                                                    "count_wrong_coords": count_wrong_coords
                                                    })

class TracksListView(View):

    template_name = "tracks/tracks_list.html"

    def get(self, request, *args, **kwargs):

        logger.info("TracksListView")

        from .forms import FindGroupForm, FindTracksForm


        name=request.GET.get("name","")
        n_days=request.GET.get("n_days","")
        year=request.GET.get("year","")
        extension=request.GET.get("extension","")
        country=request.GET.get("country","")
        source=request.GET.get("source","")
        q=request.GET.get("q","")
        min_date=request.GET.get("min_date","")
        max_date=request.GET.get("max_date","")
        group_pk_search=request.GET.get("group_pk_search","")
        group_form=FindGroupForm(initial={"group_pk_search":group_pk_search})
        how_many=request.GET.get("how_many","")
        lat=request.GET.get("lat","")
        lng=request.GET.get("lng","")
        dist=request.GET.get("dist","")
        time_zone = request.GET.get('time_zone', "")
        heartbeat = request.GET.get('heartbeat', "")
        frequency = request.GET.get('frequency', "")
        with_waypoints = request.GET.get('with_waypoints', False)
        with_photos = request.GET.get('with_photos', False)
        with_global = request.GET.get('with_global', False)
        deleted_tracks = request.GET.get('deleted_tracks', 0)
        by_id = request.GET.get('by_id', None)
        # duplicated_tracks = request.GET.get('duplicated_tracks',False)
        # merged_tracks = request.GET.get('merged_tracks',False)
        track_ids = request.GET.get('track_ids',None)
        exclude_excluded_groups = request.GET.get('exclude_excluded_groups', 0)#OK
        regex_name=request.GET.get('regex_name', False)#OK
        special_search=request.GET.get('special_search', None)#OK
        special_search_pk=request.GET.get('special_search_pk', None)#OK



        ## option to avoid doing any search (for page initialization)
        no_search = request.GET.get('no_search', "")
        if list(request.GET.keys())==["use_color"] or not request.GET.keys() or no_search:
            from base.utils import get_coords_from_ip
            initial_lat, initial_long, initial_address = get_coords_from_ip()
        else:
            initial_lat, initial_long, initial_address  = None, None, None

        ## General remark: "None" is to filter for objects with the given field null or empty
        ## "" is no filtering for the given field

        country_options_1 =  list(Track.objects.values_list('beg_country',flat=True).distinct())
        country_options_2 =  list(Track.objects.values_list('end_country',flat=True).distinct())
        country_options = list(set(country_options_1 + country_options_2 + ["","None"]))
        country_options = [str(y) if y else "None" for y in country_options]
        if "" not in country_options:
            country_options = [""]+country_options
        country_options.sort()

        year_options =  set(Track.objects.values_list('year',flat=True).distinct())
        year_options = [str(y) if y else "None" for y in year_options]
        year_options.sort(reverse=True)
        if "" not in year_options:
            year_options = [""]+year_options

        timezone_options =  set(Track.objects.values_list('time_zone',flat=True).distinct())
        timezone_options = [str(y) if y else "None" for y in timezone_options]
        timezone_options.sort()
        if "" not in timezone_options:
            timezone_options = [""]+timezone_options

        source_options_1 =  list(Track.objects.values_list('csv_source',flat=True).distinct())
        source_options_2 =  list(Track.objects.values_list('gpx_creator',flat=True).distinct())
        source_options_3 =  list(Track.objects.values_list('tcx_creator',flat=True).distinct())
        source_options_4 =  list(Track.objects.values_list('kml_creator',flat=True).distinct())
        source_options = list(set(source_options_1 + source_options_2 + source_options_3 + source_options_4))
        source_options = [str(y) if y else "" for y in source_options]
        if "" not in source_options:
            source_options = [""]+source_options
        source_options.sort()

        from .forms import FindTracksForm
        if track_ids:
            ids_list=[int(i) for i in track_ids.split("_")]
            track_form = FindTracksForm(initial={"tracks":ids_list})
            track_form.fields['tracks'].initial=track_ids
        else:
            track_form = FindTracksForm()


        ext_options =  ["","gpx","kml","kmz","csv","tcx"]

        if lat and lng:
            # if close to a given lat/lng, limit distance to 3km if not set
            if not how_many and not dist:
                dist=3
        if special_search=="close_to_group" or special_search=="close_to_track":
            if not how_many and not dist:
                how_many=20

        return render(request, self.template_name, { 
             "request":request.GET.urlencode(),
             "name":name,
             "n_days":n_days,
             "year":year,
             "extension":extension,
             "country":country,
             "source":source,
             "q":q,
             "min_date":min_date,
             "max_date":max_date,
             "group_pk_search":group_pk_search,
             "group_form":group_form,
             "country_options": country_options,
             "source_options":source_options,
             "how_many":how_many,
             "year_options":year_options,
             "ext_options":ext_options,
             "lat":lat,
             "lng":lng,
             "dist":dist,
             "time_zone":time_zone,
             "timezone_options":timezone_options,
             "initial_lat":initial_lat,
             "initial_long":initial_long,
             "initial_address":initial_address,
             "heartbeat":heartbeat,
             "frequency":frequency,
             "with_global":with_global,
             "with_waypoints":with_waypoints,
             "with_photos":with_photos,
             "deleted_tracks":deleted_tracks,
             "by_id":by_id,
            #  "merged_tracks":merged_tracks,
            #  "duplicated_tracks":duplicated_tracks,
             "track_form": track_form,
             "exclude_excluded_groups":exclude_excluded_groups,
             "special_search_pk":special_search_pk,
             "special_search":special_search,
             "regex_name":regex_name,
             })



class TracksMapView(View):

    template_name = "tracks/tracks_map.html"

    def get(self, request, *args, **kwargs):
        logger.debug("TracksMapView")

        # print(request.GET)
        # from .utils import filter_tracks
        # tracks=filter_tracks(request)

        return render(
            request,
            self.template_name,
            {
             "request":request.GET.urlencode()  #to be passed to get the json
            }
        )

class DeleteTracks(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages
        from .models import Group, Track, Photo

        # if on delete=set_null is not working, I do this by hand
        # for p in Photo.objects.all():
        #     p.track=None
        #     p.save()
        logger.info("deleting tracks")

        try:
            Track.objects.all().delete()
            message = "OK delete tracks"
            logger.info(message)
        except Exception as e:
            message = "KO deleting track %s" % e
            logger.error(message)

        messages.success(request, message)

        return redirect(reverse("index"))

class DeleteEmptyTracks(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages
        from .models import Group, Track, Photo

        logger.info("DeleteEmptyTracks")
        deleted_tracks = []
        for track in Track.objects.filter(n_points=0):
            if track.waypoints_all().count() == 0:
                deleted_tracks.append(track.name)
                track.delete()

        message = "Tracks "

        for t in deleted_tracks:
            message += str(t) + ", "
        message = message[:-2]
        message += " deleted"

        messages.success(request, message)
        logger.info(message)

        return redirect(reverse("import"))

# class SimilaritiesView(View):
#     def get(self, request, *args, **kwargs):
#         from .utils import find_similar_tracks
#         find_similar_tracks()

#         return redirect(reverse("import"))

## single track
#plots
class TrackStatisticsView(View):

    template_name = "tracks/track_plots.html"

    def get(self, request, *args, **kwargs):

        logger.debug("TrackStatisticsView")
        track_id = kwargs.get("track_id", None)
        track = get_object_or_404(Track.all_objects, pk=track_id)

        return render(
            request,
            self.template_name,
            {
                "track": track,
            },
        )

class TrackRollingView(View):
    template_name = "tracks/track_rolling.html"

    def get(self, request, *args, **kwargs):

        track_id = kwargs.get("track_id", None)
        logger.info("TrackRollingView %s" % track_id)
        track = get_object_or_404(Track.all_objects, pk=track_id)
        n_rolling_speed = request.GET.get('n_rolling_speed')
        n_rolling_alt = request.GET.get('n_rolling_alt')
        n_rolling_freq = request.GET.get('n_rolling_freq')
        n_rolling_hr = request.GET.get('n_rolling_hr')
        n_rolling_slope = request.GET.get('n_rolling_slope')
        min_n_speed = request.GET.get('min_n_speed')
        min_n_alt = request.GET.get('min_n_alt')
        min_n_freq = request.GET.get('min_n_freq')
        min_n_hr = request.GET.get('min_n_hr')
        min_n_slope = request.GET.get('min_n_slope')

        if n_rolling_speed and min_n_speed:
            track.n_rolling_speed = n_rolling_speed
            track.min_n_speed = min(int(min_n_speed), int(n_rolling_speed))
        if n_rolling_alt and min_n_alt:
            track.n_rolling_alt = n_rolling_alt
            track.min_n_alt = min(int(min_n_alt), int(n_rolling_alt))
        if n_rolling_freq and min_n_freq:
            track.n_rolling_freq = n_rolling_freq
            track.min_n_freq = min(int(min_n_freq), int(n_rolling_freq))
        if n_rolling_hr and min_n_hr:
            track.n_rolling_hr = n_rolling_hr
            track.min_n_hr = min(int(min_n_hr), int(n_rolling_hr))
        if n_rolling_slope and min_n_slope: #also vertical speed
            track.n_rolling_slope = n_rolling_slope
            track.min_n_slope = min(int(min_n_slope), int(n_rolling_slope))

        track.save()
        if (n_rolling_speed or n_rolling_freq or n_rolling_alt or n_rolling_hr or n_rolling_slope):
            track.rolling_quantities()
            track.set_json_LD(how="all")

        every = track.get_every()
        from tracks.models import TrackDetail
        from django.contrib.postgres.fields import ArrayField
        # for f in TrackDetail._meta.get_fields():
        #     f_name = f.name
        for f_name in track.td.array_fields_1:
            value = getattr(track.td, f_name[1:], None)
            # if isinstance(f, ArrayField):
            new_name = "td" + f_name
            if not "smooth" in f_name:
                setattr(track, new_name, value[::every])
            else:
                setattr(track, new_name, value)

        reduce_points = request.GET.get('reduce_points', 'every')

        return render(
            request,
            self.template_name,
            {
                "track": track,
                "reduce_points": reduce_points
            },
        )

class TrackSmoothView(View):

    template_name = "tracks/track_smooth.html"

    def get(self, request, *args, **kwargs):

        track_id = kwargs.get("track_id", None)
        logger.info("TrackSmoothView %s" % track_id)
        track = get_object_or_404(Track.all_objects, pk=track_id)
        wps = Waypoint.objects.filter(track__id=track_id)

        from .forms import SmoothTrackForm
        form = SmoothTrackForm()

        return render(
            request,
            self.template_name,
            {
                "track": track,
                "wps": wps,
                "form": form
                # "wps_global":wps_global
            },
        )

    def post(self, request, *args, **kwargs):
        from .forms import SmoothTrackForm
        form = SmoothTrackForm(request.POST)

        track_id = kwargs.get("track_id", None)
        logger.info("TrackSmoothView post %s" % track_id)
        track = get_object_or_404(Track.all_objects, pk=track_id)
        wps = Waypoint.objects.filter(track__id=track_id)

        if form.is_valid():
            algorithm = form.cleaned_data['algorithm']
            parameter = form.cleaned_data['parameter']
            logger.info("algorithm %s" % algorithm)
            logger.info("parameter %s" % parameter)

            # all methods modify _gpx, so I create an external copy
            import gpxpy
            from django.utils import timezone
            # _gpx = gpxpy.parse(open(track.gpx_file, "r", encoding="utf8"))
            _gpx = gpxpy.parse(track.gpx)
            original_times=[]
            original_lats = []
            original_lons = []
            for track_ in _gpx.tracks:
                for segment in track_.segments:
                    for i, point in enumerate(segment.points):
                        if hasattr(point,"time") and point.time:
                            original_times.append(point.time)
                        else:
                            use_time=False
                        original_lats.append(point.latitude)
                        original_lons.append(point.longitude)

            if (algorithm == "1"):
                _gpx.simplify(max_distance=parameter)
                logger.info("_gpx.simplify(max_distance=%s)" % parameter)
            elif (algorithm == "2"):
                _gpx.reduce_points(max_points_no=parameter)
                logger.info("_gpx.reduce_points(max_points_no=%s)" % parameter)
            elif (algorithm == "3"):
                max_n_points = int(float(parameter) * float(track.n_points))
                _gpx.reduce_points(max_points_no=max_n_points)
                logger.info("_gpx.reduce_points(max_points_no=%s)" % max_n_points)
            elif (algorithm == "4"):
                _gpx.reduce_points(min_distance=parameter)
                logger.info("_gpx.reduce_points(min_distance=%s)" % parameter)
            else:
                logger.error("no algorithm")
                raise ValueError('Cannot find algorithm number')

            lats = []
            long = []
            alts = []
            times = []
            speed = []
            for t in _gpx.tracks:
                for segment in t.segments:
                    for point in segment.points:
                        lats.append(point.latitude)
                        long.append(point.longitude)
                        alts.append(point.elevation)
                        times.append(point.time)
                        speed.append(point.speed)

            times_ok = times
            from .utils import get_sub_indices
            track.td.smooth3_indices = get_sub_indices(
                                            [(la,lo) for la,lo in zip(original_lats,original_lons)],
                                            [(la, lo) for la,lo in zip(lats, long)]
                                        )

            track.info("Setting smoothed quantities")
            track.info("Smoothed length3 %s" % len(lats))
            track.length_2d_smooth3 = _gpx.length_2d()  # m
            track.length_3d_smooth3 = _gpx.length_3d()
            track.n_points_smooth3 = len(lats)

            track.save()
            track.td.save()

            return render(request, self.template_name, {"form": form, "track": track})
        else:
            return render(request, self.template_name, {"form": form, "has_error": True})


# see sources
class TrackSourceView(View):
    def get(self, request, *args, **kwargs):
        track_id = kwargs.get("track_id", None)
        track = get_object_or_404(Track.all_objects, pk=track_id)
        logger.info("TrackSourceView %s" % track.name_wo_path_wo_ext)

        extension = kwargs.get("ext", None) #gpx, kml,kmz,csv, tcx
        raw_view = request.GET.get('raw_view', 0)
        file_path = request.GET.get('file_path', "")

        if raw_view or file_path:
            template_name = "tracks/track_source.html"
            if not file_path:
                text=getattr(track,extension) #track.gpx, track.kml etc.
            else:
                try:
                    with open(file_path , 'r',encoding="utf-8") as f:
                        text=f.read()
                except:
                    try:
                        with open(file_path , 'r') as f:
                            text=f.read()
                    except:
                        with open(file_path , 'r',encoding="latin-1") as f:
                            text=f.read()

            return render(request, template_name, {"track": track,"extension":extension,"text":text})
        else:

            template_name = "tracks/track_"+extension+".html"

            return render(request, template_name, {"track": track,"extension":extension})

#download sources
class DownloadSourceView(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages
        from tracks.models import Track
        from django.http import HttpResponse
        from wsgiref.util import FileWrapper
        import os

        track_id = kwargs.get("track_id", None)
        track = get_object_or_404(Track.all_objects, pk=track_id)
        extension = kwargs.get("ext", None)  # gpx, kml,kmz,csv, tcx
        if extension=="gpx":
            file_path = track.gpx_file
        elif extension=="kml":
            file_path = track.kml_file
        elif extension=="kmz":
            file_path = track.kmz_file
        elif extension=="csv":
            file_path = track.csv_file
        elif extension=="tcx":
            file_path = track.tcx_file
        logger.info("DownloadSourceView %s" % file_path)
        if os.path.exists(file_path):
            wrapper = FileWrapper(open(file_path, "rb"))
            response = HttpResponse(wrapper, content_type="application/force-download")
            out_filename = os.path.basename(file_path).replace(",", "_")
            response["Content-Disposition"] = "filename=" + out_filename
            logger.info(response)
            return response
        else:
            message = "Cannot find file " + file_path
            messages.success(message)
            logger.warning(message)
            return redirect(reverse("track", track_id=track_id))


#delete
class DeleteTrack(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages
        from .models import Group, Track, Photo

        track_id = kwargs.get("track_id", None)
        track = get_object_or_404(Track.all_objects, pk=track_id)
        track_name = track.name_wo_path_wo_ext
        logger.info("Delete track %s" % track_id)

        # if on delete=set_null is not working or is too slow, I do this by hand
        # if track.n_photos > 0:
        #     for p in Photo.objects.all():
        #         if p.track == track:
        #             p.track = None
        #             p.save()

        track.delete()

        message = "Track " + track_name + " deleted"

        logger.info(message)

        messages.success(request, message)

        return redirect(reverse("index"))

class DeleteTrackAndFile(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages
        from .models import Group, Track, Photo
        from .utils import delete_files

        track_id = kwargs.get("track_id", None)
        track = get_object_or_404(Track.all_objects, pk=track_id)
        track_name = track.name_wo_path_wo_ext
        logger.info("Delete track %s with files" % track_id)

        # if on delete=set_null is not working or is too slow, I do this by hand
        # if track.n_photos > 0:
        #     for p in Photo.objects.all():
        #         if p.track == track:
        #             p.track = None
        #             p.save()

        message = delete_files(track)

        track.delete()

        message += "Deleted Track " + track_name

        logger.info(message)

        messages.success(request, message)

        return redirect(reverse("track_index"))

#edit
# class EditTrackView(View):
#
#     template_name = "tracks/track_edit.html"
#
#     def get(self, request, *args, **kwargs):
#         from .forms import TrackGroupForm
#         track_id = kwargs.get("track_id", None)
#         logger.info("EditTrackView %s" %track_id)
#         track = get_object_or_404(Track, pk=track_id)
#         form = TrackGroupForm(instance=track)
#         return render(
#                 request, self.template_name, {"form": form, "track_id": track_id}
#             )
#
#     def post(self, request, *args, **kwargs):
#         from .forms import TrackGroupForm
#         from datetime import datetime
#
#         track_id = kwargs.get("track_id", None)
#         logger.info("EditTrackView post %s" %track_id)
#         track = get_object_or_404(Track, pk=track_id)
#
#         instance = get_object_or_404(Track, pk=track_id)
#         form = TrackGroupForm(request.POST or None, instance=instance)
#
#         old_set=set(track.groups.filter(auto_update_properties=True))
#
#         if form.is_valid():
#             f = form.save()
#             track_id = f.pk
#
#             new_set = set(track.groups.filter(auto_update_properties=True))
#
#             for g in list(new_set-old_set)+list(old_set-new_set):
#                 import threading
#                 t = threading.Thread(
#                     target=g.set_attributes
#                 )
#                 t.start()
#
#             track.info("Track modified by form")
#
#             return HttpResponseRedirect(
#                 reverse("track_detail", kwargs={"track_id": track_id})
#             )
#         else:
#             return render(
#                 request, self.template_name, {"form": form, "has_error": True}
#             )


## track + photos
class TrackPhotosView(View):
    template_name = "tracks/track_photos.html"

    def get(self, request, *args, **kwargs):
        track_id = kwargs.get("track_id", None)
        logger.debug("TrackPhotosView %s" %track_id)
        track = get_object_or_404(Track.all_objects, pk=track_id)
        #photos = Photo.objects.filter(track__id=track_id) #.filter(track_how="time_ok")
        #photos_day = Photo.objects.filter(track__id=track_id).filter(
        #    track_how="same_date"
        #)

        return render(
            request,
            self.template_name,
            {"track": track,
             "request": request.GET.urlencode()
            },
        )


###test
class TrackPlotTestView(View):
    template_name = "tracks/track_plot_test.html"
    def get(self, request, *args, **kwargs):
        from .models import Track

        track_id = kwargs.get("track_id", None)
        track = get_object_or_404(Track.all_objects, pk=track_id)

        return render(
            request,
            self.template_name,
            {
                "track": track,
            },
        )

## autocomplete
from dal import autocomplete

class TrackAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Track.objects.all()
        # i think order is ignored
        if self.q:
            # if possbile, search over pk
            try:
                qs = qs.filter(Q(name_wo_path_wo_ext__icontains=self.q)|
                                Q(pk=self.q)).order_by("-beginning")
            except:
                qs = qs.filter(Q(name_wo_path_wo_ext__icontains=self.q)).order_by("-beginning")


        return qs

class TrackAutocompleteName(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Track.objects.all()

        if self.q:
            data = qs.filter(name_wo_path_wo_ext__icontains=self.q).order_by("-beginning").values_list('name_wo_path_wo_ext',flat=True)
            json = list(data)
            return JsonResponse(json, safe=False)


class TrackAllAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        qs = Track.all_objects.all()

        if self.q:
            try:
                qs = qs.filter(Q(name_wo_path_wo_ext__icontains=self.q)|
                                Q(pk=self.q)).order_by("-beginning")
            except:
                qs = qs.filter(Q(name_wo_path_wo_ext__icontains=self.q)).order_by("-beginning")


        return qs


###set all properties
class TrackSetAllPropertiesView(View):
    def get(self, request, *args, **kwargs):
        from .models import Track

        track_id = kwargs.get("track_id", None)
        track = get_object_or_404(Track.all_objects, pk=track_id)

        track.set_all_properties(direct_call=True)
        messages.success(request, "OK set properties")

        return HttpResponseRedirect(
            reverse("track_detail", kwargs={"track_id": track_id})
        )

class TracksSetAllPropertiesView(View):
    def get(self, request, *args, **kwargs):
        from .models import Track
        import threading
        from .utils import refresh_properties

        logger.info("TracksSetAllPropertiesView")
        t = threading.Thread(target=refresh_properties, kwargs={"tracks":Track.objects.all(),"direct_call":true})
        t.start()

        message = "Started import in a parallel thread, check logs for details"
        messages.success(request, message)

        return HttpResponseRedirect(
            reverse("import")
        )
