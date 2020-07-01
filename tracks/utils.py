import numpy as np
import math
import os
from .models import *
from pprint import pprint
from datetime import datetime
from django.urls import reverse
import logging
logger = logging.getLogger("gps_tracks")
import traceback
from options.models import OptionSet
import numpy as np


def parse_deltat(row, column=4):
    # print(row[columns[4]])
    from datetime import datetime, timedelta

    try:
        parsed_time = datetime.strptime(row[columns[column]].strip(" "), "%H:%M:%S")
        return timedelta(
            hours=parsed_time.hour,
            minutes=parsed_time.minute,
            seconds=parsed_time.second,
        )
    except:
        try:
            parsed_time = datetime.strptime(row[columns[column]].strip(" "), "%M:%S")
            return timedelta(minutes=parsed_time.minute, seconds=parsed_time.second)
        except:
            try:
                parsed_time = datetime.strptime(row[columns[column]].strip(" "), "%S")
                return timedelta(seconds=parsed_time.second)
            except:
                return -1


def make_df(list_of_tracks):
    """Makes a pandas DataFrame from a list of tracks"""
    import pandas as pd

    df2 = pd.DataFrame()
    # reads the dict keys of the description from the first available file
    for t in list_of_tracks:
        try:
            columns = list(t.descr_dict.keys())
            break
        except:
            continue
    # loop over tracks
    for t in list_of_tracks:
        # this part is for all the std values
        attributes_ok = {k: v for (k, v) in t.__dict__.items() if not k.startswith("_")}
        temp = pd.DataFrame(
            index=[a for a in attributes_ok.keys()],
            data=[a for a in attributes_ok.values()],
        )
        # print(temp)
        # this part is for the description in kml files
        features = (
            "length",
            "avg_speed",
            "avg_mov_speed",
            "max_speed",
            "max_elev",
            "min_elev",
            "elev_gain",
            "max_grade",
            "min_grade",
        )
        try:
            temp = temp.append(
                pd.DataFrame(index=columns, data=list(t.descr_dict.values()))
            )
        except:
            temp = temp.append(pd.DataFrame(index=columns))
        temp = temp.T
        try:
            for i, n in enumerate((3, 6, 7, 8, 12, 13, 14, 15, 16)):
                temp[features[i]] = temp.apply(
                    lambda row: float(row[columns[n]].split(" ")[1].replace(",", ".")),
                    axis=1,
                )
            # df2["duration_d"]=df.apply (lambda row: parse_deltat(row,4),axis=1)
        except:
            for i, n in enumerate((3, 6, 7, 8, 12, 13, 14, 15, 16)):
                temp[features[i]] = np.nan

        df2 = df2.append(temp)
    df2.reset_index(inplace=True, drop=True)
    return df2





def prune_tracks(tracks):
    """Remove duplicated and empty tracks from a list of tracks; prefers kml/kmz over gpx"""
    tracks2 = []
    for track in tracks:
        if track.avg_lat is None:
            logger.info(track.name + " is empty")
            continue
        new = True
        for track2 in tracks2:
            if track.lats == track2.lats:
                if track2.extension in (".kmz", ".kml"):
                    logger.info(
                        track.file
                        + " is equal to "
                        + track2.file
                        + ", keep "
                        + track2.file
                    )
                    new = False
                if track2.extension == ".gpx":
                    logger.info(
                        track.file
                        + " is equal to "
                        + track2.file
                        + ", keep "
                        + track.file
                    )
                    tracks2.remove(track2)
        if new:
            tracks2.append(track)
    return tracks2






    # tracks_new.sort(key=lambda x: x.group)

    # import matplotlib.pyplot as plt
    # import matplotlib
    # from matplotlib import cm
    # cmap = cm.get_cmap('gist_rainbow', n_clusters )
    # col_groups=[matplotlib.colors.rgb2hex(cmap(i)[:3])for i in range(cmap.N)]





def get_colors(n, colorscale=None):
    import matplotlib
    from matplotlib import cm

    logger.debug("get_colors")
    if not colorscale:
        colorscale=OptionSet.get_option("COLORSCALE_LISTS")
    cmap = cm.get_cmap(colorscale, n)
    try:
        colors = [matplotlib.colors.rgb2hex(cmap(i)[:3]) for i in range(cmap.N)]
    except:
        colors=["black" for i in range(n)]
    # colors=["black" for i in range(n)]
    return colors











 





# def get_splits(dist_array, time_array):
#     """returns list of times and distcances for each km"""
#     import numpy as np
#     logger.info("get_splits")
#
#     indices = get_split_indices(dist_array)
#     d = np.array(dist_array)
#     times = np.array(time_array)[indices]
#     distances = np.array(dist_array)[indices]
#     durations = list([times[0]]) + list(np.diff(times))
#     lengths = list([distances[0]]) + list(np.diff(distances))
#     last_dt = time_array[-1] - time_array[indices[-1]]
#     last_ds = dist_array[-1] - d[indices[-1]]
#     return list(durations) + [last_dt], list(lengths) + [last_ds]
#
#
# def get_splits_pace(dist_array, time_array):
#     logger.info("get_splits_pace")
#     durations, lengths = get_splits(dist_array, time_array)
#     lengths = [l / 1000 for l in lengths]
#     list_ = []
#     speeds =[]
#     for d, l in zip(durations, lengths):
#         pace = d / l
#         speed = 3600 / pace
#         list_.append([sec_to_min_s(d), l, sec_to_min_s(pace), speed])
#         speeds.append(speed)
#     return list_, speeds
#
# def get_splits_hr(dist_array, hr_array):
#     """returns list of hr for each km"""
#     import numpy as np
#     logger.info("get_splits_hr")
#
#     indices = list(get_split_indices(dist_array))
#     indices.insert(0,0)
#     indices.append(len(dist_array)-1)
#     #print(indices)
#     hrs= [np.mean(hr_array[min(ind,len(hr_array)-1):min(indices[i+1],len(hr_array)-1)]) if i<len(indices)-1 else 0 for i, ind in enumerate(indices)]
#     #print(hrs)
#     hrs=hrs[:-1]
#
#     return hrs


