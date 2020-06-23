from django.urls import reverse
import logging
logger = logging.getLogger("gps_tracks")
import traceback
from tracks.models import Track
from groups.models import Group
from photos.models import Photo
from lines.models import Line
from geojson_obj.models import GeoJsonObject
from waypoints.models import Waypoint
from tracks.utils import get_colors, add_colors, add_radius,to_int
from options.models import OptionSet
import numpy as np
from tracks.utils import numbers_to_colors, to_float_or_zero
from django.conf import settings
from options.models import OptionSet

### Groups
def groups_json(groups=None):
    import math
    json_ok={}
    if groups is None:
        groups = Group.objects.all()

    min_lat = min([g.min_lat if g.min_lat else 1000 for g in groups])
    max_lat = max([g.max_lat if g.max_lat else -1000 for g in groups])
    min_lon = min([g.min_long if g.min_long else 1000 for g in groups])
    max_lon = max([g.max_long if g.max_long else -1000 for g in groups])

    colors = get_colors(len(groups))

    for group, color in zip(groups, colors):
        if group.avg_long and group.avg_long and not math.isnan(group.avg_long) and not math.isnan(group.avg_lat):
            json_ok[group.name]={"type": "Feature",
                                "geometry": {
                                    "type": "Point",
                                    "coordinates": [group.avg_long, group.avg_lat]
                                },
                                "name": group.name,
                                "size": group.size,
                                "color": color,
                                "link": reverse("group_detail", kwargs={"group_id": group.pk}),
                                "point_type": "group"
                                }

    json_ok={"Groups":json_ok,"minmaxlatlong":[min_lat,max_lat,min_lon,max_lon]}
    return json_ok

###Waypoints
def waypoints_json(wps=None, is_global=False, bounds={},do_cluster=True):
    ## waypoints
    json_ok=[]
    if wps is None:
        wps = Waypoint.objects.all()
    if is_global:
        point_type="global_waypoint"
        wps=wps.filter(is_global=True)
        opt = OptionSet.get_option("GLOBAL_OBJECTS")
        if opt=="within_bounds" and bounds:
            wps = wps.filter(lat__gte=bounds["min_lat"],
                             long__gte = bounds["min_long"],
                             lat__lte = bounds["max_lat"],
                             long__lte = bounds["max_long"],
                             )
    else:
        point_type="waypoint"

    if isinstance(wps, list):
        wps = Waypoint.objects.filter(pk__in=[wp.pk for wp in wps])

    lats = np.array(wps.values_list("lat", flat=True), dtype=float)
    lons = np.array(wps.values_list("long", flat=True), dtype=float)

    try:
        min_lat = np.nanmin(lats)
        max_lat = np.nanmax(lats)
        min_lon = np.nanmin(lons)
        max_lon = np.nanmax(lons)
    except:
        min_lat = None
        max_lat = None
        min_lon = None
        max_lon = None



    for wp in wps:
        a={"type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [wp.long, wp.lat]
                        },
                        "id": wp.pk,
                        "name": wp.name,
                        "alt": to_int(wp.alt),
                        "description": wp.description,
                        "point_type": point_type,
                        "link": reverse("waypoint_detail", kwargs={"waypoint_id": wp.pk}),
                        "country":wp.country,
                        "region":wp.region,
                        "city":wp.city,
                        "address":wp.address,
                        "lat":wp.lat,
                        "long":wp.long,
                        }
        if wp.track_name and wp.track_pk:
            a["related_track_name"]=wp.track_name
            a["track_link"]=reverse("track_detail", kwargs={"track_id": wp.track_pk})
        else:
            a["related_track_name"] = ""
        if wp.time:
            a["time"]=wp.time.strftime("%Y-%m-%d")
        json_ok.append(a)

    max_d = OptionSet.get_option("DISTANCE_FOR_CLUSTERING")
    max_f = OptionSet.get_option("MAX_FEATURES_FOR_CLUSTERING")

    if do_cluster and max_d and len(lats)>1 and len(lats)<=max_f:
        try:
            from clustering.utils import cluster_points, json_to_cluster
            coords = np.nan_to_num(np.dstack((lats, lons)), nan=1000)[0]
            clusters = cluster_points(coords, max_d=max_d / 1000)  # here in km
            #print("clusters", clusters)

            for i, p in enumerate(json_ok):
                p["cluster"] = int(clusters[i])

            json_ok = json_to_cluster(json_ok)
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error("Cannot do clustering for waypoints: %s" %e)

    from pprint import pprint
    #pprint(json_ok)

    minmaxlatlon=[min_lat,max_lat,min_lon,max_lon]
    minmaxlatlon=loosen_bounds_list(minmaxlatlon)

    logger.debug(minmaxlatlon)

    return {"Waypoints":json_ok,
            "minmaxlatlong":minmaxlatlon}

