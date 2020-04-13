import numpy as np
import scipy.spatial
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
import logging
logger = logging.getLogger("gps_tracks")
from numpy import sin, cos, sqrt, arctan2, radians, pi, arcsin


def distance_lat_long2(p1, p2):
    """https://www.movable-type.co.uk/scripts/latlong.html"""

    R = 6373.0

    if p1[0] is None or p1[1] is None or p2[0] is None or p2[1] is None:
        return None

    lat1 = p1[0]
    lon1 = p1[1]
    lat2 = p2[0]
    lon2 = p2[1]

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * arctan2(sqrt(a), sqrt(1 - a))

    return R * c

def distance_lat_long2_simplified(p1, p2):
    """Equirectangular approximation"""

    R = 6373.0

    lat1 = p1[0]
    lon1 = p1[1]
    lat2 = p2[0]
    lon2 = p2[1]

    x = (lon2 - lon1) * cos((lat2 + lat1)/2)
    y = lat2 - lat1

    c = sqrt(x**2+y**2)

    # c=sqrt(((lon2 - lon1) * cos((lat2 + lat1)/2))**2+(lat2 - lat1)**2)

    return R * c

def distance_lat_long2_simplified2(p1, p2):
    """polar coordinate flat-earth formula"""

    R = 6373.0

    # lat1 = p1[0]
    # lon1 = p1[1]
    # lat2 = p2[0]
    # lon2 = p2[1]

    t1=pi/2-p1[0]
    t2=pi/2-p2[0]

    c = np.nan_to_num(sqrt(t1**2+t2**2-2*t1*t2*cos(p1[1]-p2[1])),0)

    return R * c


def cluster_points(coords,max_d=0.05):
    """Cluster points according to maximum distance (in km) in each cluster;
    in input is a list of 2d lists (==points)"""

    try:
        logger.debug("cluster_points :%s" % (str(coords.shape)))
    except:
        logger.debug("cluster_points :%s" % (str(len(coords))))
    #print(coords)
    import time
    start=time.time()

    p1 = radians(np.array(coords))
    # TODO: make this faster
    #dists = scipy.spatial.distance.cdist(p1, p1, metric=distance_lat_long2)
    #dists = scipy.spatial.distance.cdist(p1, p1, metric=distance_lat_long2_simplified)
    dists = scipy.spatial.distance.cdist(p1, p1, metric=distance_lat_long2_simplified2)
    #dists = scipy.spatial.distance.cdist(p1, p1)
    t1=time.time()
    logger.debug("cdist :%s" % (t1 - start))
    # sometimes diagonal is not zero
    np.fill_diagonal(dists,0)
    # sometimes dists is not symmetric
    dists = (dists + dists.T)/2
    # convert the redundant n*n square matrix form into a condensed nC2 array
    distArray = scipy.spatial.distance.squareform(dists)
    t2=time.time()
    logger.debug("squareform :%s" % (t2 - t1))
    Z = linkage(distArray,
                method='complete',  # dissimilarity metric: max distance across all pairs of
                )
    t3=time.time()
    logger.debug("linkage :%s" % (t3 - t2))

    clusters = fcluster(Z, max_d, criterion='distance')

    end=time.time()
    logger.debug("fcluster :%s" % (end - t3))
    logger.info("Clustering :%s" %(end-start))
    return clusters

def json_to_cluster(input_json,feature="cluster"):
    """from a json, returns one item for each cluster"""

    import numpy as np
    cluster_json = {}
    colors = {}

    for p in input_json:
        cluster = p[feature]
        if cluster not in cluster_json:
            #print(cluster)
            cluster_json[cluster] = {"elements": []}
        cluster_json[cluster]["elements"].append(p)

    for cluster in cluster_json:
        elements=cluster_json[cluster]["elements"]

        cluster_json[cluster]["n_elements"]=len(elements)

        lons = [e["geometry"]["coordinates"][0] for e in elements if e["geometry"]["coordinates"][0] is not None]
        lats=[e["geometry"]["coordinates"][1] for e in elements if e["geometry"]["coordinates"][1] is not None]

        if lons:
            avg_lon = np.nanmean(lons)
        else:
            avg_lon=None
        if lats:
            avg_lat = np.nanmean(lats)
        else:
            avg_lat=None

        cluster_json[cluster]["geometry"]={"coordinates":[avg_lon,avg_lat],"type":"Point"}

        features_to_copy_in_array=["link","url_path","name","time","alt","description","lat","long","thumbnail_url_path"]

        for f in features_to_copy_in_array:
            cluster_json[cluster][f] = []
            for e in elements:
                if f in e:
                    cluster_json[cluster][f].append(e[f])

        features_to_copy_once=["type","point_type"]

        for f in features_to_copy_once:
            if f in elements[0]:
                cluster_json[cluster][f]=elements[0][f]

    cluster_json_ok=[]
    for  cluster in cluster_json:
        cluster_json_ok.append(cluster_json[cluster])

    return cluster_json_ok
