from .models import Line
import numpy as np
import math
import os
from pprint import pprint
from datetime import datetime
from django.urls import reverse
import logging
logger = logging.getLogger("gps_tracks")
import traceback


def create_line(lats,long,alts=[],name="line"):
    from .models import Line
    line,created=Line.objects.get_or_create(name=name)
    line.lats = lats
    line.long = long
    line.alts = alts
    line.n_points=len(lats)
    line.lats_text = str(lats)[1:-1]
    line.long_text = str(long)[1:-1]
    line.alts_text = str(alts)[1:-1]
    line.save()
    if created:
        logger.info("Created line %s from track" %line.pk)
    else:
        logger.info("Modified line %s from track" %line.pk)

    return line,created