### Photos
def photos_json(photos=None, is_global=False,  bounds={}, do_cluster=True, level=2):
    import numpy as np
    json_ok=[]
    location_way = OptionSet.get_option("PHOTO_LOCATIONS")
    if photos is None:
        photos = Photo.objects.all()
    if is_global:
        point_type="global_photo"
        photos=photos.filter(is_global=True)
        # filter by location
        opt = OptionSet.get_option("GLOBAL_OBJECTS")
        if opt == "within_bounds" and bounds:
            if location_way == "original":
                photos = photos.filter(lat__gte=bounds["min_lat"],
                                       long__gte=bounds["min_long"],
                                       lat__lte=bounds["max_lat"],
                                       long__lte=bounds["max_long"],
                                       )
            elif location_way == "deduced":
                photos = photos.filter(deduced_lat__gte=bounds["min_lat"],
                                       deduced_long__gte=bounds["min_long"],
                                       deduced_lat__lte=bounds["max_lat"],
                                       deduced_long__lte=bounds["max_long"],
                                       )
    else:
        point_type = "photo"


    coords = None
    min_lat = None
    max_lat = None
    min_lon = None
    max_lon = None

    level=int(level)
    if level==0:
        #simple json only to show photos
        values=photos.values("pk","thumbnail_url_path")
        for v in values:
            v["link"]= reverse("photo_detail", kwargs={"photo_id": v["pk"]}),
            json_ok.append(v)

    elif level==1:
    # simple json only for list
        values=photos.values("pk","thumbnail_url_path","time","country","city","region","name")
        for v in values:
            v["id"]=v["pk"]
            v["link"]= reverse("photo_detail", kwargs={"photo_id": v["pk"]}),
            if v["time"]:
                v["date"]=v["time"].strftime("%Y-%m-%d")

            json_ok.append(v)

    else:
    # full jspon for map
        if isinstance(photos,list):
            photos=Photo.objects.filter(pk__in=[p.pk for p in photos])
        values = photos.values("pk", "thumbnail_url_path", "time", "country", "city", "region", "name")
        deduced_lats = np.array(photos.values_list("deduced_lat",flat=True),dtype=float)
        deduced_lons = np.array(photos.values_list("deduced_long", flat=True), dtype=float)
        lats = np.array(photos.values_list("lat",flat=True),dtype=float)
        lons = np.array(photos.values_list("long", flat=True), dtype=float)

        if location_way == "deduced":
            ok_deduced_coords = np.isfinite(deduced_lats) & np.isfinite(deduced_lons)
            lats_ok = np.where(ok_deduced_coords,deduced_lats,lats)
            lons_ok = np.where(ok_deduced_coords,deduced_lons,lons)
        elif location_way == "original":
            ok_original_coords = np.isfinite(lats) & np.isfinite(lons)
            lats_ok = np.where(ok_original_coords, lats,deduced_lats)
            lons_ok = np.where(ok_original_coords, lons,deduced_lons)

        coords=np.nan_to_num(np.dstack((lats_ok,lons_ok)),nan=1000)[0]

        try:
            min_lat = np.nanmin(lats_ok)
            max_lat = np.nanmax(lats_ok)
            min_lon = np.nanmin(lons_ok)
            max_lon = np.nanmax(lons_ok)
        except:
            pass

        for i,photo in enumerate(values):
            # if location_way=="original":
            #     if photo.long and photo.lat:
            #         photo_long, photo_lat = photo["long"], photo["lat"]
            #     elif photo["deduced_long"] and photo["deduced_lat"]:
            #         photo_long, photo_lat = photo["deduced_long"], photo["deduced_lat"]
            #     else:
            #         photo_long, photo_lat = None, None
            # elif location_way=="deduced":
            #     if photo["deduced_long"] and photo["deduced_lat"]:
            #         photo_long, photo_lat = photo["deduced_long"], photo["deduced_lat"]
            #     elif photo["long"] and photo["lat"]:
            #         photo_long, photo_lat = photo["long"], photo["lat"]
            #     else:
            #         photo_long, photo_lat = None, None
            #
            # if photo_lat is not None and photo_long is not None:
            #     coords.append([photo_lat,photo_long])
            # else:
            #     coords.append([1000,1000])

            if np.isnan(lons_ok[i]):
                photo_long=None
            else:
                photo_long = lons_ok[i]
            if np.isnan(lats_ok[i]):
                photo_lat=None
            else:
                photo_lat = lats_ok[i]

            a={"type": "Feature",
                                "geometry": {
                                    "type": "Point",
                                    "coordinates": [photo_long,photo_lat]
                                },
                                "link": reverse("photo_detail", kwargs={"photo_id": photo["pk"]}),
                                "point_type": "photo",
                                "id": photo["pk"],
                                "point_type":point_type,
                               "lat":photo_lat,
                               "long":photo_long ,
               }
            if photo["time"]:
                a["date"]=photo["time"].strftime("%Y-%m-%d")

            photo.update(a)

            json_ok.append(photo)

    max_d = OptionSet.get_option("DISTANCE_FOR_CLUSTERING")
    max_f = OptionSet.get_option("MAX_FEATURES_FOR_CLUSTERING")

    if do_cluster and max_d  and coords is not None and len(values)>1 and len(values) and len(values)<=max_f:
        try:
            from clustering.utils import cluster_points, json_to_cluster

            try:
                clusters=cluster_points(coords,max_d=max_d/1000) #here in km
            except Exception as e:
                import traceback
                traceback.print_exc()
                logger.error("Cannot do clustering for photos, cluster_points failing: %s" %e)
                clusters=None

            if clusters is not None:
                for i,p in enumerate(json_ok):
                    p["cluster"]=int(clusters[i])
                json_ok=json_to_cluster(json_ok)

        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error("Cannot do clustering for photos: %s" %e)

    minmaxlatlon=[min_lat,max_lat,min_lon,max_lon]
    minmaxlatlon=loosen_bounds_list(minmaxlatlon)

    return {"Photos":json_ok,
            "minmaxlatlong":minmaxlatlon}

