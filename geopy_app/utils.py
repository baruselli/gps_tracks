import numpy as np
import math
import os
from tracks.models import *
from pprint import pprint
from datetime import datetime
from django.urls import reverse
import logging
logger = logging.getLogger("gps_tracks")
import traceback
from options.models import OptionSet

def get_geopy(lat, long):

    if OptionSet.get_option("USE_GEOPY"):
        from geopy.geocoders import Nominatim

        logger.info("get_geopy")
        geolocator = Nominatim(user_agent="gps_tracks")
        lat = float(lat)
        long = float(long)

        language = OptionSet.get_option("LANGUAGE_GEOPY")
        if language:
            language = language.strip()
            location = geolocator.reverse([lat, long], language=language)
        else:
            location = geolocator.reverse([lat, long])

        # formatted string
        address = location.address

        # componenets
        out_dict = location.raw.get("address", {})

        return {
            "address": address,
            "country": out_dict.get("country"),
            "country_code": out_dict.get("country_code"),
            "region": out_dict.get("county")
            or out_dict.get("state_district")
            or out_dict.get("suburb")
            or out_dict.get("state"),
            "city": out_dict.get("village") or out_dict.get("town") or out_dict.get("city"),
        }
    else:
        return {}

def tracks_geopy():
    from tracks.models import Track

    logger.info("tracks_geopy")
    for tr in Track.objects.all():
        if (
            not tr.beg_address
            or not tr.end_address
            or tr.beg_address == ""
            or tr.end_address == ""
        ):
            track_geopy(tr)


def track_geopy(tr):

    logger.info("track_geopy")
    try:
        logger.info("--------------------")
        logger.info(tr.name)
        if len(tr.td.lats) > 0:
            # first point
            tr.info("Set location via geopy")
            location_dict = get_geopy(tr.td.lats[0], tr.td.long[0])
            if location_dict:
                tr.beg_address = location_dict.get("address")
                tr.beg_country = location_dict.get("country")
                tr.beg_region = location_dict.get("region")
                tr.beg_city = location_dict.get("city")
                logger.info(location_dict)
            # last point
            location_dict = get_geopy(tr.td.lats[-1], tr.td.long[-1])
            if location_dict:
                tr.end_address = location_dict.get("address")
                tr.end_country = location_dict.get("country")
                tr.end_region = location_dict.get("region")
                tr.end_city = location_dict.get("city")
                logger.info(location_dict)
            if location_dict:
                tr.info("OK set location")
            else:
                tr.info("Location not set")
            tr.save()
    except Exception as e:
        tr.warning("track_geopy "+str(e))


def photo_geopy(photo):
    try:
        logger.info("photo_geopy "+ photo.name)
        if photo.lat and photo.long and photo.lat != 0 and photo.long != 0:
            location_dict = get_geopy(photo.lat, photo.long)
            photo.address = location_dict.get("address")
            photo.country = location_dict.get("country")
            photo.region = location_dict.get("region")
            photo.city = location_dict.get("city")
            logger.info(photo.address)
            photo.save()
        elif (
            photo.deduced_lat
            and photo.deduced_long
            and photo.deduced_lat != 0
            and photo.deduced_long != 0
        ):
            location_dict = get_geopy(photo.deduced_lat, photo.deduced_long)
            photo.address = location_dict.get("address")
            photo.country = location_dict.get("country")
            photo.region = location_dict.get("region")
            photo.city = location_dict.get("city")
            logger.info(photo.address)
            photo.save()

    except Exception as e:
        logger.warning("photo_geopy "+photo.name+" "+str(e))


def photos_geopy():
    from tracks.models import Photo

    logger.info("photos_geopy")
    for photo in Photo.objects.all():
        if not photo.address:
            photo_geopy(photo)

def lines_geopy():
    from tracks.models import Line
    logger.info("lines_geopy")

    for line in Line.objects.all():
        if (
            not line.beg_address
            or not line.end_address
            or line.beg_address == ""
            or line.end_address == ""
        ):
            line_geopy(line)


def line_geopy(line):
    logger.info("line_geopy")
    try:
        logger.info(line.name)
        if len(line.lats) > 1:
            # first point
            location_dict = get_geopy(line.lats[0], line.long[0])
            line.beg_address = location_dict.get("address")
            line.beg_country = location_dict.get("country")
            line.beg_region = location_dict.get("region")
            line.beg_city = location_dict.get("city")
            logger.info(line.beg_address)
            # last point
            location_dict = get_geopy(line.lats[-1], line.long[-1])
            line.end_address = location_dict.get("address")
            line.end_country = location_dict.get("country")
            line.end_region = location_dict.get("region")
            line.end_city = location_dict.get("city")
            line.save()
    except Exception as e:
        logger.warning(str(e))


def waypoint_geopy(wp):
    logger.info("waypoint_geopy")
    try:
        logger.info(wp.name)
        location_dict = get_geopy(wp.lat, wp.long)
        # print(location_dict)
        # print(location_dict.get("country"))
        wp.address = location_dict.get("address")
        wp.country = location_dict.get("country")
        wp.country_code = location_dict.get("country_code")
        wp.region = location_dict.get("region")
        wp.city = location_dict.get("city")
        wp.save()
    except Exception as e:
        logger.warning(str(e))


def waypoints_geopy():
    from waypoints.models import Waypoint
    logger.info("waypoints_geopy")

    for wp in Waypoint.objects.all():
        try:
            if not wp.address or wp.address == "":
                waypoint_geopy(wp)
        except Exception as e:
            logger.warning(str(e))

def track_owm(tr):

    logger.info("track_owm")
    try:
        logger.info("--------------------")
        logger.info(tr.name)
        if len(tr.td.lats) > 1:
            # first point
            tr.info("Set weather via owm")
            location_dict = get_geopy(tr.td.lats[0], tr.td.long[0])
            tr.beg_address = location_dict.get("address")
            tr.beg_country = location_dict.get("country")
            tr.beg_region = location_dict.get("region")
            tr.beg_city = location_dict.get("city")
            logger.info(tr.beg_address)
            # last point
            location_dict = get_geopy(tr.td.lats[-1], tr.td.long[-1])
            tr.end_address = location_dict.get("address")
            tr.end_country = location_dict.get("country")
            tr.end_region = location_dict.get("region")
            tr.end_city = location_dict.get("city")
            tr.info("OK set location")
            tr.save()
    except Exception as e:
        tr.warning("track_geopy "+str(e))

def get_altitude(lat,long):
    """https://stackoverflow.com/a/51064850"""

    logger.info("get_altitude")

    import requests,json
    try:
        query="https://api.open-elevation.com/api/v1/lookup?locations=%s,%s" %(lat,long)
        #{"results   [{"latitude": 41.161758, "elevation": 117, "longitude": -8.583933}]}
        r = requests.get(query).text
        dict_=json.loads(r)
        elevation=dict_["results"][0]["elevation"]
    except Exception as e:
        logger.warning("get altitude "+str(e))
        elevation=0
    logger.info(elevation)
    return(elevation)

# at the moment not used
def get_owm(lat,long,time):
    from options.models import OptionSet
    import pyowm
    owm = pyowm.OWM(OptionSet.get_option("OWM_KEY"))
    logger.debug("get_owm")
    observation = owm.weather_at_place('London,GB')
    w = observation.get_weather()
    #print(w)

    return(w)