import numpy as np
import math
import os
from tracks.models import Track
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

def convert_to_gpx(lats,long,alts=[],times=[], waypoints=[], segment_indices=[],subtrack_indices=[]):
    """
    https://pypi.org/project/gpxpy/
    TODO: reproduce segments and subtracks
    """
    logger.info("convert_to_gpx")
    import gpxpy
    gpx = gpxpy.gpx.GPX()
    # Create first track in our GPX:
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    # Create first segment in our GPX track:
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)
    assert(len(lats)==len(long))

    # Create points:
    if len(alts)==len(lats) and len(times)==len(lats):
        for lat, lon, alt, time in zip(lats, long, alts, times):
            # print (lat,lon,alt)
            if lat is not None and lon is not None:
                try:
                    alt=float(alt)
                    gpx_segment.points.append(
                        gpxpy.gpx.GPXTrackPoint(
                            lat, lon, time=time, elevation=alt
                        )
                    )
                except:
                    gpx_segment.points.append(
                        gpxpy.gpx.GPXTrackPoint(
                            lat, lon, time=time
                        )
                    )
    elif len(alts)==len(lats):
        for lat, lon, alt in zip(lats, long, alts):
            # print (lat,lon,alt)
            try:
                alt=float(alt)
            except:
                alt=alt
            if lat is not None and lon is not None:
                gpx_segment.points.append(
                    gpxpy.gpx.GPXTrackPoint(
                        lat, lon, elevation=alt
                    )
                )
    elif len(times)==len(lats):
        for lat, lon, time in zip(lats, long, times):
            # print (lat,lon,alt)
            if lat is not None and lon is not None:
                gpx_segment.points.append(
                    gpxpy.gpx.GPXTrackPoint(
                        lat, lon, time=time
                    )
                )
    else:
        for lat, lon in zip(lats, long):
            # print (lat,lon,alt)
            if lat is not None and lon is not None:
                gpx_segment.points.append(
                    gpxpy.gpx.GPXTrackPoint(
                        lat, lon
                    )
                )

    for wp in waypoints:
        gpx.waypoints.append(gpxpy.gpx.GPXWaypoint(
            latitude=wp.lat,
            longitude=wp.long,
            elevation=wp.alt,
            time=wp.time,
            name=wp.name,
            description=wp.description,
            comment=wp.comment,
            ))

    return gpx