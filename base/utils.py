import json
import urllib
import logging
logger = logging.getLogger("gps_tracks")


def get_coords_from_ip():
    try:
        external_ip = json.load(urllib.request.urlopen("http://ipinfo.io/json"))
        logger.debug(external_ip)
        lat, long = external_ip["loc"].split(",")
        address = external_ip["city"] + ", " + external_ip["region"] + ", " + external_ip["country"]
    except:
        lat, long = 0, 0
        address = None
    logger.info("%s %s" % (lat, long))
    return lat, long, address