### Lines
def lines_json(lines=None, is_global=True, bounds={}):
    json_ok=[]
    if lines is None:
        lines = Line.objects.all()
    if is_global:
        lines=lines.filter(is_global=True)
        from options.models import OptionSet
        opt = OptionSet.get_option("GLOBAL_OBJECTS")
        if opt == "within_bounds" and bounds:
            lines = lines.filter(
                            max_lat__gte=bounds["min_lat"],
                            max_long__gte=bounds["min_long"],
                            min_lat__lte=bounds["max_lat"],
                            min_long__lte=bounds["max_long"],
                             )

    for line in lines:
        coordinates = []
        for lat, lon in zip(line.lats, line.long):
            coordinates.append([lon, lat])

        json_ok.append({"type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": coordinates
                        },
                        "name": line.name,
                        "point_type": "global_line",
                        "link": reverse("line_detail", kwargs={"line_id": line.pk}),
                        "properties": {
                            "name": line.name,
                            "popupContent": line.name,
                            "color": line.color
                        },
                        "min_lat":line.min_lat,
                        "max_lat": line.max_lat,
                        "min_long": line.min_long,
                        "max_long": line.max_long,
                        })
    return json_ok

### geojson objects
def geojson_json(geojsonobjs=None, is_global=True, bounds={}):
    ## waypoints
    json_ok=[]
    if geojsonobjs is None:
        geojsonobjs = GeoJsonObject.objects.all()
    if is_global:
        geojsonobjs=geojsonobjs.filter(is_global=True)
        from options.models import OptionSet
        opt = OptionSet.get_option("GLOBAL_OBJECTS")
        if opt == "within_bounds" and bounds:
            geojsonobjs = geojsonobjs.filter(
                            max_lat__gte=bounds["min_lat"],
                            max_lon__gte=bounds["min_long"],
                            min_lat__lte=bounds["max_lat"],
                            min_lon__lte=bounds["max_long"],
                             )

    colors=get_colors(geojsonobjs.count())

    for obj,color in zip(geojsonobjs,colors):
        json_ok.append(obj.get_geojson(color=color))
    return json_ok

