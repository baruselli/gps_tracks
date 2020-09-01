from .models import Photo
from tracks.models import Track
from groups.models import Group
from django.urls import reverse
from options.models import OptionSet
import logging
logger = logging.getLogger("gps_tracks")
import numpy as np
from django.db.models import Q
# def find_near_photos_point(lat_p, long_p, distance):
#     """find photos close to a point"""
#     distance=float(distance)
#     lat_p=float(lat_p)
#     long_p = float(long_p)
#     import time
#     start = time.time()
#     import decimal
#     from tracks.utils import distance_lat_long
#
#     ## using the original lat long
#     photos = Photo.objects.all().exclude(lat__isnull=True). \
#         exclude(long__isnull=True). \
#         exclude(lat=decimal.Decimal('NaN')). \
#         exclude(long=decimal.Decimal('NaN'))
#     ids = np.squeeze(np.array(photos.values_list('id')))  # squeeze remove the ,1 dimension
#     lats = np.squeeze(np.array(photos.values_list('lat')))
#     long = np.squeeze(np.array(photos.values_list('long')))
#
#     dists= distance_lat_long(lats, lat_p,long,long_p)
#     ok_indices = dists < distance
#
#     #extract ok photos
#     dists=dists[ok_indices]
#     ids = ids[ok_indices]
#     # order by dist
#     ordered_indices = np.argsort(dists)
#     dists1= dists[ordered_indices]
#     ids1 = ids[ordered_indices]
#
#     ## by deduced coords
#     photos = Photo.objects.all().exclude(deduced_lat__isnull=True). \
#         exclude(deduced_long__isnull=True). \
#         exclude(deduced_lat=decimal.Decimal('NaN')). \
#         exclude(deduced_lat=decimal.Decimal('NaN'))
#     ids = np.squeeze(np.array(photos.values_list('id')))  # squeeze remove the ,1 dimension
#     lats = np.squeeze(np.array(photos.values_list('deduced_lat')))
#     long = np.squeeze(np.array(photos.values_list('deduced_long')))
#
#     dists= distance_lat_long(lats, lat_p,long,long_p)
#     ok_indices = dists < distance
#
#     #extract ok photos
#     dists=dists[ok_indices]
#     ids = ids[ok_indices]
#     # order by dist
#     ordered_indices = np.argsort(dists)
#     dists2= dists[ordered_indices]
#     ids2 = ids[ordered_indices]
#
#     # merge the two queries
#     dists=[*dists1,*dists2]
#     ids = [*ids1, *ids2]
#
#     photos = []
#     for dist,i in zip(dists, ids):
#         photo=Photo.objects.get(pk=int(i))
#         photo.distance=dist
#         if photo not in photos:
#             photos.append(photo)
#
#     end = time.time()
#     logger.info("find_near_photos_point: %s s" %(end - start))
#     return photos