def sec_to_min_s(seconds):
    logger.debug("sec_to_min_s")
    try:
        return str(int(seconds // 60)) + ":" + "{:02}".format(int(seconds % 60))
    except:
        return "0"


def sec_to_h_min_s(seconds):
    logger.debug("sec_to_h_min_s")
    return (
        str(seconds // 3600)
        + ":"
        + "{:02}".format(int(seconds % 3600 // 60))
        + ":"
        + "{:02}".format(int(seconds % 60))
    )


def sec_to_str(seconds):
    logger.debug("sec_to_str")
    if seconds < 3600:
        return sec_to_min_s(seconds)
    else:
        return sec_to_h_min_s(seconds)


# def sec_to_speed(seconds):
#     return str(int(seconds//60))+"m:"+"{:02}".format(int(seconds%60))+"s"















def get_all_paths(node, path=None, fct="features"):
    """https://stackoverflow.com/a/42678356
    fct is the method to call on a note to get its children"""
    paths = []
    if path is None:
        path = []
    path.append(node)
    try:
        #if getattr(node, fct) gives a list
        if len(list(getattr(node, fct)()))>0:
            for child in getattr(node, fct)():
                paths.extend(get_all_paths(child, path=path[:], fct=fct))
        #if getattr(node, fct) gives an empty list
        else:
            paths.append(path)
    #if getattr(node, fct) does not exist
    except Exception as e:
        paths.append(path)
    return paths

def get_all_nodes(k,fct):
    paths=get_all_paths(k,fct=fct)
    nodes=set([item for sublist in paths for item in sublist])
    return list(nodes)

def get_lat_lon(k):
    logger.info("get_lat_lon")
    for node in get_all_nodes(k):
        try:
            if len(node.geometry.coords)>1:
                lats=[x[0] for x in node.geometry.coords]
                long=[x[1] for x in node.geometry.coords]
                return lats,long       
        except Exception as e:
            logger.warning(str(e))
    
    return [],[]

def open_kml_file(kml_file):
    from fastkml import kml
    with open(kml_file, 'r') as myfile:
        data=myfile.read().encode('utf-8')

        k = kml.KML()
        k.from_string(data)
        return k




def delete_files(track):
    message="Deleted file(s) "
    import os
    if (track.gpx_file):
        file=track.gpx_file
        os.remove(file)
        message+=file+", "
    if (track.kml_file):
        file=track.kml_file
        os.remove(file)
        message+=file+", "
    if (track.kmz_file):
        file=track.kmz_file
        os.remove(file)
        message+=file+", "
    if (track.tcx_file):
        file=track.tcx_file
        os.remove(file)
        message+=file+", "
    if (track.csv_file):
        file=track.csv_file
        os.remove(file)
        message+=file+", "
    return message


def filter_queryset_by_distance(query_set, lat,long, distance=None, limit=None):
        """
        approximate formula, easiest to implement
        x = (lon2 - lon1) * cos((lat2 + lat1) / 2)
        y = lat2 - lat1
        c = sqrt(x ** 2 + y ** 2)
        requires lonrad e latrad to be defined in the incoming queryset
        """
        from django.db.models.functions import Sin, Cos, ATan2, Sqrt, Power
        from django.db.models import F
        from math import radians

        R = 6373.0
        lat_p = radians(float(lat))
        long_p = radians(float(long))
        if distance:
            distance = float(distance)
        if limit:
            limit=int(limit)

        result =  query_set.\
                    annotate(dlon=F("lonrad") - long_p). \
                    annotate(dlat=F("latrad") - lat_p). \
                    annotate(latavg=(F("latrad") + lat_p) / 2). \
                    annotate(x=F("dlon") * Cos(F("latavg"))). \
                    annotate(c=Sqrt(Power("x", 2) + Power("dlat", 2))). \
                    annotate(distance=R * F("c"))
        if distance:
            result = result.filter(distance__lte=distance)

        result = result.order_by("distance")

        if limit:
            result = result[:limit]

        return result

        


def filter_tracks(request,silent=True,initial_queryset=None):
    from datetime import datetime, timedelta
    from .models import Track
    from django.db.models import Q
    from django.db.models import Count

    today = datetime.today()

    print(request)

    import time
    start=time.time()
    logger.debug("filter_tracks")

    if initial_queryset:
        tracks=initial_queryset
    else:
        tracks=Track.objects.all()

    n_days=request.get('n_days',None)           #OK
    name = request.get('name',None)           #OK
    extension = request.get('extension',None)           #OK
    country = request.get('country',None)           #OK
    address = request.get('address',None)           #OK
    year = request.get('year',None)           #OK
    heartbeat = request.get('heartbeat',None) #OK
    frequency = request.get('frequency',None) #OK
    q = request.get('q',None)            #OK
    group_pk_search = request.get('group_pk_search',None) #OK
    group_pk = request.get('group_pk',None) #no need
    how_many = request.get('how_many',None) #OK
    lat = request.get('lat',None) #TOK
    long = request.get('lng',None) #OK
    distance = request.get('dist',None) #OK 
    by_id = request.get('by_id', None) #OK
    ids_string = request.get('track_ids',None) #no need
    min_date = request.get('min_date',None) #OK
    max_date = request.get('max_date',None)#OK
    limit = request.get('limit', False)#OK
    time_zone = request.get('time_zone', None)#OK
    no_search = request.get('no_search', None)
    deleted_tracks = request.get('deleted_tracks', 0)#OK
    exclude_excluded_groups = request.get('exclude_excluded_groups', 0)#OK
    ## special searches
    # duplicated_tracks = request.get('duplicated_tracks',False)#OK
    #wrong_coords = request.get('wrong_coords',None) #TODO
    #merged_tracks = request.get('merged_tracks', False)#OK
    # similar_track_pk = request.get('similar_to',None) #NO
    # similar_group_pk = request.get('similar_to_group',None) #NO
    # close_group_pk = request.get('close_to_group',None) #NO
    # 
    special_search=request.get('special_search', None)#OK
    special_search_pk=request.get('special_search_pk', None)#OK

    if no_search:
        return Track.objects.none()


    # by group
    if group_pk:
        return Track.all_objects.filter(group__pk=int(group_pk))

    tracks=None
    # by ids, here I must take the all_objects selector
    if ids_string:
        tracks = Track.all_objects.filter(pk__in=[int(pk) for pk in ids_string.split("_") ])

    # by group, in OR with ids
    if group_pk_search:
        tracks_group =  Track.all_objects.filter(group__pk=int(group_pk_search))
        if tracks is None:
            tracks = tracks_group
        else:
            tracks = tracks | tracks_group

    if deleted_tracks:
        deleted_tracks=int(deleted_tracks)
        # here I must use all_objects, otherwise these tracks are not picked
        # 0: only active tracks (does not enter here)
        # 1: only deleted tracks 
        # 2: also deleted tracks
        if deleted_tracks==1 and tracks is None:
            tracks=Track.all_objects.filter(is_active=False)
        elif deleted_tracks==2 and tracks is None:
            tracks=Track.all_objects.all()
    elif tracks is None:
        tracks=Track.objects.all()


    if how_many:
        how_many = int(how_many)
    
    logger.debug("request %s" % request)

    #by last n days
    if n_days:
        n_days=int(n_days)
    if n_days==-1:
        tracks = tracks.filter(date__isnull=True)
    elif n_days:
        tracks = tracks.filter(date__lte=today).filter(date__gte=today-timedelta(days=n_days))
    else:
        pass

    # by name
    if name:
        tracks = tracks.filter(name_wo_path_wo_ext__icontains=name)

    # by extension
    if extension:
        tracks = tracks.filter(extension__icontains=extension)

    # by country
    if country=="None":
        tracks = tracks.filter(
                                Q(beg_country__isnull=True,end_country__isnull=True)| \
                                Q(beg_country="", end_country="")
                              )
    elif country:
        tracks = tracks.filter(Q(beg_country=country)|Q(end_country=country))

    # by time_zone
    if time_zone=="None":
        tracks = tracks.filter(time_zone__isnull=True)
    elif time_zone:
        tracks = tracks.filter(time_zone=time_zone)

    # by address
    if address:
        tracks = tracks.filter(
            Q(beg_country__icontains=address)|Q(end_country__icontains=address)|
            Q(beg_region__icontains=address)|Q(end_region__icontains=address)|
            Q(beg_city__icontains=address)|Q(end_city__icontains=address)|
            Q(beg_address__icontains=address)|Q(end_address__icontains=address)
        )

    # by year
    if year and year!="None":
        year=int(year)
        tracks = tracks.filter(date__year=year)
    if year=="None":
        tracks = tracks.filter(date__isnull=True)

    # by heartbeat
    import decimal
    if heartbeat=="yes":
        tracks = tracks.filter(total_heartbeat__isnull=False).exclude(total_heartbeat=decimal.Decimal('NaN'))
    if heartbeat=="no":
        tracks = tracks.filter(Q(total_heartbeat__isnull=True)|Q(total_heartbeat=decimal.Decimal('NaN')))

    # by frequency
    import decimal
    if frequency=="yes":
        tracks = tracks.filter(total_frequency__isnull=False).exclude(total_frequency=decimal.Decimal('NaN')).exclude(total_frequency=0)
    if frequency=="no":
        tracks = tracks.filter(Q(total_frequency__isnull=True)|Q(total_frequency=decimal.Decimal('NaN'))|Q(total_frequency=0))


    import decimal



    # by string
    if q:
        tracks = tracks.filter(
                                Q(csv__icontains=q) |
                                Q(gpx__icontains=q) |
                                Q(kml__icontains=q) |
                                Q(kmz__icontains=q) |
                                Q(tcx__icontains=q)
        )


    if exclude_excluded_groups:
        tracks = tracks.exclude(groups__exclude_from_search=True)

    # # by group
    # if group_pk:
    #     tracks = tracks.filter(group__pk=group_pk)

    # by last ids--> now i order by creation date
    if by_id:
        by_id=int(by_id)
        if by_id>0:
            tracks=tracks.order_by("-created")[:by_id]

    # by min max date
    if min_date:
        min_date=datetime.strptime(min_date,"%Y-%m-%d").date()
        tracks=tracks.exclude(date__isnull=True).filter(date__gte=min_date)
    if max_date:
        max_date = datetime.strptime(max_date, "%Y-%m-%d").date()
        tracks=tracks.exclude(date__isnull=True).filter(date__lte=max_date)

    # duplicated tracks

    # values("n_points","initial_lat","initial_lon","final_lat","final_lon","beg_country","id").\
    # annotate(Count("n_points")).\
    # annotate(Count("initial_lat")).\
    # annotate(Count("initial_lon")).\
    # annotate(Count("final_lat")).\
    # annotate(Count("final_lon")).\
    # values("n_points","initial_lat","initial_lon","final_lat","final_lon","beg_country","id").\


#     if duplicated_tracks:
#         #https://stackoverflow.com/questions/8989221/django-select-only-rows-with-duplicate-field-values
        
#         #print("duplicated_tracks")
#         duplicated_values = tracks.\
#             values("n_points","initial_lat","initial_lon","final_lat","final_lon","avg_lat","avg_long","date").\
#             annotate(Count("n_points")).\
#             values("n_points","initial_lat","initial_lon","final_lat","final_lon","avg_lat","avg_long","date").\
#             order_by().\
#             filter(n_points__gt=0).\
#             filter(n_points__count__gt=1)#.\
#             #values()#.\#.\
#             #values_list("id", flat=True)#.\
#             #filter(n_points__count__gt=1)#.\
#             # filter(initial_lat__count__gt=1).\
#             # filter(initial_lon__count__gt=1).\
#             # filter(final_lat__count__gt=1).\
#             # filter(final_lon__count__gt=1)
#         ids=[]
#         all_dupl_tracks=[] #Track.objects.none()
#         groups={}
#         for i,dv in enumerate(duplicated_values): #TODO: make faster
#             tracks_temp=tracks.filter(**dv)
#             for t in tracks_temp:
#                 groups[t.pk]=i
#                 all_dupl_tracks.append(t.pk)
# #            new_ids=tracks_temp.values_list("pk",flat=True)
# #            ids.extend(new_ids)

#         tracks=tracks.filter(pk__in=all_dupl_tracks)
#         for t in tracks:
#             t.duplicated_group=groups[t.pk]
#         #tracks=tracks.filter(pk__in=ids)

    # if merged_tracks:
    #     tracks=tracks.filter(is_merged=True)

    ## Special searches
    # by missing coords
    if special_search=="wrong_coords":
        tracks = tracks.filter(Q(avg_lat__isnull=True) | Q(avg_long__isnull=True) | Q(avg_lat=0) | Q(avg_long=0)|
                Q(avg_lat=decimal.Decimal('NaN'))|Q(avg_long=decimal.Decimal('NaN')))
    elif special_search=="merged_tracks":
        # merged tracks
        tracks=tracks.filter(is_merged=True)
    elif special_search=="duplicated_tracks":
        #https://stackoverflow.com/questions/8989221/django-select-only-rows-with-duplicate-field-values
        duplicated_values = tracks.\
            values("n_points","initial_lat","initial_lon","final_lat","final_lon","avg_lat","avg_long","date").\
            annotate(Count("n_points")).\
            values("n_points","initial_lat","initial_lon","final_lat","final_lon","avg_lat","avg_long","date").\
            order_by().\
            filter(n_points__gt=0).\
            filter(n_points__count__gt=1)#.\
            #values()#.\#.\
            #values_list("id", flat=True)#.\
            #filter(n_points__count__gt=1)#.\
            # filter(initial_lat__count__gt=1).\
            # filter(initial_lon__count__gt=1).\
            # filter(final_lat__count__gt=1).\
            # filter(final_lon__count__gt=1)
        ids=[]
        all_dupl_tracks=[] #Track.objects.none()
        groups={}
        for i,dv in enumerate(duplicated_values): #TODO: make faster
            tracks_temp=tracks.filter(**dv)
            for t in tracks_temp:
                groups[t.pk]=i
                all_dupl_tracks.append(t.pk)
        #    new_ids=tracks_temp.values_list("pk",flat=True)
        #    ids.extend(new_ids)

        tracks=tracks.filter(pk__in=all_dupl_tracks)
        # for t in tracks:
        #     t.duplicated_group=groups[t.pk]
        # I need to add the duplicated_group field while retaining a queryset
        #https://stackoverflow.com/questions/36137528/django-conditional-expression

        from django.db.models import When, F, Q, Value, Case
        whens = [
            When(pk=k, then=v) for k, v in groups.items()
        ]

        from django.db import models
        tracks = tracks.annotate(
            duplicated_group=Case(
                *whens,
                default=-1,
                output_field=models.IntegerField()
            )
        )

        #tracks=tracks.filter(pk__in=ids)
    elif special_search=="close_to_group":
        if not special_search_pk:
            return Track.objects.none()
        group = Group.objects.get(pk=int(special_search_pk))
        lat = group.avg_lat
        long = group.avg_long
        # distance = None 
        # if not how_many:
        #     how_many=20
    elif special_search=="close_to_track":
        if not special_search_pk:
            return Track.objects.none()
        track = Track.objects.get(pk=int(special_search_pk))
        lat = track.avg_lat
        long = track.avg_long
        # distance = None 
        # if not how_many:
        #     how_many=20
    elif special_search=="similar_to_track":
        if not special_search_pk:
            return Track.objects.none()
        if not how_many:
            how_many=20
        track = Track.all_objects.get(pk=special_search_pk)
        sim, list_pk, list_pk_all = find_similar_tracks(similar_to_tracks=[track],search_in_tracks=tracks)
    elif special_search=="similar_to_group":
        if not special_search_pk:
            return Track.objects.none()
        if not how_many:
            how_many=20
        group = Group.objects.get(pk=special_search_pk)
        #sim, list_pk, list_pk_all = find_similar_tracks(group=group)
        sim, list_pk, list_pk_all = find_similar_tracks(similar_to_tracks=group.tracks.all(),search_in_tracks=tracks)
    elif special_search=="empty_tracks":
        tracks=tracks.annotate(count_wp=Count('waypoint')).\
            annotate(count_wp2=Count('waypoints2')).\
            filter(n_points=0).filter(count_wp=0).filter(count_wp2=0)

    ## by distance to a point: can choose within distance, or limit to the how_many closest
    if lat and long:
        # if close to a given lat/lng, limit distance to 3km if not set
        if not how_many and not distance:
            if special_search=="close_to_group" or special_search=="close_to_track":
                how_many=20
            else:
                distance=3
        if True: #distance or special_search=="close_to_group"  or special_search=="close_to_track" or how_many:
            #tracks_list = find_near_tracks_point(lat, long, distance)
            #tracks_pk = [t.pk for t in tracks_list]
            #tracks = tracks.filter(pk__in=tracks_pk)

            import decimal

            from django.db.models.functions import Radians
            initial_queryset=  tracks. \
                exclude(avg_lat__isnull=True). \
                exclude(avg_long__isnull=True). \
                exclude(avg_lat=decimal.Decimal('NaN')). \
                exclude(avg_long=decimal.Decimal('NaN')). \
                annotate(latrad=Radians("avg_lat")). \
                annotate(lonrad=Radians("avg_long"))

                #exclude(groups__exclude_from_search=True). \


            if special_search=="close_to_group":
                initial_queryset = initial_queryset.exclude(groups__in=[special_search_pk])

            tracks = filter_queryset_by_distance(
                initial_queryset,
                lat=lat,
                long=long,
                distance=distance,
                limit = how_many
            )


    # by similarity to another track or group
    # this is the only part not done within django
    # returns a list rather than a queryset
    # search in the tracks filtered up to now
    if special_search=="similar_to_track" or special_search=="similar_to_group":
        # order by similarity
        #sim_1d = sim[:, 0] this only takes the first input track
        sim_1d = np.mean(sim, axis=1)  # average over input tracks
        inds = (-sim_1d).argsort()
        sorted_pk = np.array(list_pk_all)[inds]
        sorted_sim = sim_1d[inds]
        tracks_list = []
        dict_pk_sim={}
        for t_pk, sim in zip(sorted_pk[:how_many], sorted_sim[:how_many]):
            dict_pk_sim[t_pk]=sim
        tracks_pk=dict_pk_sim.keys()
        tracks=tracks.filter(pk__in=tracks_pk)
        for t in tracks:
            t.similarity=dict_pk_sim[t.pk]

    if how_many:
        how_many = int(how_many)
        #tracks = tracks[:how_many] -> NO, this gives a list, and I need a queryset later on (to use annotate)
        if isinstance(tracks,list):
            tracks=tracks[:how_many] #list
        else:
            from django.db.models import F
            try:
                tracks=tracks.order_by(F("beginning").desc(nulls_last=True))
            except:
                pass
            tracks.query.set_limits(0, how_many) #queryset

    # len_tracks =  tracks.count()

    end = time.time()
    if not silent:
        # logger.info("filter_tracks: %.3f s, %s tracks" %(end-start,len_tracks))
        logger.info("filter_tracks: %.3f s" %(end-start))

    return tracks


def pace_from_speed(speed):
    """km/h to min/km"""

    if speed:
        pace = 60 / speed  # (min/km)
        pace_string = (
                                str(int(pace))
                                + ":"
                                + "{:02}".format(int((pace - int(pace)) * 60))
                                + "min/km"
                            )
    else:
        pace_string="No data"

    return pace_string


def numbers_to_colors(array,colorscale=None,steps=256, steps_legend=9, how="number",mhr=None,diverging=False):
    import matplotlib
    from matplotlib import cm
    from numpy import percentile
    import math
    import numpy as np

    if not colorscale:
        colorscale=OptionSet.get_option("COLORSCALE_TRACK")

    if diverging:
        colorscale=OptionSet.get_option("COLORSCALE_DIVERGING")

    if how=="number" or how=="time_ms" or how=="time_hm" or not how:
        ## assign color to each point in the array
        #start colormap
        cmap = cm.get_cmap(colorscale, steps)
        #find minimum and maximum (percentile to exclude outliers)
        try:
            min_array = np.percentile([a for a in array if a], 5)
            max_array = np.percentile([a for a in array if a], 95)
            if diverging:
                max_array=max([-min_array,max_array])
                min_array=-max_array
            delta=max_array-min_array
            #assign a step to each point, between 0 and steps
            ints=[int(min(1,max(0,(x-min_array)/delta))*steps) if x is not None else None for x in array ]
            # if diverging:
            #     print(max(ints),min(ints)) #256,0
            #assign a color to each point according to the step to which it belongs
            colors = [matplotlib.colors.rgb2hex(cmap(i)[:3]) if i is not None else None for i in ints]

            ## create legend
            #start colormap
            cmap = cm.get_cmap(colorscale, steps_legend)
            #numbers
            grades = [min_array + delta * i / (steps_legend-1) for i in range(steps_legend)]
            #colors
            a = list(range(steps_legend))
            colors_legend = [matplotlib.colors.rgb2hex(cmap(i)[:3]) for i in a]
            # if diverging:
            #     print("grades",grades)
            #     print("colors_legend",colors_legend)
            # format time from minutes
            # hour minute
            if how=="time_ms":
                grades=[format_minutes_ms(g) for g in grades]
            # minute second
            if how=="time_hm":
                grades=[format_minutes_hm(g) for g in grades]
        except:
            colors=[None for a in array]
            grades=[]
            colors_legend=[]
    elif how=="quality":
        colorscale=OptionSet.get_option("COLORSCALE_LISTS")
        try:
            qs=sorted(list(set(array))) # unique features
        except:
            qs = list(set(array))  # unique features
        steps=len(qs)
        cmap = cm.get_cmap(colorscale, steps)
        ints=[]
        #print("ints", ints)
        for a in array:
            for i,q in enumerate(qs):
                if a==q:
                    ints.append(i)
                    break
        colors = [matplotlib.colors.rgb2hex(cmap(i)[:3]) for i in ints]
        #print(colors)

        grades=qs
        colors_legend = [matplotlib.colors.rgb2hex(cmap(i)[:3]) for i in range(len(grades))]
        #print(colors_legend)

    try:
        grades=[g if not np.isnan(g) else None for g in grades]
    except:
        pass

    return colors,grades,colors_legend

def features_for_similarity():
    features = {
        "avg_lat":10,
        "avg_long":10,
        "length_3d":5,
        "min_lat":5,
        "min_long":5,
        "max_lat":5,
        "max_long":5,
        "min_alt":5,
        "max_alt":5,
        "avg_speed":4,
        "duration":4,
        "total_frequency":3,
        "total_heartbeat":3,
        "total_calories":1,
        "total_steps":1,
        "max_cardio":1,
        "min_cardio":1,
        "max_speed":1,
    }
    return features


def find_similar_tracks(similar_to_tracks, search_in_tracks=None, features_weights=None):
    logger.info("find_similar_tracks")
    from tracks.models import Track
    from sklearn.preprocessing import MinMaxScaler, StandardScaler
    from sklearn.metrics.pairwise import cosine_similarity, rbf_kernel, laplacian_kernel
    from scipy.spatial.distance import cosine


    if features_weights is None:
        features_weights = features_for_similarity()
    features=features_weights.keys()
    weights = list(features_weights.values())
    # if similar_to_tracks is None and group is None:
    #     tracks = Track.objects.exclude(groups__exclude_from_search=True).only(*features)
    # elif group:
    #     tracks= group.tracks.all().only(*features)

    # exclude input tracks
    similar_to_tracks_pk_list=[t.pk for t in similar_to_tracks]

    if search_in_tracks is None:
        search_in_tracks=Track.objects.all()

    search_in_tracks=search_in_tracks.exclude(pk__in=similar_to_tracks_pk_list).only(*features)

    array0, list_pk_all = collect_track_infos(features, search_in_tracks)
    array1, list_pk = collect_track_infos(features, similar_to_tracks)
    #rescale features to 1
    scaler = MinMaxScaler()
    scaler.fit(array0)
    array0n = scaler.transform(array0)
    array1n = scaler.transform(array1)
    #apply weights of each feature
    weights=np.sqrt(np.array(weights))
    array0nw = array0n * weights[None,:]
    array1nw = array1n * weights[None,:]
    #find similarity
    sim = laplacian_kernel(array0nw,array1nw)
    #print(sim.shape) # all_tracks x input_tracks


    return sim, list_pk, list_pk_all

# def save_similar_tracks(tracks=None, features=None):
#     from tracks.models import Track
#     find_similar_tracks(tracks=tracks, features=features)
#     for it in range(len(tracks)):
#         t=Track.objects.get(pk=list_index_pk[it])
#         logger.info("Saving %s" %t.name_wo_path_wo_ext)
#         t.td.track_indices=list(list_index_pk.values())
#         t.td.track_similarities=list(sim[it,:])
#         t.td.save()

def collect_track_infos(features, tracks):
    logger.info("collect_track_infos")
    from tracks.models import Track

    #print(len(tracks), len(features))
    array = np.zeros([len(tracks), len(features)])


    list_index_pk = []
    for it, t in enumerate(tracks):
        list_index_pk.append(t.pk)
        for jf, f in enumerate(features):
            try:
                value = float(getattr(t, f, 0))
                if np.isnan(value):
                    value = 0
            except:
                value = float(0)

            # print(value)
            array[it, jf] = value

    return array, list_index_pk


def rolling_quantity(q, n_rolling=30, min_periods=10,mult_by=1):
    logger.debug("rolling_quantity")
    import pandas as pd
    df = pd.DataFrame({"q": q})
    df2 = df.rolling(int(n_rolling), min_periods=int(min_periods),center=True).mean()
    df2 = df2.bfill()
    # should remove nan but not works
    if mult_by !=1:
        df2=df2*mult_by
    ret = df2["q"].where((pd.notnull(df2["q"])), None)
    #ret=list(ret)
    #ret = [ x if x is not None and not np.isnan(x) else None for x in ret ]
    return ret

def rolling_speed(x, t, n_rolling=30, min_periods=10,diff_x=True,diff_t=True,only_positive=True):
    """diff_x if x is cumulated; diff_t if y is cumulated"""
    if not x or not t:
        return []
    try:
        logger.debug("rolling_speed")
        import pandas as pd
        # fix lengths
        if len(x)<len(t):
            t=t[0:len(x)]
        elif len(t)<len(x):
            x=x[0:len(t)]
        # then go on
        df = pd.DataFrame({"x": x, "t": t})
        if diff_x:
            df["dx"] = df["x"].diff()
        else:
            df["dx"] = df["x"]
        if diff_t:
            df["dt"] = df["t"].diff()
        else:
            df["dt"] = df["t"]
        df2 = df.rolling(int(n_rolling), min_periods=int(min_periods),center=True).sum()
        df2["v"] = df2["dx"] / df2["dt"]
        df2 = df2.bfill()
        df2.replace([np.inf, -np.inf], 0,inplace=True)
        if only_positive:
            df2[df2 < 0] = 0
        return df2["v"].where((pd.notnull(df2["v"])), None)
    except:
        logger.error("len(x):%s, len(t):%s" %(len(x),len(t)))
        import traceback
        traceback.print_exc()
        return pd.DataFrame()


def get_sub_indices(a,b,ignore_not_subset=True):
    """
    b must be a subset of a
    return the indices of a that give b
    if b is not subset of a, only take the part of b that is subset
    """
    try:
        if len(set(b)-set(a))>0:
            if ignore_not_subset:
                logger.info("%s %s %s %s" %(len(set(a)),len(set(b)),len(set(a-b)),len(set(b-a))))
                logger.warning("get_sub_indices, b not included in a, reducing b to a subset of a (OK if using starting and ending index)")
                b=[x for x in b if x in a]
        if len(set(b)-set(a))>0:
            logger.error("get_sub_indices, b not included in a: %s" %(set(b) - set(a)))
            return list()
        index_dict = dict((value, idx) for idx,value in enumerate(a))
        #print ("ok get_sub_indices")
        return [index_dict[x] for x in b]
    except:
        return []








def get_options():
    options={
        "Ordinal number":{"feature_name":"number", "feature_color":"color", "feature_label":"Ordinal number","decimals":0},
        "Date":{"feature_name":"time", "feature_color":"", "feature_label":"Date","feature_radius":""},
        "Duration":   {"feature_name":"duration_duration", "feature_color":"duration_duration_color",
                        "feature_label":"Duration", "feature_formatted":"duration_duration_string2",
                        "feature_radius":"duration_duration_radius","decimals":-1,
                        "feature_rank":"duration_duration_rank","has_total":1,"is_time":1},
        "Length":{"feature_name":"length_length_km", "feature_color":"length_length_km_color",
                    "feature_label":"Length(km)", "feature_formatted":"length_length_string",
                    "feature_radius":"length_length_km_radius",
                    "feature_rank":"length_length_rank","decimals":2,
                    "feature_symbol":"km","has_total":1},
        "Speed":{"feature_name":"speed_speed_kmh", "feature_color":"speed_speed_kmh_color", "feature_label":"Speed(km/h)",
                    "feature_formatted":"speed_speed_string","feature_radius":"speed_speed_kmh_radius","decimals":1,
                    "feature_rank":"speed_speed_rank","feature_symbol":"km/h"},
        "Pace":{"feature_name":"pace_pace", "feature_color":"pace_pace_color", "feature_label":"Pace",
                    "feature_formatted":"pace_pace_string","feature_radius":"pace_pace_radius","decimals":2,
                    "feature_rank":"pace_pace_rank","feature_symbol":"min/km","decimals":-1,"is_time":1},
        # "Pace":{"feature_name":"", "feature_color":"", "feature_label":"Pace(min/km)",
        #             "feature_formatted":"pace_pace_string","feature_radius":"","decimals":1,
        #             "feature_symbol": "min/km"},
        "Min Altitude":{"feature_name":"min_alt", "feature_color":"min_alt_color", "feature_label":"Min Altitude(m)",
                        "decimals":0,"feature_radius":"min_alt_radius",
                        "feature_rank":"min_alt_rank","feature_symbol":"m"},
        "Max Altitude":{"feature_name":"max_alt", "feature_color":"max_alt_color", "feature_label":"Max Altitude(m)",
                        "decimals":0,"feature_radius":"max_alt_radius",
                        "feature_rank":"max_alt_rank","feature_symbol":"m"},
        "Frequency":{"feature_name":"total_frequency", "feature_color":"total_frequency_color",
                        "feature_label":"Frequency (steps per min)","decimals":0,"feature_radius":"total_frequency_radius",
                        "feature_rank": "total_frequency_rank"},
        "Heartrate":{"feature_name":"total_heartrate", "feature_color":"total_heartrate_color",
                        "feature_label":"Heartrate (bpm)","unit":"bpm","decimals":0,"feature_radius":"total_heartrate_radius",
                        "feature_rank": "total_heartrate_rank"},
        "Heartrate Group":{"feature_name":"total_heartrate_group", "feature_color":"total_heartrate_color_group",
                        "feature_label":"Heartrate (bpm)","decimals":-1,"feature_formatted":"total_heartrate_group"},
        "Calories":{"feature_name":"total_calories", "feature_color":"total_calories_color",
                    "feature_label":"Calories","decimals":0,"feature_radius":"total_calories_radius",
                    "feature_rank": "total_calories_rank","has_total":1},
        "Step Length":{"feature_name":"total_step_length", "feature_color":"total_step_length_color",
                        "feature_label":"Step Length(m)","decimals":2,"feature_radius":"total_step_length_radius",
                        "feature_rank": "total_step_length_rank","feature_symbol":"m"},
        "Total steps":{"feature_name":"total_steps", "feature_color":"total_steps_color", "feature_label":"Total Steps",
                        "feature_radius":"total_steps_radius",
                        "feature_rank": "total_steps_rank","has_total":1},
        "Delta Altitude":{"feature_name":"delta_alt", "feature_color":"delta_alt_color",
                            "feature_label":"Delta Altitude(m)","decimals":0,"feature_radius":"delta_alt_radius",
                        "feature_rank": "delta_alt_rank","feature_symbol":"m","has_total":1},
        "cm per Beat":{"feature_name":"cmeters_per_beat", "feature_color":"cmeters_per_beat_color",
                        "feature_label":"cm per beat", "feature_formatted":"","feature_radius":"","decimals":1,
                        "feature_rank": "cmeters_per_beat_rank","feature_symbol":"cm"},
        "Steps per beat":{"feature_name":"steps_per_beat", "feature_color":"steps_per_beat_color",
                        "feature_label":"Steps per beat", "feature_formatted":"","feature_radius":"","decimals":2,
                        "feature_rank": "steps_per_beat_rank"},
        "Uphill":{"feature_name":"uphill", "feature_color":"uphill_color",
                        "feature_label":"Uphill","decimals":0,"feature_radius":"",
                        "feature_rank": "uphill_rank","feature_symbol":"m","has_total":1},
        "Downhill":{"feature_name":"downhill", "feature_color":"downhill_color",
                        "feature_label":"Downhill","decimals":0,"feature_radius":"",
                        "feature_rank": "downhill_rank","feature_symbol":"m","has_total":1},
        "Year":{"feature_name":"year", "feature_color":"year_color", "feature_label":"","decimals":0,"feature_radius":""},
        "City":{"feature_name":"end_city", "feature_color":"end_city_color", "feature_label":"","feature_radius":""},
        "Country":{"feature_name":"end_country", "feature_color":"end_country_color", "feature_label":"","feature_radius":""},
        "Month":{"feature_name":"month", "feature_color":"month_color", "feature_label":"Month", "feature_formatted":"month","feature_radius":""},
        "Activity Type":{"feature_name":"activity_type", "feature_color":"activity_type_color", "feature_label":"", "feature_formatted":"","feature_radius":""},
    }
    return options

def format_feature(value, feature):
    value=float(value)
    ov = get_options()[feature]

    if "decimals" in ov:
        n_dec = ov["decimals"]
    else:
        n_dec = 0
    if n_dec==-1:
        n_dec=0
    
    format_string = "{:." + str(n_dec) + "f}"

    if "is_time" in ov and ov["is_time"]:
        formatted_value = format_minutes(value)
    else:
        formatted_value = format_string.format(value)
    if "feature_symbol" in ov:
        formatted_value += ov["feature_symbol"]

    return formatted_value

def format_minutes(minutes):
    ## H:M:S
    if minutes>=60:
        return str(int(minutes // 60))\
            + ":"\
            + "{:02}".format(int(minutes % 60))\
            + ":"\
            + "{:02}".format(int(math.modf(minutes)[0] * 60))
    # H:M
    else:
        return "{:02}".format(int(minutes % 60))\
        + ":"\
        + "{:02}".format(int(math.modf(minutes)[0] * 60))

def format_minutes_hm(minutes):
    ## H:M
    return str(int(minutes // 60))\
        + ":"\
        + "{:02}".format(int(minutes % 60))\

def format_minutes_ms(minutes):
    ## M:S
    return "{:02}".format(int(minutes))\
        + ":"\
        + "{:02}".format(int(math.modf(minutes)[0] * 60))

def to_int(a):
    try:
        return int(a)
    except:
        return -1

def to_float_or_zero(a, default=None):
    if a is None:
        return default
    if math.isnan(a) or np.isinf(a):
        return default
    else:
        try:
            return float(a)
        except:
            return default





def get_cardio_colors():
    return {"colors":["#4caf50", " #d4e157","#afb42b", " #ffa726 ",
                      #"#f44336",
                      "#800080",
                      " #FF0000 "],
            "thresholds":[0.5,0.6,0.7,0.8,0.9],
            "labels":["<50% MHR","50%-60% MHR","60%-70% MHR","70%-80% MHR","80%-90% MHR",">90% MHR"]}

def get_cardio_zone(x, mhr):
    d = get_cardio_colors()
    colors=d["colors"]
    ts=d["thresholds"]
    labels=d["labels"]

    try:
        if x<mhr*ts[0]:
            return [colors[0],labels[0]]
        elif x<mhr*ts[1]:
            return [colors[1],labels[1] ]
        elif x < mhr * ts[2]:
            return [colors[2], labels[2]]
        elif x<mhr*ts[3]:
            return [colors[3],labels[3] ]
        elif x < mhr * ts[4]:
            return [colors[4],labels[4] ]
        else :
            return [colors[5], labels[5]]
    except:
        return["",""]



import collections

def flatten(d, parent_key='', sep='_'):
    """https://stackoverflow.com/questions/6027558/flatten-nested-dictionaries-compressing-keys"""
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def add_colors(objects, features, steps=256, steps_legend=9,colorscale=None):
    """add colors to a list of dicts according to a given feature"""

    grades={}
    legends = {}
    details_legend = {}
    for f in features:

        feature=f.split(";")[0]
        try:
            how=f.split(";")[1]
        except:
            how="number"
        array=[a[feature] if feature in a.keys() else None for a in objects ]
        ## time in minutes:
        # above one hour, H:M, otherwise M:S
        if how=="time_m":
            try:
                if max([a for a in array if a])>60:
                    how="time_hm"
                else:
                    how="time_ms"
            except:
                how="time_hm"
            details_legend[feature]=how

        if not colorscale:
            colorscale=OptionSet.get_option("COLORSCALE_RANKS")
            #print(colorscale)
        f_colors, f_grades, colors_legend = numbers_to_colors(array, colorscale, steps=steps,steps_legend=steps_legend,how=how)
        for i,object in enumerate(objects):
            object.update({feature+"_color":f_colors[i]})
        fn = feature+"_color"
        grades[fn]=f_grades
        legends[fn] = colors_legend

    grades["total_heartrate_color_group"]=get_cardio_colors()["labels"]
    legends["total_heartrate_color_group"] = get_cardio_colors()["colors"]

    return {"grades":grades,"colors_legend":legends,"details_legend":details_legend}


def add_radius(objects, features, min_radius=2, max_radius=15):
    """add point size to a list of dicts according to a given feature"""

    for f in features:
        feature=f.split(";")[0]
        try:
            how=f.split(";")[1]
        except:
            how="number"
        array=[a[feature] if feature in a.keys() else None  for a in objects]
        if how=="number":
            radius = numbers_to_radius(array, min_radius=min_radius, max_radius=max_radius)
            for i,object in enumerate(objects):
                object.update({feature+"_radius":radius[i]})

def numbers_to_radius(array, min_radius=2, max_radius=15):
    from numpy import percentile
    import numpy as np

    try:
        min_array = np.percentile([a for a in array if a], 5)
        max_array = np.percentile([a for a in array if a], 95)
        # assign a step to each point, between 0 and steps
        radius = [number_to_radius(a,max_array) for a in array]
    except:
        import traceback
        #traceback.print_exc()
        radius = [None for a in array]


    return radius

def number_to_radius(a,max_array, min_radius=2, max_radius=15):
    import math
    if a:
        a=max(a,0)
        r=max(min(max_radius * np.sqrt(a / max_array), max_radius), min_radius)
        if not math.isnan(r):
            return r
        else:
            return min_radius
        #radius = [max(min(max_radius * np.sqrt(min_array + a / delta), max_radius), min_radius) if a else min_radius for a in array]
    else:
        return min_radius

# def find_near_tracks_point(lat_p, long_p, distance):
#     """find tracks close to a point"""
#     from .models import Track
#     distance=float(distance)
#     lat_p=float(lat_p)
#     long_p = float(long_p)
#     import time
#     start = time.time()
#
#     import decimal
#     tracks = Track.objects.all().exclude(avg_lat__isnull=True). \
#         exclude(avg_long__isnull=True). \
#         exclude(avg_lat=decimal.Decimal('NaN')). \
#         exclude(avg_long=decimal.Decimal('NaN')).\
#         exclude(groups__exclude_from_search=True)
#     ids = np.squeeze(np.array(tracks.values_list('id')))  # squeeze remove the ,1 dimension
#     lats = np.squeeze(np.array(tracks.values_list('avg_lat')))
#     long = np.squeeze(np.array(tracks.values_list('avg_long')))
#
#     dists= distance_lat_long(lats, lat_p,long,long_p)
#     ok_indices = dists < distance
#
#     #extract ok tracks
#     dists=dists[ok_indices]
#     ids = ids[ok_indices]
#     # order by dist
#     ordered_indices = np.argsort(dists)
#     dists= dists[ordered_indices]
#     ids = ids[ordered_indices]
#
#     tracks=[]
#     for dist,i in zip(dists, ids):
#         track=Track.objects.get(pk=int(i))
#         track.distance=dist
#         tracks.append(track)
#
#     end = time.time()
#     logger.info("find_near_tracks_point: %s s" %(end - start))
#     #tracks.sort(key=lambda x: x.distance, reverse=False) #already done in np
#     return tracks

def loosen_bounds(bounds):
    if "min_lat" in bounds and bounds["min_lat"] is not None:
        min_lat=bounds["min_lat"]-0.01
    else:
        min_lat=1000
    if "min_lat" in bounds and bounds["max_lat"] is not None:
        max_lat = bounds["max_lat"] + 0.01
    else:
        max_lat=-1000
    if "min_lat" in bounds and bounds["min_long"] is not None:
        min_long = bounds["min_long"] - 0.01
    else:
        min_long=1000
    if "min_lat" in bounds and bounds["max_long"] is not None:
        max_long = bounds["max_long"] + 0.01
    else:
        max_long=-1000
    return {
            "min_lat":min_lat,
            "max_lat": max_lat,
            "min_long": min_long,
            "max_long": max_long,
    }

def refresh_properties(tracks):
    logger.info("refresh_properties")
    for t in tracks:
        logger.info("refresh_properties %s" % t)
        t.set_all_properties()
    logger.info("end refresh_properties")


