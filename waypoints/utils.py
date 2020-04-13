from tracks.models import Track
from .models import Waypoint
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
from tracks.utils import to_int
from django.db.models import Q

def find_near_tracks(waypoint, distance):
    """find tracks close to a waypoint"""

    logger.info("find_near_tracks")
    lat_wp = waypoint.lat
    long_wp = waypoint.long

    from tracks.utils import filter_tracks
    tracks = filter_tracks({"lat":lat_wp, "long":long_wp, "distance":distance})
    return tracks

# def find_near_waypoints_point(lat_p, long_p, distance):
#     """find waypoints close to a point"""
#     distance=float(distance)
#     lat_p=float(lat_p)
#     long_p = float(long_p)
#     import time
#     start = time.time()
#     import decimal
#     from tracks.utils import distance_lat_long
#     from math import  radians
#
#     #logger.debug("distance_lat_long")
#
#     # old solution
#     # waypoints = Waypoint.objects.all().exclude(lat__isnull=True). \
#     #     exclude(long__isnull=True). \
#     #     exclude(lat=decimal.Decimal('NaN')). \
#     #     exclude(long=decimal.Decimal('NaN'))
#     # ids = np.squeeze(np.array(waypoints.values_list('id')))  # squeeze remove the ,1 dimension
#     # lats = np.squeeze(np.array(waypoints.values_list('lat')))
#     # long = np.squeeze(np.array(waypoints.values_list('long')))
#
#     from django.db.models.functions import Sin, Cos, ATan2, Sqrt, Power, Radians
#     from django.db.models import F
#     R = 6373.0
#     lat_p = radians(lat_p)
#     long_p = radians(long_p)
#
#     # approximate formula, easiest to implement
#     # x = (lon2 - lon1) * cos((lat2 + lat1) / 2)
#     # y = lat2 - lat1
#     # c = sqrt(x ** 2 + y ** 2)
#     waypoints =Waypoint.objects.\
#         exclude(lat__isnull=True). \
#         exclude(long__isnull=True). \
#         exclude(lat=decimal.Decimal('NaN')). \
#         exclude(long=decimal.Decimal('NaN')). \
#         annotate(latrad=Radians("lat")). \
#         annotate(lonrad=Radians("long")). \
#         annotate(dlon=F("lonrad") - long_p). \
#         annotate(dlat=F("latrad") - lat_p). \
#         annotate(latavg=(F("latrad") + lat_p)/2). \
#         annotate(x=F("dlon")*Cos(F("latavg"))). \
#         annotate(c=Sqrt(Power("x",2) + Power("dlat",2))). \
#         annotate(d=R*F("c")). \
#         filter(d__lte=distance)
#
#     #print(waypoints)
#
#     # t1=pi/2-p1[0]
#     # t2=pi/2-p2[0]
#     #
#     # c = np.nan_to_num(sqrt(t1**2+t2**2-2*t1*t2*cos(p1[1]-p2[1])),0)
#
#
#     # dlon = lon2 - lon1
#     # dlat = lat2 - lat1
#     # a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
#     # c = 2 * atan2(sqrt(a), sqrt(1 - a))
#
#     # dists= distance_lat_long(lats, lat_p,long,long_p)
#     # ok_indices = dists < distance
#     #
#     # #extract ok waypoints
#     # dists=dists[ok_indices]
#     # ids = ids[ok_indices]
#     # # order by dist
#     # ordered_indices = np.argsort(dists)
#     # dists= dists[ordered_indices]
#     # ids = ids[ordered_indices]
#     #
#     # waypoints = []
#     # for dist,i in zip(dists, ids):
#     #     waypoint=Waypoint.objects.get(pk=int(i))
#     #     waypoint.distance=dist
#     #     waypoints.append(waypoint)
#
#     end = time.time()
#     logger.info("find_near_waypoints_point: %s s" %(end - start))
#     return waypoints