###tracks
## as list of points
def get_json_LD_tracks(ids, reduce_points="every", do_waypoints=True, do_photos=True, global_wps=True,
                       global_lines=True, global_geojson=True, color=None, every=None):
    """
    used by TracksAsPointListsJsonView
    """
    tracks = {}
    colors_track = {}
    from .utils import get_colors
    colors = get_colors(len(ids))
    min_lat = 1000
    min_lon = 1000
    max_lat = -1000
    max_lon = -1000
    has_times = False
    has_alts = False
    has_hr = False
    has_freq = False
    for i, id in enumerate(ids):
        color = colors[i]
        track = Track.all_objects.get(pk=id)
        #print(id, color, track)
        # parameters to facilitate frontend work
        min_lat = min(track.min_lat, min_lat)
        min_lon = min(track.min_long, min_lon)
        max_lat = max(track.max_lat, max_lat)
        max_lon = max(track.max_long, max_lon)
        has_times = has_times or track.has_times
        has_alts = has_alts or track.has_alts
        has_hr = has_hr or track.has_hr
        has_freq = has_freq or track.has_freq
        if i == 0:
            track_json = track.get_json_LD( reduce_points=reduce_points, 
                                            do_waypoints=do_waypoints, 
                                            do_photos=do_photos, 
                                            global_wps=global_wps,
                                            global_lines=global_lines, 
                                            global_geojson=global_geojson, 
                                            color=color,
                                            every=every,
                                            is_from_many_tracks=True)
            global_wps = track_json["Global Waypoints"]
            global_lines = track_json["Global Lines"]
            global_geojson = track_json["Global GeoJSON"]
            waypoints = track_json["Waypoints"]
            photos = track_json["Photos"]
            tracks[track.name_wo_path_wo_ext] = track_json["Track"]["points"]
            colors_track[track.name_wo_path_wo_ext] = color
        else:
            track_json = track.get_json_LD(
                reduce_points=reduce_points, 
                do_waypoints=do_waypoints, 
                do_photos=do_photos, 
                global_wps=False,
                global_lines=False, 
                global_geojson=False, 
                color=color, 
                every=every,
                is_from_many_tracks=True)
            waypoints.extend(track_json["Waypoints"])
            photos.extend(track_json["Photos"])
            tracks[track.name_wo_path_wo_ext] = track_json["Track"]["points"]
            colors_track[track.name_wo_path_wo_ext] = color

    features = {"has_times": has_times,
                "has_alts": has_alts,
                "has_hr": has_hr,
                "has_freq": has_freq}
    # TODO: has freq, hrs, etc.
    json_tot = {
        "features": features,
        "minmaxlatlong": [min_lat, max_lat, min_lon, max_lon],
        "colors": colors_track,
        "Tracks": tracks,
        "Waypoints": waypoints,
        "Photos": photos,
        "Global Waypoints": global_wps,
        "Global Lines": global_lines,
        "Global GeoJSON": global_geojson
    }

    return json_tot

