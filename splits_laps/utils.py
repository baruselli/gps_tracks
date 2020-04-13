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
from tracks.utils import get_colors, pace_from_speed
import numpy as np


def track_slices(track,indices,every=None, name="Lap", add_before_after=True):
    """given a list of indices, returns details of each slice"""

    logger.debug("track_slices")

    if indices is None or not indices:
        return []

    if every is None:
        every=track.get_every()

    colors = iter(get_colors(len(indices)-1))

    from copy import deepcopy
    indices_ok=deepcopy(indices)
    if add_before_after:
        indices_ok.insert(0,0) #insert first point
        indices_ok.append(track.n_points) #and last

    #print(indices_ok)

    slices=[]
    for ind,(i,j) in enumerate(zip(indices_ok,indices_ok[1:])):
        logger.debug("i, j %s %s" %(i,j))
        #if j == 0: j = 1
        if j >= len(track.td.times): j = len(track.td.times) - 1
        if i >= len(track.td.times): i = len(track.td.times) - 1

        if track.td.alts:
            alts_i=track.td.alts[i]
            alts_j1=track.td.alts[j-1]
            alts_ij=track.td.alts[i:j]
        else:
            alts_i=0
            alts_j1 = 0
            alts_ij= [0 for a in range(i,j)]

        slice={}
        #scalar quantities

        slice["number"]=ind

        if add_before_after:
            if ind==0:
                slice["name"]="Before"
                slice["color"]="gray"
            elif ind==len(indices_ok)-2:
                slice["name"]="After"
                slice["color"]="gray"
            else:
                slice["name"]=name +" "+ str(ind)
                slice["color"]=next(colors)
        else:
            slice["name"] = name + " " + str(ind+1)
            slice["color"] = next(colors)

        slice["beg_ind"]=i
        slice["fin_ind"]=j-1
        if track.td.times:
            slice["duration"]=track.td.times[j-1]-track.td.times[i]
        else:
            slice["duration"]=0
        if j>0:
            slice["computed_length"]=(track.td.computed_dist[j-1]-track.td.computed_dist[i])/1000
        else:
            slice["computed_length"]=0
        if track.td.times:
            slice["starting_point"]=[track.td.lats[i],track.td.long[i],alts_i,track.td.times[i].replace(tzinfo=None)]
            slice["ending_point"]=[track.td.lats[j-1],track.td.long[j-1],alts_j1,track.td.times[j-1].replace(tzinfo=None)]
        else:
            slice["starting_point"]=[track.td.lats[i],track.td.long[i],alts_i,0]
            slice["ending_point"]=[track.td.lats[j-1],track.td.long[j-1],alts_j1,0]
        if track.td.dist_csv and any(track.td.dist_csv):
            slice["csv_length"]=((track.td.dist_csv[j-1] or 0) - (track.td.dist_csv[i] or 0))/1000
        if track.td.dist_tcx and any(track.td.dist_tcx):
            slice["tcx_length"]=((track.td.dist_tcx[j-1] or 0) - (track.td.dist_tcx[i] or 0))/1000

        #arrays
        slice["times"]=track.td.times[i:j]
        slice["computed_dists_m"]=track.td.computed_dist[i:j]
        slice["computed_dists"]=[a/1000 for a in slice["computed_dists_m"]]
        slice["alts"]=alts_ij
        slice["lats"]=track.td.lats[i:j]
        slice["long"]=track.td.long[i:j]
        slice["speeds"]=track.td.computed_speed_rolling[i:j]
        slice["times_strings"]=track.td.times_string[i:j]
        if track.td.dist_csv:
            slice["csv_dists_m"]=track.td.dist_csv[i:j]
            slice["csv_dists"]=[(a or 0) /1000 for a in slice["csv_dists_m"]]
            slice["dists"]=slice["csv_dists"]
        elif track.td.dist_tcx:
            slice["tcx_dists_m"] = track.td.dist_tcx[i:j]
            slice["tcx_dists"] = [(a or 0) / 1000 for a in slice["tcx_dists_m"]]
            slice["dists"] = slice["tcx_dists"]
        else:
            slice["dists"] = slice["computed_dists"]
        if track.td.frequency_rolling:
            slice["frequencies"]=track.td.frequency_rolling[i:j]
        else:
            slice["frequencies"]=[]
        if track.td.heartbeats:
            slice["heartbeats"]=track.td.heartbeats[i:j]
        else:
            slice["heartbeats"]=[]

        #computed fields
        slice["delta_times"]=[(t-slice["times"][0]).total_seconds() for t in slice["times"]]
        slice["delta_dists"]=[(x-slice["dists"][0]) for x in slice["dists"]]
        try:
            slice["avg_speed"]=slice["computed_length"]/slice["duration"].total_seconds()*3.6*1000
        except:
            slice["avg_speed"]=0
        try:
            slice["avg_pace"]=pace_from_speed(slice["avg_speed"])
        except:
            slice["avg_pace"]=0
        if slice["heartbeats"]:
            try:
                slice["avg_heartbeat"]=np.nanmean(slice["heartbeats"])
            except:
                slice["avg_heartbeat"]=None
        else:
            slice["avg_heartbeat"]=None
        if slice["frequencies"]:
            try:
                slice["avg_frequency"]=np.nanmean(slice["frequencies"])
            except:
                slice["avg_frequency"]=None
        else:
            slice["avg_frequency"]=None

        # every done after computed fields otherwise avg are wrongs
        slice["times"]=slice["times"][::every]
        slice["dists"]=slice["dists"][::every]
        slice["alts"]=slice["alts"][::every]
        slice["lats"]=slice["lats"][::every]
        slice["long"]=slice["long"][::every]
        slice["speeds"]=slice["speeds"][::every]
        slice["times_strings"]=slice["times_strings"][::every]
        slice["frequencies"]=slice["frequencies"][::every]
        slice["heartbeats"]=slice["heartbeats"][::every]
        slice["delta_times"]=slice["delta_times"][::every]
        slice["delta_dists"]=slice["delta_dists"][::every]

        slices.append(slice)

    return slices