def filter_waypoints(request, silent=True):
    """filter waypoints given a get request"""
    from django.db.models import Q

    import time
    start = time.time()

    lat = request.get('lat', None)
    long = request.get('lng', None)
    distance = request.get('dist', None)
    how_many = request.get('how_many',None)
    n_days = request.get('n_days', None)
    year = request.get('year', None)
    country = request.get('country', None)
    by_id = request.get('by_id', None)
    name = request.get('name',None)
    min_date = request.get('min_date',None)
    max_date = request.get('max_date', None)
    q = request.get('q', None)
    wps_ids = request.get('wps_ids', None)
    group_pk = request.get('group_pk', None)
    track_ids=request.get("track_ids",None)
    no_search = request.get('no_search', None)
    time_zone = request.get('time_zone', None)
    address = request.get('address', None)

    if no_search:
        return Waypoint.objects.none()

    waypoints=None

    # when i selest track, group, or Waypoint, I use an or, instead of the usual and
    if group_pk:
        group_pk=int(group_pk)
        waypoints=Waypoint.objects.filter(track__groups__id=group_pk) | Waypoint.objects.filter(track2__groups__id=group_pk)

    if track_ids:
        t_ids = [int(a) for a in track_ids.split("_")]
        waypoints_track=Waypoint.objects.filter(track__in=t_ids) | Waypoint.objects.filter(track2__in=t_ids)
        if waypoints is None:
            waypoints = waypoints_track
        else:
            waypoints = waypoints | waypoints_track

    if wps_ids:
        ids=[int(id) for id in wps_ids.split("_")]
        waypoints_by_ids = Waypoint.objects.filter(pk__in=ids)
        if waypoints is None:
            waypoints = waypoints_by_ids
        else:
            waypoints = waypoints | waypoints_by_ids

    if waypoints is None:
        waypoints = Waypoint.objects.all()

    # from now on, filtering is done as an AND
    from datetime import datetime, timedelta
    today = datetime.today()

    if lat and long and distance:
        import decimal
        from django.db.models.functions import Radians
        initial_queryset=   waypoints. \
            exclude(lat__isnull=True). \
            exclude(long__isnull=True). \
            exclude(lat=decimal.Decimal('NaN')). \
            exclude(long=decimal.Decimal('NaN')). \
            annotate(latrad=Radians("lat")). \
            annotate(lonrad=Radians("long"))

        from tracks.utils import filter_queryset_by_distance
        waypoints = filter_queryset_by_distance(
            initial_queryset,
            lat=lat,
            long=long,
            distance=distance
        )

    if n_days:
        n_days=int(n_days)
    if n_days==-1:
        waypoints = waypoints.filter(time__isnull=True)
    elif n_days:
        waypoints = waypoints.filter(time__lte=today).filter(time__gte=today-timedelta(days=n_days))
    else:
        pass

    if year:
        year=int(year)
        waypoints = waypoints.filter(time__year=year)

    if country=="None":
        waypoints = waypoints.filter(
                                Q(country__isnull=True)| Q(country="")
                              )
    elif country:
        waypoints = waypoints.filter(country=country)

    if by_id:
        by_id=int(by_id)
        waypoints = waypoints.order_by("-pk")[:by_id]

    if name:
        waypoints = waypoints.filter(name__icontains=name)

    if min_date:
        min_date=datetime.strptime(min_date,"%Y-%m-%d").date()
        waypoints=waypoints.exclude(time__isnull=True).filter(time__gte=min_date)
    if max_date:
        max_date = datetime.strptime(max_date, "%Y-%m-%d").date()
        waypoints=waypoints.exclude(time__isnull=True).filter(time__lte=max_date)

    if q:
        waypoints = waypoints.filter(Q(description__icontains=q)|
                                               Q(comment__icontains=q))

    if address:
        waypoints = waypoints.filter(
            Q(country__icontains=address)|
            Q(region__icontains=address)|
            Q(city__icontains=address)|
            Q(address__icontains=address)
        )

    if time_zone:
        waypoints=waypoints.filter(time_zone=time_zone)

    if how_many:
        how_many = int(how_many)
        waypoints = waypoints[:how_many]

    end = time.time()
    if not silent:
        logger.info("filter_waypoints: %.3f s" %(end - start))

    return waypoints