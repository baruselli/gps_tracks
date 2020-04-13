import numpy as np
import math
import os
from pprint import pprint
from datetime import datetime
from django.urls import reverse
import logging
logger = logging.getLogger("gps_tracks")
import traceback
from tracks.models import Track
from .models import Group
from tracks.utils import get_colors


def cluster(n_clusters):
    import numpy as np
    from sklearn.cluster import KMeans
    import decimal

    # n_clusters=np.min((n_clusters,len(tracks_new)))

    logger.info("Parsing centers of tracks")
    centers = []
    list_of_tracks = []
    for track in (
        Track.objects.exclude(avg_lat__gte=1000)
        .exclude(avg_lat__lte=-1000)
        .exclude(avg_long__gte=1000)
        .exclude(avg_long__lte=-1000)
    ):  # ugly to exlude nan
        if track.avg_lat is not None and track.avg_long is not None:
            centers.append([track.avg_lat, track.avg_long])
            list_of_tracks.append(track)
    # print(centers)
    logger.info("tracks found: " + str(len(centers)))

    cent_np = np.array(centers)

    logger.info("Doing K means")
    kmean = KMeans(init="k-means++", n_clusters=n_clusters, n_init=10, random_state=1)
    kmean.fit(cent_np)
    # print(kmean.labels_)

    logger.info("Saving")
    # Group.objects.all().delete()

    import matplotlib
    from matplotlib import cm

    from options.models import OptionSet
    colorscale=OptionSet.get_option("COLORSCALE_LISTS")
    cmap = cm.get_cmap(colorscale, n_clusters)
    col_groups = [matplotlib.colors.rgb2hex(cmap(i)[:3]) for i in range(cmap.N)]

    for n in range(n_clusters):
        g, created = Group.objects.get_or_create(number=n)
        g.avg_lat = kmean.cluster_centers_[n, 0]
        g.avg_long = kmean.cluster_centers_[n, 1]
        g.size = 0
        g.n_waypoints = 0
        g.total_points = 0
        g.color = col_groups[n]
        g.save()
        g.set_attributes()

    for track, label in zip(list_of_tracks, kmean.labels_):
        group = Group.objects.filter(number=label).first()  # number is univocal
        track.group = group
        group.size += 1
        group.total_points += track.n_points
        group.n_waypoints += track.n_waypoints
        group.save()
        track.save()

    # print ("Setting track colors")
    # for g in Group.objects.all():
    #     if(g.size>0):
    #         size=g.size
    #         cmap = cm.get_cmap('gist_rainbow', size )
    #         col_groups=[matplotlib.colors.rgb2hex(cmap(i)[:3])for i in range(cmap.N)]
    #         for i,track in enumerate(Track.objects.filter(group=g)):
    #             track.color=col_groups[i]
    #             track.save()