def filter_photos(request, silent=True):
    """filter photos given a get request"""

    from django.db.models import Q
    from datetime import datetime, timedelta
    import time
    start = time.time()

    today = datetime.today()

    lat = request.get('lat', None)
    long = request.get('lng', None)
    distance = request.get('dist', None)
    how_many = request.get('how_many',None)
    n_days = request.get('n_days', None)
    year = request.get('year', None)
    country = request.get('country', None)
    address = request.get('address', None)
    by_id = request.get('by_id', None)
    name = request.get('name',None)
    min_date = request.get('min_date',None)
    max_date = request.get('max_date', None)
    q = request.get('q', None)
    photo_ids = request.get('photo_ids', None)
    group_pk=request.get("group_pk",None)
    track_ids=request.get("track_ids",None)
    no_search = request.get('no_search', None)
    time_zone = request.get('time_zone', None)

    if no_search:
        return Photo.objects.none()

    photos=None

    # when i selest track, group, or photo, I use an or, instead of the usual and
    if group_pk:
        group_pk=int(group_pk)
        photos=Photo.objects.filter(tracks__groups__id=group_pk)

    if track_ids:
        t_ids = [int(a) for a in track_ids.split("_")]
        photos_track=Photo.objects.filter(tracks__in=t_ids)
        if photos is None:
            photos = photos_track
        else:
            photos = photos | photos_track

    if photo_ids:
        ids=[int(id) for id in photo_ids.split("_")]
        photos_by_ids = Photo.objects.filter(pk__in=ids)
        if photos is None:
            photos = photos_by_ids
        else:
            photos = photos | photos_by_ids

    if photos is None:
        photos = Photo.objects.all()

    ## at this point, I filter what i have by the other filters
    if lat and long and distance:
        import decimal
        from django.db.models.functions import Radians
        from tracks.utils import filter_queryset_by_distance

        initial_queryset_1 = photos. \
            exclude(lat__isnull=True). \
            exclude(long__isnull=True). \
            exclude(lat=decimal.Decimal('NaN')). \
            exclude(long=decimal.Decimal('NaN')). \
            annotate(latrad=Radians("lat")). \
            annotate(lonrad=Radians("long"))

        photos_1 = filter_queryset_by_distance(
            initial_queryset_1,
            lat=lat,
            long=long,
            distance=distance
        )

        initial_queryset_2 = photos. \
            exclude(deduced_lat__isnull=True). \
            exclude(deduced_long__isnull=True). \
            exclude(deduced_lat=decimal.Decimal('NaN')). \
            exclude(deduced_long=decimal.Decimal('NaN')). \
            annotate(latrad=Radians("deduced_lat")). \
            annotate(lonrad=Radians("deduced_long"))

        photos_2 = filter_queryset_by_distance(
            initial_queryset_2,
            lat=lat,
            long=long,
            distance=distance
        )

        photos = photos_1 | photos_2

        #photos = find_near_photos_point(lat, long, distance)

    if n_days:
        n_days=int(n_days)
    if n_days==-1:
        photos = photos.filter(time__isnull=True)
    elif n_days:
        photos = photos.filter(time__lte=today).filter(time__gte=today-timedelta(days=n_days))
    else:
        pass

    if year:
        if year=="None":
            photos = photos.filter(time__isnull=True)
        else:
            year=int(year)
            photos = photos.filter(time__year=year)

    if country=="None":
        photos = photos.filter(
                                Q(country__isnull=True)| Q(country="")
                              )
    elif country:
        photos = photos.filter(country=country)

    if by_id:
        by_id=int(by_id)
        photos = photos.order_by("-pk")[:by_id]

    if address:
        photos = photos.filter(
            Q(country__icontains=address)|
            Q(region__icontains=address)|
            Q(city__icontains=address)|
            Q(address__icontains=address)
        )

    if name:
        photos = photos.filter(name__icontains=name)

    if min_date:
        min_date=datetime.strptime(min_date,"%Y-%m-%d").date()
        photos=photos.exclude(time__isnull=True).filter(time__date__gte=min_date)
    if max_date:
        max_date = datetime.strptime(max_date, "%Y-%m-%d").date()
        photos=photos.exclude(time__isnull=True).filter(time__date__lte=max_date)


    if q:
        photos = photos.filter(Q(description__icontains=q)|
                               Q(address__icontains=q)|
                               Q(info__icontains=q))

    if how_many:
        how_many = int(how_many)
        photos = photos[:how_many]

    if time_zone:
        photos=photos.filter(time_zone=time_zone)

    end = time.time()
    if not silent:
        logger.info("filter_photos: %.3f s" %(end - start))

    return photos