## as lines
def tracks_json(tracks=None, with_color=False, how=None, points_line="MultiLineString", 
                reduce_points="smooth2", add_flat=False, keep_empty_set=False,ranks=False,
                group_pk=None,simple=False,waypoints=False,photos=False,every=0):
    # TODO: do for a single track, then call fct for single track
    """
    json for a list of tracks, only global properties and geometry (no arrays of alt, speed, etc):
    good for map + table, no c3 plots; with flat it is used for scatter plots with one point for each track,
    and for statistics for groups
    called by: 
    -TracksAsLinesJsonView
    -group.set_attributes

    """
    import math
    from tracks.utils import get_cardio_zone
    json_ok=[]

    logger.info(("tracks_json", how,points_line, reduce_points))

    import time
    start=time.time()

    if tracks is None:
        n_tracks=0
    else:
        n_tracks=tracks.count()

    if (tracks is None or n_tracks==0) and not keep_empty_set:
        tracks = Track.objects.all()
    # try:
    #     tracks=list(tracks)
    #     tracks.sort(key=lambda x: x.beginning, reverse=False)
    # except Exception as e:
    #     logger.error(e)

    max_n_tracks = OptionSet.get_option("MAX_N_TRACKS_AS_LINES")
    photos_list=[]
    waypoints_list=[]

    if group_pk:
        tracks=Track.objects.filter(groups__id=group_pk).order_by("beginning")

    #t1=time.time()
    #logger.info("before if tracks in tracks_json: %s" % (t1 - start))
    if tracks is not None and n_tracks>0:
        #t1=time.time()
        #logger.info("after if tracks in tracks_json: %s" % (t1 - start))
        # progressive color, just to distinguish the different tracks
        if with_color:
            colors = get_colors(n_tracks)
        else:
            colors =[None for t in enumerate(n_tracks)]
        if how=="auto":
            if n_tracks<=max_n_tracks:
                points_line="MultiLineString"
                reduce_points="smooth2"
            else:
                points_line="Point"
                reduce_points="single"

        start1=time.time()
        # logger.info("before get_track_single_geojson in tracks_json: %s" % (start1 - start))

        #logger.info("%s %s" %(points_line, reduce_points))

        # json just for map for a lot of tracks
        # for some reason slower than the following part
        if simple and points_line=="Point":
            values = tracks. \
                values("pk", "name_wo_path_wo_ext",
                       "avg_lat",
                       "avg_long","date"
                       )
            for i, v in enumerate(values):
                v["avg_long"] = to_float_or_zero(v["avg_long"])
                v["avg_lat"] = to_float_or_zero(v["avg_lat"])
                v["id"] = v["pk"]
                v["time"] = str(v["date"])
                v["link"] = reverse("track_detail", kwargs={"track_id": v["pk"]})
                v["name"] = v["name_wo_path_wo_ext"]
                v["type"] = "Feature"
                v["geometry"] = {"type": "Point",
                                 "coordinates": [v["avg_long"], v["avg_lat"]]}
                v["point_type"] = "track"
                v["color"] = colors[i]

                json_ok.append(v)

        # this is slightly faster than loading the json for each track, since I need few properties
        elif points_line=="Point":
            from django.db.models import Count
            fields=["pk", "name_wo_path_wo_ext","png_file","date","end_country","end_city","duration",
                                   "duration_string2","pace","pace_string","total_frequency","total_heartbeat",
                                   #"min_lat","max_lat",
                                   "avg_lat",
                                   #"min_long","max_long",
                                   "avg_long",
                                   "duration_string", "duration_string2","length_3d","avg_speed","n_photos",
                                   "activity_type","total_calories", "total_step_length","total_steps",
                                   "uphill","downhill","min_alt","max_alt","user__max_heartrate",]

            try:
                # check if value distance exists (added ony if filtering by distance)
                tracks.values("distance")
                fields.append("distance")
            except:
                pass
            try:
                # check if value distance exists (added ony if filtering by distance)
                tracks.values("duplicated_group")
                fields.append("duplicated_group")
            except:
                pass

            # t2=time.time()
            # logger.info("before query for values in tracks_json: %s" % (t2 - start))


            values = tracks.annotate(n_photos=Count('photos')).\
                                      values(*fields)

            # t2=time.time()
            # logger.info("after query for values in tracks_json: %s" % (t2 - start))

            
            for i,v in enumerate(values):
                v["avg_speed"]=v["avg_speed"] or 0
                v["avg_long"]=to_float_or_zero(v["avg_long"])
                v["avg_lat"] = to_float_or_zero(v["avg_lat"])
                v["length_3d"] = to_float_or_zero(v["length_3d"],default=0)
                v["id"]=v["pk"]
                v["time"] = str(v["date"])
                if v["date"]:
                    v["year"] = v["date"].year
                    v["month"] = v["date"].strftime("%Y-%m") + "-01"
                    v["time_number"] = int(v["date"].strftime("%Y%m%d"))
                else:
                    v["year"] = None
                    v["month"] = None
                    v["time_number"] = -1
                v["link"] = reverse("track_detail", kwargs={"track_id": v["pk"]})
                v["photos_link"]= reverse('track_photos_detail', kwargs={"track_id": v["pk"]})
                v["name"]=v["name_wo_path_wo_ext"]
                v["duration"]= {
                    "duration_string1": v["duration_string"],
                    "duration_string2": v["duration_string2"],
                    "duration": v["duration"],
                    "duration_ms": int((v["duration"] or 0)*60000),
                }
                v["length"]= {
                    "length_string": "{0:.2f}".format(v["length_3d"] / 1000) + "km",
                    "length": v["length_3d"],
                    "length_km": v["length_3d"] / 1000
                }
                v["speed"]= {
                    "speed_string": "{0:.1f}".format(v["avg_speed"] * 3.6) + "km/h",
                    "speed": v["avg_speed"],
                    "speed_kmh": v["avg_speed"] * 3.6
                }
                v["type"]= "Feature"
                v["geometry"]={"type": "Point",
                                   "coordinates": [v["avg_long"],v["avg_lat"]]}
                v["point_type"]= "track"
                v["color"]=colors[i]
                v["pace"]={
                    "pace":v["pace"],
                    "pace_string":v["pace_string"],
                }
                v["frequency"]={
                    "frequency":to_float_or_zero(v["total_frequency"]),
                    "frequency_string":int(to_float_or_zero(v["total_frequency"],default=0))
                }
                v["heartrate"]={
                    "heartrate":to_float_or_zero(v["total_heartbeat"]),
                    "heartrate_string":int(to_float_or_zero(v["total_heartbeat"],default=0))
                }
                v["total_heartrate"]=v["heartrate"]["heartrate"]
                v["total_frequency"]=v["frequency"]["frequency"]
                v.pop("total_heartbeat")
                try:
                    v["cmeters_per_beat"] = v["avg_speed"] / v["total_heartrate"] * 1000
                except:
                    v["cmeters_per_beat"] = None
                try:
                    v["steps_per_beat"] = v["total_frequency"] / v["total_heartrate"]
                except:
                    v["steps_per_beat"]= None
                v["number"]=i+1
                try:
                    v["delta_alt"]=v["max_alt"]-v["min_alt"]
                except:
                    v["delta_alt"]=None
                v["total_heartrate_group"] = get_cardio_zone(v["total_heartrate"], v["user__max_heartrate"])[1]
                v["total_heartrate_color_group"] = get_cardio_zone(v["total_heartrate"], v["user__max_heartrate"])[0]

                # # does this make everythong slow?
                # I do this above, should be OK
                # if tracks[i].duplicated_group!=-1:
                #     v["duplicated_group"]=tracks[i].duplicated_group

                if "distance" in v:
                    v["distance"] = {
                        "distance": v["distance"],
                        "distance_string": "{0:.2f}".format(v["distance"]) + "km"
                    }

                # def clean_nan(x):
                #     from numpy import isnan
                #     try:
                #         if x is None or isnan(x):
                #             return None
                #         else:
                #             return x
                #     except Exception as e:
                #         print("x", x)
                #         raise(e)
                # v = {k:clean_nan(vl) for k,vl in v.items()}

                if True: #add_flat to be used by scatter plots
                    from tracks.utils import flatten
                    v2 = flatten(v)
                    v={**v,**v2}

                json_ok.append(v)

      

        else:
            for i,(track, color) in enumerate(zip(tracks, colors)):
                #print (i, track.pk, track)
                if track.avg_long and track.avg_long and not math.isnan(track.avg_long) and not math.isnan(track.avg_lat):
                    features=track.get_track_single_geojson(
                        color=color, \
                        points_line=points_line, \
                        reduce_points=reduce_points,\
                        every=every,
                        add_flat=add_flat,\
                        number=i+1,
                        photos=photos,
                        waypoints=waypoints
                    )
                    #print(photos,waypoints)
                    from pprint import pprint

                    json_ok.append(features)
                    photos_list.extend(features["Photos"])
                    waypoints_list.extend(features["Waypoints"])



        end1=time.time()
        logger.info("get_track_single_geojson in tracks_json: %s" %(end1-start1))

        #json_ok2 = {a["name"]: a for a in json_ok}

        grades=[]
        colors_legend=[]
        details_legend=[]
        if ranks:
            json_ok, grades, colors_legend, details_legend = add_ranks(json_ok)

        # if group_pk:
        #     group=Group.objects.get(pk=group_pk)
        import numpy as np
        min_lats = [x for x in tracks.values_list("min_lat", flat=True) if x is not None]
        min_lat = np.nanmin(min_lats)
        min_lons = [x for x in tracks.values_list("min_long", flat=True) if x is not None]
        min_lon = np.nanmin(min_lons)
        max_lats = [x for x in tracks.values_list("max_lat", flat=True) if x is not None]
        max_lat = np.nanmax(max_lats)
        max_lons = [x for x in tracks.values_list("max_long", flat=True) if x is not None]
        max_lon = np.nanmax(max_lons)

        final_json={
                    "Tracks":json_ok,
                    "minmaxlatlong":[min_lat,max_lat,min_lon,max_lon],
                    "grades": grades,
                    "colors_legend": colors_legend,
                    "Photos":photos_list,
                    "Waypoints":waypoints_list,
                    "details_legend":details_legend,
                    }
        # from pprint import pprint
        # pprint(json_ok)
    else:
        final_json={
                    "Tracks":[],
                    "minmaxlatlong":[1000,-1000,1000,-1000],
                    "grades": [],
                    "colors_legend": [],
                    "Photos":photos_list,
                    "Waypoints":waypoints_list
                    }

    end=time.time()

    # if n_tracks>0:
    #     logger.info("after track_single_geojson in tracks_json: %s" % (end - end1))
    logger.info("tracks_json duration: %s" %(end-start))
    return final_json


