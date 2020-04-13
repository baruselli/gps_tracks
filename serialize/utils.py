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


def serialize(obj_list, label="", alltogether=False):
    from itertools import chain
    from django.core import serializers
    from django.contrib.admin.utils import NestedObjects

    import os

    logger.info("Starting Serialization")

    # one file for all (waypoints, photos, groups)
    if alltogether:
        logger.info("One file")
        collector = NestedObjects(using="default")
        collector.collect(obj_list)
        if label != "":
            out_file = label + ".json"
        else:
            obj = obj_list[0]
            if len(obj_list) == 1:
                out_file = obj.__name__.replace(" ", "_") + ".json"
            else:
                out_file = obj.__class__.replace(" ", "_") + ".json"

        out_file = os.path.join(settings.EXPORT_DIR, out_file)
        collector = NestedObjects(using="default")
        collector.collect(obj_list)
        objects = list(chain.from_iterable(collector.data.values()))
        logger.info("Writing to file")
        with open(out_file, "w") as f:
            logger.info(out_file)
            f.write(serializers.serialize("json", objects))
    # one file for each object (tracks)
    else:
        # print("Many files")
        for obj_ in obj_list:
            name = repr(obj_)
            logger.info(name)
            collector = NestedObjects(using="default")
            collector.collect([obj_])
            out_file = name.replace(" ", "_") + ".json"

            out_file = os.path.join(settings.EXPORT_DIR, out_file)
            collector = NestedObjects(using="default")
            collector.collect(obj_list)
            objects = list(chain.from_iterable(collector.data.values()))
            for o in objects:
                logger.debug(o)
            logger.info("Writing to file")
            with open(out_file, "w") as f:
                logger.info(out_file)
                f.write(serializers.serialize("json", objects))
                # f.write(serializers.serialize("json", [obj_,]))

    logger.info("OK Serialization")


def deserialize(file_):
    from django.core import serializers

    logger.info("deserialize")
    with open(file_, "r") as data:
        for deserialized_object in serializers.deserialize("json", data):
            logger.info(deserialized_object.object)
            deserialized_object.save()