def associate_photos_to_tracks(photo_list=None, track_list=None):
    """associates a track to a photo based on datetime.
        if the photo already has a track, it skips it"""
    logger.info("associate_photos_to_tracks")
    logger.info("collecting track info")

    if track_list is None:
        track_list = Track.objects.filter(beginning__isnull=False,end__isnull=False)
    else:
        logger.info("using tracks:")
        logger.info([t.name_wo_path_wo_ext for t in track_list])

    if photo_list is None:
        photo_list = Photo.objects.filter(time__isnull=False)
    else:
        if isinstance(photo_list, list):
            photo_list=Photo.objects.filter(pk__in=[p.pk for p in photo_list]).exclude(time__isnull=True)
        logger.info("using photos:")
        logger.info([p.name for p in photo_list])

    logger.info("doing associations")

    counter= 0
    counter_new = 0

    from options.models import OptionSet
    how = OptionSet.get_option("LINK_PHOTOS_TO_TRACKS")

    for track in track_list:
        counter_track=0
        counter_track_new=0
        if not track.beginning or not track.end:
            track.photos_details="No linking performed because beginning and/or end are missing"
            track.save()
            continue

        if how=="same_day":
            photo_list_track=photo_list.filter(time__date=track.beginning.date())|photo_list.filter(time__date=track.end.date())
        elif how=="beginning_end":
            photo_list_track=photo_list.filter(time__gte=track.beginning,time__lte=track.end)
        else: # same as same_day, should not happen
            photo_list_track=photo_list.filter(time__date=track.beginning.date())|photo_list.filter(time__date=track.end.date())

        for photo in photo_list_track:
            # time = photo.time
            # for track, beginning, end, lat, long in zip(
            #         track_list, beginning_list, end_list, lat_list, long_list
            # ):
            #     if how=="same_day":
            #         condition = (time.date() == beginning.date()) or (time.date() == end.date())
            #     elif how=="beginning_end":
            #         condition = time > beginning and time < end
            #     if condition:
            if not track in photo.tracks.all():
                counter_new+=1
                counter_track_new+=1
            photo.tracks.add(track)
            photo.track_pk = track.id
            photo.track_name = track.name_wo_path_wo_ext
            if not photo.time_zone:
                photo.set_timezone()
            deduce_lat_long(photo, track)
            deduce_city(photo, track)
            photo.save()
            counter += 1
            counter_track += 1
            track.info("Added photo %s - %s to track %s" % (photo.pk, photo.name, track.name_wo_path_wo_ext))
            # photo_list.remove(photo)

        from datetime import datetime
        track.photos_details="Found %s photos, of which %s new, as of %s" %(counter_track, counter_track_new,datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        track.save()

    message="Associations found %s: %s; new : %s" % (how,counter,counter_new)
    logger.info(message)
    return message

def deduce_lat_long(photo,track):
    """gives location to photo from times of the track points"""
    # don't set if track is from google history, and I already have deduced_lat
    google_timeline=Group.objects.filter(name="Google timeline").first()
    times = track.td.times 
    if google_timeline and google_timeline in track.groups.all() and photo.deduced_lat:
        return
    if not times:
        return

    try:
        # if time is outside bounds, take first or last point
        if not photo.deduced_lat:
            if photo.time.replace(tzinfo=None)<times[0].replace(tzinfo=None):
                photo.deduced_lat = track.td.lats[0]
                photo.deduced_long = track.td.long[0]
                if track.td.alts and track.td.alts[0]:
                    photo.deduced_alt = track.td.alts[0]
                photo.save()
                return
            if photo.time.replace(tzinfo=None)>times[-1].replace(tzinfo=None):
                photo.deduced_lat = track.td.lats[-1]
                photo.deduced_long = track.td.long[-1]
                if track.td.alts and track.td.alts[-1]:
                    photo.deduced_alt = track.td.alts[-1]
                photo.save()
                return

        # in general, look for points close in time
        for i,t in enumerate(times):
            if photo.time.replace(tzinfo=None) < t.replace(tzinfo=None):
                dt1=(photo.time.replace(tzinfo=None)-times[i-1].replace(tzinfo=None)).total_seconds()
                dt2 =  (times[i].replace(tzinfo=None) - photo.time.replace(tzinfo=None)).total_seconds()
                d1=dt1/(dt1+dt2)
                d2 = dt2/(dt1 + dt2)
                photo.deduced_lat=track.td.lats[i]*d1+track.td.lats[i-1]*d2
                photo.deduced_long = track.td.long[i]*d1 + track.td.long[i - 1]*d2
                if track.td.alts:
                    photo.deduced_alt=track.td.alts[i]*d1+track.td.alts[i-1]*d2
                photo.save()
                return
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.warning("Error in deduce_lat_long: %s. photo.time %s, time0 %s time1 %s" %(e,photo.time, times[0],times[1]))

def deduce_city(photo,track):

    # address got by geopy->more reliable than from track
    if photo.address:
        return

    # use google timeline only if fields are empty
    google_timeline=Group.objects.filter(name="Google timeline").first()
    if google_timeline and google_timeline in track.groups.all() and photo.country:
        return

    # copy fields
    if track.end_country:
        photo.country = track.end_country
    elif track.beg_country:
        photo.country = track.beg_country
    if track.end_region:
        photo.region = track.end_region
    elif track.beg_region:
        photo.region = track.beg_region
    if track.end_city:
        photo.city = track.end_city
    elif track.beg_city:
        photo.city = track.beg_city
    photo.save()
