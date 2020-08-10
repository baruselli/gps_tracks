from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
import json
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from pprint import pprint
import logging
from groups.models import Group
from photos.models import Photo
from lines.models import Line
from geojson_obj.models import GeoJsonObject
from waypoints.models import Waypoint
import traceback
logger = logging.getLogger("gps_tracks")

from groups.models import Group
from tracks.utils import get_colors
from tracks.models import *
from waypoints.models import *
from django.core.serializers.json import DjangoJSONEncoder

###Groups
class GroupsJsonView(View):
    def get(self, request, *args, **kwargs):
        logger.info("GroupsJsonView")
        from .utils import groups_json
        json_=groups_json()

        return JsonResponse(json_,safe=False)

class GroupPlotsJsonView(View):
    def get(self, request, *args, **kwargs):

        logger.debug("GroupPlotsJsonView")
        group_id = kwargs.get("group_id", None)
        group = get_object_or_404(Group, pk=group_id)
        group.check_json()
        json_ok = group.get_properties()
        #print (json_ok.keys())
        return JsonResponse(json_ok)

class GroupStatisticsJsonView(View):
    def get(self, request, *args, **kwargs):
        logger.debug("GroupPlotsJsonView")
        group_id = kwargs.get("group_id", None)
        group = get_object_or_404(Group, pk=group_id)
        group.check_json()
        json_ok = group.get_statistics()
        return JsonResponse(json_ok)


###Waypoints
class WaypointsJsonView(View):
    def get(self, request, *args, **kwargs):
        logger.info("WaypointsJsonView")
        import time
        start = time.time()

        from .utils import waypoints_json
        from waypoints.utils import filter_waypoints

        if request.GET:
            waypoints=filter_waypoints(request.GET, silent=False)
        else:
            waypoints=Waypoint.objects.all()

        do_cluster = request.GET.get("do_cluster", True)
        if do_cluster==0 or do_cluster=="0":
            do_cluster=False

        json_ = waypoints_json(wps=waypoints,do_cluster=do_cluster)

        end = time.time()

        logger.info("WaypointsJsonView: %s" %(end-start))


        return JsonResponse(json_, safe=False)


###Photos
class PhotosJsonView(View):
    def get(self, request, *args, **kwargs):
        logger.info("PhotosJsonView")
        import time
        start = time.time()

        from .utils import photos_json
        from photos.utils import filter_photos

        if request.GET:
            photos = filter_photos(request.GET,silent=False)
        else:
            photos = Photo.objects.all()

        do_cluster = request.GET.get("do_cluster", True)
        if do_cluster == 0 or do_cluster == "0":
            do_cluster = False

        level = request.GET.get("level", 2)

        json_ = photos_json(photos=photos, do_cluster=do_cluster,level=level)

        # try:
        #     if json_ and "lat" in json_[0] and isinstance(json_[0]["lat"], list):
        #         minmaxlatlong = [min([l["lat"][0] for l in json_ if l["lat"][0]]),
        #                          max([l["lat"][0] for l in json_ if l["lat"][0]]),
        #                          min([l["long"][0] for l in json_ if l["lat"][0]]),
        #                          max([l["long"][0] for l in json_ if l["lat"][0]]), ]
        #     else:
        #         minmaxlatlong = [min([l["lat"] for l in json_ if l["lat"]]),
        #                          max([l["lat"] for l in json_ if l["lat"]]),
        #                          min([l["long"] for l in json_ if l["lat"]]),
        #                          max([l["long"] for l in json_ if l["lat"]]), ]
        # except:
        #     minmaxlatlong = [1000, -1000, 1000, -1000]

        # json_ok = {"Photos": json_,
        #            "minmaxlatlong": minmaxlatlong}

        from pprint import pprint
        # pprint(json_ok)

        end = time.time()

        logger.info("PhotosJsonView: %s" %(end-start))


        return JsonResponse(json_, safe=False)

###Lines
##many
class LinesJsonView(View):
    def get(self, request, *args, **kwargs):
        logger.info("LinesJsonView")
        from .utils import lines_json
        json_ = lines_json(is_global=False)

        json_ok = {"Lines": json_, "minmaxlatlong": [min([l["min_lat"] for l in json_ if l["min_lat"]]),
                                                     max([l["max_lat"] for l in json_ if l["max_lat"]]),
                                                     min([l["min_long"] for l in json_ if l["min_long"]]),
                                                     max([l["max_long"] for l in json_ if l["max_long"]]),
                                                     ]}

        return JsonResponse(json_ok, safe=False)