def get_reduced_slices(slices):
    reduced_slices=[]
    for slice in slices:
        reduced_slice = {}
        for k,v in slice.items():
            if k not in ["times","dists","alts","lats","long","speeds","times_strings","frequencies",
                         "heartbeats","delta_times","delta_dists","computed_dists_m","csv_dists_m",
                         "csv_dists","computed_dists"]:
                reduced_slice[k]=v
        reduced_slices.append(reduced_slice)
    return reduced_slices

def stats_from_slices(slices,first=None,last=None):
    speeds=[]
    hrs=[]
    freqs=[]
    slices_ok=slices
    if last is not None:
        slices_ok=slices_ok[:last]
    if first is not None:
        slices_ok=slices_ok[first:]

    for s in slices_ok:
        speeds.append(s["avg_speed"])
        hrs.append(s["avg_heartbeat"])
        freqs.append(s["avg_frequency"])

    return ({
        "speeds":speeds,
        "hrs":hrs,
        "freqs":freqs
    })

def get_split_indices(dist_array, n_km=1):
    """returns list of indices for each km"""
    import numpy as np

    logger.info("get_split_indices")
    d = np.array(dist_array)
    d1 = np.diff(d // (1000*n_km))
    indices = np.where(d1 != 0)[0]
    indices=list(indices)
    indices.insert(0,0)
    if indices[-1]!=len(dist_array)-1:
        indices.append(len(dist_array)-1)
    return indices

def distance_lat_long(lat1, lat2, lon1, lon2):
    from math import sin, cos, sqrt, atan2, radians

    #logger.debug("distance_lat_long")
    R = 6373.0
    # approximate radius of earth in km

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

distance_lat_long = np.vectorize(distance_lat_long)

def find_laps(track, time_threshold=300, space_threshold=3, initial_point=None,
              threshold_length=10, min_laps=2, max_laps=100, back_forth=False):
    if back_forth:
        # just divide the track in half according to distance
        # TODO: better algorithm
        indices = get_split_indices(track.td.computed_dist, n_km=track.length_3d / 2 / 1000)
        # you could also get a spurious third lap of almost zero length, delete it
        if len(indices) == 4:
            indices = [indices[0], indices[1], indices[3]]
    else:
        total_list = find_laps_1(
            track=track,
            time_threshold=time_threshold,
            space_threshold=space_threshold,
            initial_point=initial_point,
        )

        indices = find_laps_2(
            total_list=total_list,
            threshold_length=threshold_length / 100,  # in input is %
            min_laps=min_laps,
            max_laps=max_laps,
            track=track,
        )

    laps = track_slices(track, indices)

    if laps:
        message = "%s laps found" % len(laps)
    else:
        message = "Could not find any lap"

    return ({
        "message": message,
        "laps": laps,
        "indices": indices
    })


def find_laps_1(track, time_threshold, space_threshold, initial_point):
    """returns, for each point, a list of all points outside a given time threshold
    (to avoid taking points just a few seconds later)
    and within a given space threshold,
    If no initial_point is given, loop over all points of the track.
    If an initial_point is given [lat,lon], loop over all points close to the initial_point"""

    logger.info("find_laps_1")

    def dt(p1, p2):
        return (p2[2] - p1[2]).total_seconds()

    def dist(p1, p2):
        return distance_lat_long(p1[0], p2[0], p1[1], p2[1]) * 1000

    def is_same_point(p1, p2, threshold):
        return dist(p1, p2) < threshold

    def is_same_point2(p1, p2, threshold, dist):
        return dist < threshold

    # all points

    # find all points close to the initial selection
    if initial_point:
        logger.info("Using initial point %s, %s" % (initial_point[0], initial_point[1]))
        ps = []
        for i, (la, lo, ti) in enumerate(zip(track.td.lats, track.td.long, track.td.times)):
            if is_same_point(initial_point, [la, lo], space_threshold):
                ps.append([la, lo, ti, i])
    else:
        lats = track.td.lats
        long = track.td.long
        times = track.td.times
        ps = [(lat, lon, t, i) for i, (lat, lon, t) in enumerate(zip(lats, long, times))]

    max_ps = 300
    if len(ps) > max_ps:
        every_p = len(ps) // max_ps + 1
    else:
        every_p = 1
    ps = ps[::every_p]
    logger.info("Number of starting points: %s" % len(ps))

    total_list = {}

    for p1 in ps:
        i = p1[3]
        point_list = [i]  # list of points
        dist_list = [0]  # list of distances from first point
        p_new = p1
        for p2 in ps:  # ps_all:
            j = p2[3]
            dist12 = dist(p1, p2)
            if j > i and dt(p_new, p2) > time_threshold and is_same_point2(p1, p2, space_threshold, dist12):
                point_list.append(j)
                dist_list.append(dist12)
                p_new = p2
        total_list[i] = [point_list, dist_list]

    return total_list


def find_laps_2(total_list, threshold_length, min_laps, max_laps, track):
    import numpy as np
    """given the list for each point of all points within a given threshold,
    find the number of laps with conditions:
    1) length of laps must be similar within a hard threshold (default 10%)
    2) maximize number of laps
    3) minimize the distance between initial and ending point of each lap,
    plus the length difference of all laps
    Returns the indices of beginning of each lap
    """
    logger.info("find_laps_2")
    from collections import OrderedDict
    # order by number of loops found for each point
    ordered_list = OrderedDict(sorted(total_list.items(), key=lambda t: -len(t[1][0])))
    # check that the length of each lap is reasonable (within a 10%)
    # otherwise goes to next point
    laps_number = sorted(list(set([len(v[0]) for v in total_list.values()])), reverse=True)
    laps_number_ok = [ln for ln in laps_number if ln >= min_laps and ln <= max_laps]
    # loop over possible lap number
    for ln in laps_number_ok:
        list2 = {}
        for starting_index, other in ordered_list.items():
            all_indices = other[0]
            all_dists = other[1]
            if len(all_indices) == ln:
                #print(all_indices)
                global_dist = [track.td.computed_dist[j] for j in all_indices]
                lap_lengths = [y - x for x, y in zip(global_dist, global_dist[1:])]
                lap_length_variation = (max(lap_lengths) - min(lap_lengths)) / np.mean(lap_lengths)
                if lap_length_variation < threshold_length:
                    list2[starting_index] = [all_indices, lap_lengths, lap_length_variation, all_dists]

        # if I find laps within the given threshold, I choose here the best one
        if list2:
            # list3 contains, for each starting point, the lap length variation and the distance between initial points
            list3 = {}
            for ind, other in list2.items():
                all_indices = other[0]
                lap_length_variation = other[2]
                all_dists = other[3]

                list3[ind] = [lap_length_variation, np.mean(all_dists)]

            # here I normalize to 1
            max_llv = max(a[0] for a in list3.values())
            max_mad = max(a[1] for a in list3.values())
            # and sum the two contributions
            list4 = {a: b[0] / max_llv + b[1] / max_mad for a, b in list3.items()}
            # then I take the smallest one
            import operator
            final_index = min(list4.items(), key=operator.itemgetter(1))[0]

            indices_ok = list2[final_index][0]
            logger.info("Returning %s" % indices_ok)
            return indices_ok

            # def find_laps_3(result,track):
            #     results_ok={}
            #     """given the results from find_laps_2, returns all the laps with their details"""

            #     #result[0] contains the indices corresponding to the beginning of each lap
            #     results_ok["n_laps"]=len(result[0])-1
            #     #result[1] contains the lengths of each lap
            #     results_ok["lengths"]=result[1]

            #     points=[]
            #     for ind in result[0]:
            #         points.append([track.td.lats[ind],track.td.long[ind]])
            #     results_ok["points"]=points

            #     laps=[]
            #     durations=[]
            #     for ind1,ind2 in zip (result[0],result[0][1:]):
            #         durations.append(track.td.times[ind2]-track.td.times[ind1])
            #         #for ind in range(ind1,ind2):



            #     results_ok["durations"]=durations


            #     return results_ok