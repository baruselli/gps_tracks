import numpy as np
import math
import os
from .models import Track, Photo, TrackDetail, Profile, Log, Blacklist, Waypoint, Line, Group, GeoJsonObject
from pprint import pprint
from datetime import datetime
from django.urls import reverse
import logging
logger = logging.getLogger("gps_tracks")
import numpy as np
import math
from pprint import pprint
import traceback





def convert_to_kml(lats,long,alts=[],times=[],name="kml_file"):
    logger.info("convert_to_kml")
    from simplekml import Kml, Snippet, Types
    kml = Kml(name="Tracks", open=1)
    mtr = kml.newgxmultitrack()
    trk = mtr.newgxtrack(name=name)


    # Create points:
    if len(alts)==len(lats) and len(times)==len(lats):
        for lat, lon, alt, time in zip(lats, long, alts, times):
            trk.newgxcoord([[lon,lat,alt]])
            trk.newwhen([time])

    elif len(alts)==len(lats):
        for lat, lon, alt in zip(lats, long, alts):
            trk.newgxcoord([[lon,lat,alt]])


    elif len(times)==len(lats):
        for lat, lon, time in zip(lats, long, times):
            trk.newgxcoord([[lon,lat]])
            trk.newwhen([time])

    else:
        for lat, lon in zip(lats, long):
            trk.newgxcoord([[lon,lat]])

    return kml