##one
class LineJsonView(View):
    def get(self, request, *args, **kwargs):
        logger.info("LineJsonView")
        from .utils import lines_json
        line_id = kwargs.get("line_id", None)
        json_ = lines_json(lines=Line.objects.filter(pk=line_id),is_global=False) # requires a queryset

        try:
            min_lat=min([l["min_lat"] for l in json_ if l["min_lat"]])
            max_lat=max([l["max_lat"] for l in json_ if l["max_lat"]])
            min_long=min([l["min_long"] for l in json_ if l["min_long"]])
            max_long=max([l["max_long"] for l in json_ if l["max_long"]])
        except:
            min_lat=-1000
            max_lat=1000
            min_long=-1000
            max_long=1000

        json_ok = {"Lines": json_, "minmaxlatlong": [min_lat, max_lat,min_long,max_long,]}

        return JsonResponse(json_ok, safe=False)

###Geojson objects
class GeoJsonObjectJsonView(View):
    def get(self, request, *args, **kwargs):

        obj_id = kwargs.get("geojsonobj_id", None)
        obj = get_object_or_404(GeoJsonObject, pk=obj_id)
        logger.info("GeoJsonObjectJsonView %s" % obj_id)

        json_ok = {"GeoJSON": [obj.get_geojson()],
                   "minmaxlatlong": [obj.min_lat, obj.max_lat, obj.min_lon, obj.max_lon]}

        return JsonResponse(json_ok, safe=False)

class GeoJsonObjectsJsonView(View):
    def get(self, request, *args, **kwargs):

        logger.info("GeoJsonObjectsJsonView")

        objects=GeoJsonObject.objects.all()
        json_tot=[]
        minmaxlatlon=[]
        
        colors = get_colors(objects.count())

        for obj,color in zip(objects,colors):
            json=obj.get_geojson(color=color)
            json_tot.append(json)

        min_lat=np.nanmin([a for a in objects.values_list("min_lat",flat=True) if a])
        max_lat=np.nanmax([a for a in objects.values_list("max_lat",flat=True) if a])
        min_lon=np.nanmin([a for a in objects.values_list("min_lon",flat=True) if a])
        max_lon=np.nanmax([a for a in objects.values_list("max_lon",flat=True) if a])

        json_ok = {"GeoJSON": json_tot,
                   "minmaxlatlong": [min_lat, max_lat, min_lon, max_lon]}

        return JsonResponse(json_ok, safe=False)