def tracks_alts_json(ids):
    """list of altitudes for heatmap"""
    data=[]
    tracks=[]
    for id in ids:
        tracks.append(Track.all_objects.get(pk=id))
    for t in tracks:
        data.extend(list(zip(t.td.lats,t.td.long,t.td.alts)))

    min_lat=min([t.min_lat for t in tracks])
    max_lat=max([t.max_lat for t in tracks])
    min_lon=min([t.min_long for t in tracks])
    max_lon=max([t.max_long for t in tracks])

    n_lat=100
    n_lon=100
    d_lat = (max_lat-min_lat)/n_lat
    d_lon = (max_lon - min_lon) / n_lon

    lats = np.arange(min_lat,max_lat,d_lat)
    lons = np.arange(min_lon, max_lon, d_lon)
    lala, lolo = np.meshgrid(lats, lons)



    return {"data":data,"minmaxlatlong":[min_lat,max_lat,min_lon,max_lon]}

## helper functions
def fix_geometries_json(json_ok, use_lines=None ):
    logger.info("fix_geometries_json")
    if use_lines is None:
        max_n_tracks = OptionSet.get_option("MAX_N_TRACKS_AS_LINES")
        use_lines = len(json_ok) < max_n_tracks
    for t in json_ok:
        # just one point
        if not use_lines:
            t["geometry"]={
                "coordinates": [t["avg_long"],t["avg_lat"]],
                "type":"Point"
            }
            t["point_type"] = "track"
        # lines
        else:
            try:
                t["geometry"]={
                    "coordinates": t["coordinates_smooth2"],
                    "type":"MultiLineString"
                }
                t["point_type"] = "track_as_line"
            except:
                t["geometry"]={
                    "coordinates": [t["avg_long"],t["avg_lat"]],
                    "type":"Point"
                }
                t["point_type"] = "track"

    return json_ok


