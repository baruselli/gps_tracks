import json
import urllib
import logging
logger = logging.getLogger("gps_tracks")


def get_coords_from_ip(cached=False):

    ok_cached=False
    from options.models import OptionSet
    lat_cached= OptionSet.get_option("DEFAULT_LAT")
    long_cached= OptionSet.get_option("DEFAULT_LNG")
    # try to keep cached values if requested
    if cached:
        if lat_cached and long_cached:
            logger.info("Using cached default_lat and default_long")
            ok_cached = True
            lat=lat_cached
            long=long_cached
            address=None

    # if cached values are not requested or they are zero, use the webservice
    if not cached or not ok_cached:
        try:
            logger.info("Querying http://ipinfo.io/json")
            external_ip = json.load(urllib.request.urlopen("http://ipinfo.io/json"))
            logger.debug(external_ip)
            lat, long = external_ip["loc"].split(",")
            address = external_ip["city"] + ", " + external_ip["region"] + ", " + external_ip["country"]
            # if cached values are 0, then save found values in cache
            if not (lat_cached and long_cached):
                logger.info("Saving default_lat and default_long in cache")
                OptionSet.set_option("DEFAULT_LAT", lat)
                OptionSet.set_option("DEFAULT_LNG", long)
        except:
            lat, long = lat_cached, long_cached
            address = None
    logger.info("%s %s" % (lat, long))
    return lat, long, address