###Tracks
##many
# as lines
class TracksAsLinesJsonView(View):
    """
    this view is for many tracks as lines (or multipoint)
    calls tracks_json
    which calls get_track_single_geojson
    used in:
    point.html
    group.html
    manytracks_plot.html
    manytracks.html
    tracks_list.html
    tracks_map.html
    """
    def get(self, request, *args, **kwargs):
        logger.info("TracksAsLinesJsonView")
        import time
        start = time.time()
        
        from .utils import tracks_json,waypoints_json,photos_json
        from tracks.utils import filter_tracks
        from waypoints.utils import filter_waypoints
        from photos.utils import filter_photos


        ## extract GET parameters
        if request.GET:
            tracks=filter_tracks(request.GET,silent=False)
        else:
            tracks=Track.objects.all()

        track_ids = request.GET.get('track_ids', None)
        ## if i give ids, I keep the same order of the ids, for compatibility with
        ## TracksAsPointListsJsonView (othersie color, which is based on order, is wrong)
        if track_ids:
            track_ids=track_ids.split("_")
            track_ids=[int(a) for a in track_ids]
            ## https://stackoverflow.com/questions/4916851/django-get-a-queryset-from-array-of-ids-in-specific-order
            from django.db.models import Case, When
            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(track_ids)])
            tracks = tracks.order_by(preserved)

        use_color=bool(request.GET.get("use_color", False))
        reduce_points=request.GET.get("reduce_points", None)
        how=request.GET.get("how", None)
        add_flat = request.GET.get("flat", False)
        group_pk = request.GET.get("group_pk", None)
        simple = request.GET.get("simple", False)
        every = int(request.GET.get('every', 0))
        with_photos = int(request.GET.get('with_photos', 0))
        with_waypoints = int(request.GET.get('with_waypoints', 0))
        with_global = int(request.GET.get('with_global', 0))
        # ranks date_order added only for manytracks_plots
        ranks = int(request.GET.get('ranks', 0))
        date_order = int(request.GET.get('date_order', 0))

        n_tracks=tracks.count()

        if date_order:
            tracks=tracks.order_by("beginning")



        # decide points vs lines
        points_line=request.GET.get("points_line", None)

        if not points_line:
            max_n_tracks = OptionSet.get_option("MAX_N_TRACKS_AS_LINES")
            if n_tracks<=max_n_tracks:
                points_line="MultiLineString"
                if not reduce_points:
                    reduce_points="smooth2"
            else:
                points_line="Point"
                reduce_points="single"

        if not reduce_points:
            reduce_points="smooth2"

        #points_line=request.GET.get("points_line", "MultiLineString")
        use_points = request.GET.get('use_points', None)
        if use_points is not None:
            use_points=int(use_points)
            if use_points==0:
                points_line="MultiLineString"
            elif use_points==1:
                points_line="MultiPoint"

        group=None

        ok_load_from_db=False
        if group_pk:
            group=Group.objects.get(pk=group_pk)
            # use cached results if I have set the relative options
            if group.auto_update_properties:
                if group.properties_json!="{}":
                    try:
                        json_tracks=group.get_properties()
                        ok_load_from_db=True
                        # check that the number of tracks is correct!
                        json_tracks=group.check_properties(json_tracks)
                    except Exception as e:
                        logger.error("Cannot load properties_json for group %s: %s" %(group, e))

        if not ok_load_from_db:
            logger.info("not ok_load_from_db %s %s" %(points_line,reduce_points))
            if group_pk:
                if group.always_use_lines:
                    points_line="MultiLineString"
                    reduce_points="smooth2"

            t1=time.time()
            #logger.info("--before tracks_json in TracksAsLinesJsonView: %s" %(t1-start))
                
            json_tracks=tracks_json(
                tracks, 
                with_color=use_color, 
                points_line=points_line,
                reduce_points=reduce_points,
                every=every,
                how=how,
                add_flat=add_flat,
                keep_empty_set=True,
                group_pk=group_pk,
                simple=simple,
                waypoints=with_waypoints,
                photos=with_photos,
                ranks=ranks
            )
            
            # t2=time.time()
            # logger.info("--after tracks_json in TracksAsLinesJsonView: %s" %(t2-start))
            # logger.info("--tracks_json duration in TracksAsLinesJsonView: %s" %(t2-t1))


            #print(json_tracks.keys())

        ## add photos
        json_photos = {"Photos":[]}
        if with_photos:
            from photos.models import Photo
            photos = filter_photos(request.GET, silent=False)
            json_photos =  {"Photos":photos_json(photos)["Photos"]}

        ## add waypoints
        json_waypoints = {"Waypoints":[]}
        if with_waypoints:
            from waypoints.models import Waypoint
            waypoints=filter_waypoints(request.GET, silent=False)
            json_waypoints = {"Waypoints":waypoints_json(waypoints)["Waypoints"]}

        json_global={}
        if with_global:
            bounds={
                "min_lat": json_tracks["minmaxlatlong"] [0],
                "max_lat": json_tracks["minmaxlatlong"] [1],
                "min_long": json_tracks["minmaxlatlong"] [2],
                "max_long": json_tracks["minmaxlatlong"] [3],
            }
            from tracks.utils import loosen_bounds
            from .utils import lines_json, geojson_json, waypoints_json
            bounds=loosen_bounds(bounds)
            json_global["Global Photos"] = photos_json(is_global=True, bounds=bounds)["Photos"]
            json_global["Global Lines"] = lines_json(is_global=True, bounds=bounds)
            json_global["Global GeoJSON"] = geojson_json(is_global=True, bounds=bounds)
            json_global["Global Waypoints"] = waypoints_json(is_global=True, bounds=bounds)["Waypoints"]


        has_hr=any(tracks.values_list("has_hr",flat=True))
        has_freq=any(tracks.values_list("has_freq",flat=True))

        # add photos and waypoints, but hide them by default
        final_json={"features":{
                        "show_features":with_photos or with_waypoints or with_global,
                        "has_hr":has_hr,
                        "has_freq":has_freq,
                    },
                    **json_tracks,
                    # **json_waypoints,
                    # **json_photos,
                    **json_global
                    }

        if not "Waypoints" in   final_json:
            final_json["Waypoints"]=[]       
        if not "Photos" in   final_json:
            final_json["Photos"]=[]       

        final_json["Photos"].extend(json_photos["Photos"])
        final_json["Waypoints"].extend(json_waypoints["Waypoints"])


        end=time.time()
        logger.info("End TracksJsonView: %s" %(end-start))


        #import simplejson as json
        #json.dumps(thing, ignore_nan=True)
        #final_json = json.dumps(final_json,ignore_nan=False)


        # from django.core.serializers import serialize
        # from django.core.serializers.json import DjangoJSONEncoder
        # class LazyEncoder(DjangoJSONEncoder):
        #     def default(self, obj):
        #         if isinstance(obj, YourCustomType):
        #             return str(obj)
        #         return super().default(obj)
        # serialize('json', final_json, cls=LazyEncoder)
        # final_json=json.dumps(final_json)
        return JsonResponse(final_json,safe=False)