def add_colors_to_json(json_ok):
    colors = get_colors(len(json_ok))
    for t,c in zip(json_ok,colors):
        t["color"]=c
    return json_ok

def add_numbers_to_json(json_ok):
    json_ok.sort(key=lambda x:x["time"])
    for i,t in enumerate(json_ok):
        t["number"]=i+1
    return json_ok

def add_ranks(json_ok):
    properties=["duration_duration;time_m", "length_length_km", "speed_speed_kmh", "year;quality",
                                 "total_frequency", "total_heartrate", "total_calories", "total_step_length",
                                 "min_alt", "max_alt", "delta_alt", "total_steps","end_city;quality","end_country;quality",
                                 "month;quality","activity_type;quality","cmeters_per_beat", "uphill","downhill","steps_per_beat",
                                 "pace_pace;time_m"]
    result=add_colors(json_ok,properties)
    grades=result["grades"]
    add_radius(json_ok, properties)

    colors_legend = result["colors_legend"]
    details_legend = result["details_legend"]

    # add ranks
    ranks=[ ("duration_duration", True),
            ("length_length", True),
            ("speed_speed", True),
            ("total_frequency", True),
            ("min_alt",True),
            ("max_alt", True),
            ("total_heartrate", False), # lower is better
            ("total_calories", True),
            ("total_step_length", True),
            ("total_steps", True),
            ("delta_alt", True),
            ("cmeters_per_beat",True),
            ("steps_per_beat",True),
            ("uphill", True),
            ("downhill", True),
            ("pace_pace", False),
            ]

    for (feature,reversed) in ranks:
        logger.info("Updating ranks for feature %s" %feature)
        #if feature=="Heartrate":
        #   print ([x[feature] for x in json_ok])
        #print(feature)
        try:
            for el2 in json_ok:
                el2.update({feature + "_rank": None})
            json_ok_feature = [t for t in json_ok if feature in t.keys() and t[feature]]
            json_ok_feature.sort(key=lambda x: x[feature],reverse=reversed)
            #pprint(sorted_obj)
            for i, element in enumerate(json_ok_feature):
                for el2 in json_ok:
                    if el2["name"] == element["name"]:
                        el2.update({feature + "_rank": i+1})
                        break
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(e)


    return json_ok, grades, colors_legend, details_legend

def track_json_to_splits(track_json,feature="Split"):

    name=(feature[0]).upper()+feature[1:] #Split
    name_plural = name +"s"                 #Splits
    #track_only_json=track_json.pop("Track")
    track_only_json = track_json["Track"]["points"]

    #track_only_json = track_only_json[list(track_only_json.keys())[0]]

    splits_json={}
    colors={}

    for p in track_only_json:
        #print(p)
        split=p[feature]
        if split not in splits_json:
            #print(split)
            splits_json[split]={"points":[], "color":p["Color"+name], "name":p[name+"Name"], "number":split}
        splits_json[split]["points"].append(p)

    track_json[name_plural]=splits_json

    if "legend" in track_json.keys():
        track_json.pop("legend")

    track_json["features"]["plot_track"]=False

    return track_json


def loosen_bounds_list(bounds):
    if bounds[0] is not None and bounds[1] is not None and bounds[2] is not None and bounds[3] is not None:
        return [bounds[0]-0.01,bounds[1]+0.01,bounds[2]-0.01,bounds[3]+0.01]
    else:
        return [None,None,None,None]