#as list of points
class TracksAsPointListsJsonView(View):
    """
    this view is for many tracks as list of points
    (when mapping and plotting)
    calls get_json_LD_tracks from utils
    which calls get_json_LD from models
    used in manytracks.html
    """

    def get(self, request, *args, **kwargs):
        logger.info("ManyTracksJsonView")

        ## extract GET parameters
        reduce_points = request.GET.get('reduce_points', 'every')
        track_ids_string = request.GET.get("track_ids", "")
        every = request.GET.get("every", 0)
        use_color=bool(request.GET.get("use_color", False))
        with_photos = int(request.GET.get('with_photos', 0))
        with_waypoints = int(request.GET.get('with_waypoints', 0))
        with_global = int(request.GET.get('with_global', 0))

        # get track ids
        string_list = track_ids_string.split("_")
        track_ids = [int(s) for s in string_list]

        # fix every
        if reduce_points=="every" and (not every or every=="0"):
            n_points_total = 1  # to avoid having every=0
            for i, track_id in enumerate(track_ids):
                track = get_object_or_404(Track.all_objects, pk=track_id)
                n_points_total += track.n_points

            import math
            from options.models import OptionSet
            every = math.ceil(n_points_total / OptionSet.get_option("MAX_POINTS_TRACK"))

            logger.info("Setting every %s" %every)

        from .utils import get_json_LD_tracks

        tracks_json=get_json_LD_tracks( track_ids,
                                        every=every,
                                        reduce_points=reduce_points,
                                        do_waypoints=with_waypoints,
                                        do_photos=with_photos,
                                        global_wps=with_global,
                                        global_lines=with_global, 
                                        global_geojson=with_global, 
                                        )

        # todo:             if as_lines: #add colors
        #                     track_json = track.get_json_smooth(color=colors[i])


        return JsonResponse(tracks_json, safe=False)

#list of altitudes
class TracksAltsJsonView(View):
    """this view is for many tracks as list of alts"""
    def get(self, request, *args, **kwargs):
        logger.info("TracksAltsJsonView")

        track_ids_string = request.GET.get("track_ids", "")

        string_list = track_ids_string.split("_")
        track_ids = [int(s) for s in string_list]

        from .utils import tracks_alts_json

        tracks_json=tracks_alts_json(track_ids)

        return JsonResponse(tracks_json, safe=False)

##one
# both as list of points and as line
class TrackJsonView(View):
    """list of dictionaries, one for each point"""
    def get(self, request, *args, **kwargs):

        import time
        start = time.time()


        track_id = kwargs.get("track_id", None)
        track=Track.all_objects.get(pk=track_id)



        reduce_points = request.GET.get('reduce_points', 'every')
        points_line = request.GET.get('points_line', 'MultiLineString')
        every = int(request.GET.get('every', 0))

        logger.info("TrackJsonView %s %s"%(track,reduce_points))


        try:
            track_json=track.get_json_LD(reduce_points=reduce_points)
            features = track.get_track_single_geojson(
                color="blue", \
                add_flat=False,\
                reduce_points=reduce_points,\
                points_line=points_line,
                every=every
            )
            track_json["Track"]["details"]=features
        except Exception as e:
            import traceback
            traceback.print_exc()
            track.error(e)
            track_json={"error":str(e)}

        end = time.time()
        logger.info("TrackJsonView: %s" %(end - start))

        return JsonResponse(track_json,safe=False)

## One: Splits, laps, segments, subtracks
class TrackJsonSplitsView(View):
    def get(self, request, *args, **kwargs):
        import time
        start = time.time()

        reduce_points = request.GET.get('reduce_points', 'every')
        track_id = kwargs.get("track_id", None)
        track = get_object_or_404(Track.all_objects, pk=track_id)

        #        reduce_points = request.GET.get('reduce_points', 'every')

        track_json=track.get_json_LD(reduce_points=reduce_points)
        from .utils import track_json_to_splits
        track_json_ok=track_json_to_splits(track_json)

        # add waypoints and photos

        end = time.time()
        logger.info("TrackJsonSplitsView: %s" % (end - start))

        return JsonResponse(track_json_ok, safe=False)

class TrackJsonLapsView(View):
    def get(self, request, *args, **kwargs):
        import time
        start = time.time()

        reduce_points = request.GET.get('reduce_points', 'every')
        track_id = kwargs.get("track_id", None)
        track = get_object_or_404(Track.all_objects, pk=track_id)

        #        reduce_points = request.GET.get('reduce_points', 'every')

        track_json=track.get_json_LD(reduce_points=reduce_points)
        from .utils import track_json_to_splits
        track_json_ok=track_json_to_splits(track_json,feature="Lap")

        # add waypoints and photos

        end = time.time()
        logger.info("TrackJsonLapsView: %s" % (end - start))

        return JsonResponse(track_json_ok, safe=False)

class TrackJsonSegmentsView(View):
    def get(self, request, *args, **kwargs):
        import time
        start = time.time()

        reduce_points = request.GET.get('reduce_points', 'every')
        track_id = kwargs.get("track_id", None)
        track = get_object_or_404(Track.all_objects, pk=track_id)

        #        reduce_points = request.GET.get('reduce_points', 'every')

        track_json=track.get_json_LD(reduce_points=reduce_points)
        from .utils import track_json_to_splits
        track_json_ok=track_json_to_splits(track_json, feature="Segment")

        # add waypoints and photos

        end = time.time()
        logger.info("TrackJsonSegmentsView: %s" % (end - start))

        return JsonResponse(track_json_ok, safe=False)

class TrackJsonSubtracksView(View):
    def get(self, request, *args, **kwargs):
        import time
        start = time.time()

        reduce_points = request.GET.get('reduce_points', 'every')
        track_id = kwargs.get("track_id", None)
        track = get_object_or_404(Track.all_objects, pk=track_id)

        #        reduce_points = request.GET.get('reduce_points', 'every')

        track_json=track.get_json_LD(reduce_points=reduce_points)
        from .utils import track_json_to_splits
        track_json_ok=track_json_to_splits(track_json, feature="Subtrack")

        # add waypoints and photos

        end = time.time()
        logger.info("TrackJsonSubtracksView: %s" % (end - start))

        return JsonResponse(track_json_ok, safe=False)


# class TrackJsonDLView(View):
#     def get(self, request, *args, **kwargs):
#
#         import time
#         start = time.time()
#
#         track_id = kwargs.get("track_id", None)
#         track = get_object_or_404(Track, pk=track_id)
#
#         try:
#             track_json=track.get_json_DL()
#         except Exception as e:
#             import traceback
#             traceback.print_exc()
#             track.error(e)
#             track_json={"error":e}
#
#         end = time.time()
#         logger.info("TrackJsonDLView: %s" %(end - start))
#
#         return JsonResponse(track_json,safe=False)

# class TrackJsonSmoothView(View):
#     def get(self, request, *args, **kwargs):
#
#         import time
#         start = time.time()
#
#         track_id = kwargs.get("track_id", None)
#         track = get_object_or_404(Track, pk=track_id)
#
# #        reduce_points = request.GET.get('reduce_points', 'every')
#
#         track_json=track.get_json_smooth()
#         #add waypoints and photos
#
#         end = time.time()
#         logger.info("TrackJsonSmoothView: %s" %(end - start))
#
#
#         return JsonResponse(track_json,safe=False)