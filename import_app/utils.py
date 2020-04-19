import numpy as np
import math
import os
from tracks.models import *
from pprint import pprint
from datetime import datetime
from django.urls import reverse
import logging
logger = logging.getLogger("gps_tracks")
import numpy as np
import math
from pprint import pprint
import traceback
from blacklists.models import Blacklist
from users.models import Profile
from logger.models import Log
from photos.models import Photo


def generate_tracks(dir_, extensions=[".kmz", ".kml", ".gpx", ".csv", ".tcx"], update=False,import_new_extensions=False,files=None,ignore_blacklist=False):

    logger.info("Generate tracks")
    if files is None:
        files = find_files_in_dir(dir_, extensions)
    generated_tracks=from_files_to_tracks(files, update,ignore_blacklist=ignore_blacklist,import_new_extensions=import_new_extensions)
    logger.info("End Generate tracks")
    return generated_tracks

def generate_tracks_by_prefix(dir_,prefix, update=False):

    logger.info("Generate tracks by prefix")
    files = find_files_in_dir_by_prefix(dir_, prefix)
    from_files_to_tracks(files, update,ignore_blacklist=True)
    logger.info("End generate tracks by prefix")

def from_files_to_tracks(files, update=False,import_new_extensions=False,ignore_blacklist=False, manual_upload=False):
    """Creates a list of tracks from a list of files"""
    import os

    import time
    start = time.time()

    logger.info("From files to tracks")
    logger.info("files %s, update %s,import_new_extensions %s,ignore_blacklist %s,manual_upload %s"\
        %(len(files),update,import_new_extensions,ignore_blacklist,manual_upload ))
    
    # to be returned
    generated_tracks=[]

    # for logging
    generated_tracks_names = []
    updated_tracks_names = []
    file_probably_exists = []
    blacklisted_files = []

    reimport_single_track = len(files)==1 and update==True and ignore_blacklist==True and manual_upload==False

    if not reimport_single_track:
        existing_files_0= Track.all_objects.all().values_list("name_wo_path_wo_ext","extension")
        existing_files={t[0]:t[1] for t in existing_files_0}

    for file in files:


        logger.debug("Doing %s" %file)

        name_simple = os.path.splitext(os.path.split(file)[-1])[0]
        extension = os.path.splitext(file)[1]

        ##Blacklist
        # first check non regex names
        non_regex_names=Blacklist.objects.all().filter(interpret_regex=False).values_list("file_name",flat=True)
        file_is_blacklisted=name_simple in non_regex_names
        # then regex ones
        if not file_is_blacklisted:
            import re
            regex_names = Blacklist.objects.all().filter(interpret_regex=True).values_list("file_name", flat=True)
            for regex_name in regex_names:
                if re.search(regex_name,name_simple):
                    file_is_blacklisted=True
                    break

        if not ignore_blacklist and file_is_blacklisted:
            logger.debug("File %s is blacklisted. Stop here" %file)
            blacklisted_files.append(file)
            continue

        # # tries to find the track in DB
        # query = Track.objects.filter(name_wo_path_wo_ext=name_simple).first()
        # file_exists = query is not None
        # if file_exists:
        #     logger.info("File exists")
        #     ext_exists = extension in query.extension
        #     if not ext_exists:
        #         logger.info("File exists, but not with given extension")

        # tries to find the track in DB

        if not reimport_single_track:
            file_exists = name_simple in existing_files.keys()
            if file_exists:
                logger.debug("File exists")
                ext_exists = extension in existing_files[name_simple]
                if not ext_exists:
                    logger.info("File %s exists, but not with given extension" %file)
        else:
            file_exists=True

        # try more advanced way to compare names
        fpar = False
        if not file_exists:
            if len(name_simple) > 10 and name_simple.endswith(
                ("_1", "_2", "_3", "_4", "_5", "_6","_7","_8","_9",)
            ):
                name2 = name_simple[:-2]
                if name2 in existing_files.keys():
                    file_probably_exists.append([file])
                    logger.debug("file %s probably_exists as %s" % (file, name2))
                    fpar = True
                if len(name_simple) > 10 and name_simple.endswith(
                    ("__1", "__2", "__3", "__4", "__5", "__6", "__7", "__8", "__9",
                     "(1)", "(2)", "(3)", "(4)", "(5)", "(6)", "(7)", "(8)", "(9)",)
                ):
                    name3 = name_simple[:-3].strip()
                    if name3 in existing_files.keys():
                        file_probably_exists.append([file])
                        logger.debug("file %s probably_exists as %s" % (file, name3))
                        fpar = True
                # fix for Feb_10,_2018_11_37_27_rakov_neve_1577980160410
                # find if exists file ending with _ and 13 numbers
            import re
            r = re.compile(r"_[0-9]{12}$")
            if r.search(name_simple):
                logger.info("Name %s has 12 numbers at the end: checking if it has to be ignored" % (name_simple))
                name3 = name_simple[:-13]
                if name3 in existing_files.keys():
                    file_probably_exists.append([file])
                    logger.info("File %s probably_exists as %s" %(file, name3))
                    fpar = True
            r = re.compile(r"_[0-9]{13}$")
            if r.search(name_simple):
                logger.info("Name %s has 13 numbers at the end: checking if it has to be ignored" % (name_simple))
                name3 = name_simple[:-14]
                if name3 in existing_files.keys():
                    file_probably_exists.append([file])
                    logger.info("File %s probably_exists as %s" %(file, name3))
                    fpar = True

        if fpar:
            continue
        ####


        # # try more advanced way to compare names
        # fpar = False
        # if not file_exists:
        #     if len(name_simple) > 10 and name_simple.endswith(
        #         ("_1", "_2", "_3", "_4", "_5")
        #     ):
        #         name2 = name_simple[:-2]
        #         query2 = Track.objects.filter(name_wo_path_wo_ext=name2).first()
        #         if query2 is not None:
        #             file_probably_exists.append([file, query2.file])
        #             logger.info("file probably_exists %s %s" %(file, query2.file))
        #             fpar = True
        #         if len(name_simple) > 10 and name_simple.endswith(
        #             ("__1", "__2", "__3", "__4", "__5")
        #         ):
        #             name3 = name_simple[:-3]
        #             query3 = Track.objects.filter(name_wo_path_wo_ext=name3).first()
        #             if query3 is not None:
        #                 file_probably_exists.append([file, query3.file])
        #                 logger.info("file probably_exists %s %s" %(file, query3.file))
        #                 fpar = True
        # if fpar:
        #     continue
        # ####

        ## import if :
        # 1) file not exists
        # 2) force update
        # 3) file exists but not with given extension, and I force new extensions

        if (not file_exists or update or (not ext_exists and import_new_extensions) ):

            if file_exists:
                track = Track.all_objects.filter(name_wo_path_wo_ext=name_simple).first()
                if not track.log:
                    log = Log.objects.create(pk=track.pk)
                    track.log = log
                    log.save()
                    track.info("Log created!")
                    track.save()
                if not (track.td):
                    if track.log:
                        track.info("Creating track detail")
                    track.td = TrackDetail.objects.create(pk=track.pk)
                    track.save()
                track.info("----------Updating track----------")

            else:
                try: #just for safety I look for existing track in db
                    track = Track.all_objects.filter(name_wo_path_wo_ext=name_simple).first()
                    track.warning("----------Track %s should not exist but was found with pk %s----------"
                                  %(name_simple,track.pk))
                except:
                    track = Track()
                    track.name_wo_path_wo_ext = name_simple
                    track.file = file
                    track.td = TrackDetail.objects.create(pk=track.pk)
                    track.log = Log.objects.create(pk=track.pk)
                    track.save()
                    track.info("----------Track %s created with pk %s----------" %(track, track.pk))
                    for u in Profile.objects.all():
                        if u.is_default:
                            track.user=u
                            track.info("Assigned user %s" %u)
                            break
                    track.save()

            generated_tracks.append(track)

            if not file_exists:
                generated_tracks_names.append(track.name_wo_path_wo_ext)
            elif file_exists and track.name_wo_path_wo_ext not in updated_tracks_names:
                     updated_tracks_names.append(track.name_wo_path_wo_ext)

        # if the file does not exists, or it exists and I want to update it
            step=1
            track.info("%s - Setting dir, extensions, file" %step)
            step+=1

            track.dir_name = os.path.split(file)[:-1]
            track.name_wo_ext, extension = os.path.splitext(file)
            track.file_name = os.path.split(file)[-1]
            track.enabled = True

            if extension == ".gpx":
                track.gpx_file = file
            elif extension == ".kml":
                track.kml_file = file
            elif extension == ".kmz":
                track.kmz_file = file
            elif extension == ".csv":
                track.csv_file = file
            elif extension == ".tcx":
                track.tcx_file = file

            track.name = track.file_name
            track.save()

            if track.extension:
                if extension not in track.extension.split(","):
                    extension_new=reorder_extension(track.extension + "," + extension)
                    track.extension = extension_new
                    track.file += file
            else:
                track.extension = extension
                track.file = file

            track.save()

            logger.debug (track.name_wo_path_wo_ext)
            track.debug("track.extension global "+ track.extension)
            track.debug("track.extension now "+ extension)

            track.corrected_times=False # to avoid correcting more than once, if fix_times is called elsewhere

            track.info("%s - Reading files" %step)
            step+=1
            try:
                if extension == ".gpx":
                    track.read_gpx()
                elif extension == ".kml":
                    track.read_kml()
                elif extension == ".kmz":
                    track.read_kmz()
                elif extension == ".csv":
                    track.read_csv()
                elif extension == ".tcx":
                    track.read_tcx()
                else:
                    track.error("Unknown extension" + track.extension)
            except Exception as e:
                track.error("Error with track %s: %e" %(track.name,e))

            track.info("End reading files")

            track.info("%s - Set all properties" %step)
            step += 1
            track.set_all_properties()
            #track.set_splits()
            #track.set_laps()
            track.info("%s - Fix times" %step)
            step += 1
            track.fix_times(fake=False)
            # moved inside set_all_properties
            # track.info("%s - Set single geojson" %step)
            # step += 1
            # track.set_track_single_geojson()

            track.save()
            track.td.save()
            track.info("OK " + file)

    end = time.time()

    logger.info("***************************************")
    logger.debug("File probably already existing")
    from pprint import pprint, pformat
    logger.debug(pformat(file_probably_exists))
    logger.debug("Blacklisted files")
    logger.debug(pformat(blacklisted_files))

    logger.info("Created tracks:")
    logger.info(pformat(generated_tracks_names))
    logger.info("Updated tracks:")
    logger.info(pformat(updated_tracks_names))

    logger.info("Elapsed time: %.2fs" %(end-start))

    logger.info("Import Done!")
    logger.info("***************************************")

    logger.info("Updating Groups in background")
    groups=[]
    for t_name in generated_tracks_names+updated_tracks_names: #maybe only generated_tracks_names?
        t=Track.all_objects.get(name_wo_path_wo_ext=t_name)
        for g in t.groups.all():
            if g not in groups and g.auto_update_properties:
                groups.append(g)
    for g in groups:
        logger.info(g)
        import threading
        t = threading.Thread(
            target=g.set_attributes, args=([a for a in updated_tracks_names],)
        )
        t.start()

    logger.info("***************************************")
    return generated_tracks

def find_files_in_dir(dir_, extensions):
    """Automatically finds file in dir and its subdirs"""
    import os

    files = []
    logger.info("find_files_in_dir")
    for root, dirs, filess in os.walk(dir_):
        for file in filess:
            for extension in extensions:
                if file.endswith(extension):
                    files.append(os.path.join(root, file))
    return files

def find_files_in_dir_by_prefix(dir_, prefix):
    """Automatically finds file in dir and its subdirs with name prefix and all extensions"""
    import os

    files = []
    logger.info("find_files_in_dir_by_prefix %s, dir %s" %(prefix,dir_))
    for root, dirs, filess in os.walk(dir_):
        for file in filess:
            if os.path.splitext(file)[0]==prefix:
                files.append(os.path.join(root, file))
    return files

def find_allfiles_in_dir(dir_):
    """Automatically finds file in dir and its subdirs"""
    import os

    files = []
    logger.info("find_allfiles_in_dir")
    for root, dirs, filess in os.walk(dir_):
        for file in filess:
            files.append(os.path.join(root, file))
    return files

def reorder_extension(string):
    logger.debug("reorder_extension")
    list_=string.split(",")
    outlist=",".join(sorted(list_))
    return outlist

def import_photos(path=None, update=False, files=None):
    import os
    from PIL import Image, ExifTags
    from PIL.ExifTags import TAGS, GPSTAGS
    import os
    from datetime import datetime

    logger.info("import_photos")

    logger.info(os.getcwd())

    logger.info("looking for all jpg files...")
    if files is None:
        files = find_files_in_dir(path, ".jpg")

    thumbnail_dir = os.path.join(settings.PHOTOS_DIR, "thumbnails")

    files=[f for f in files if thumbnail_dir not in f]

    logger.info("...found %s files" %len(files))

    imported_photos = []


    all_photos=Photo.objects.all().values_list('name', flat=True)
    logger.info("Found %s photos in database" %len(all_photos))

    # name:full_path
    files_dict_1={os.path.splitext(os.path.split(file)[-1])[0]:file for file in files}
    # full_path:name
    files_dict_2 = {file:os.path.splitext(os.path.split(file)[-1])[0] for file in files}

    if update:
        files_to_import=files_dict_1.values()
    else:
        names_to_import = set(files_dict_1.keys()) - set(all_photos)
        files_to_import = [files_dict_1[a] for a in names_to_import]
        logger.info("Found %s files not in db" % len(files_to_import))

    for file in files_to_import:
        name_simple=files_dict_2[file]

        if update:
            file_exists = name_simple in all_photos
            if file_exists:
                photo = Photo.objects.filter(name=name_simple).first()
            else:
                photo = Photo()
        else:
            photo = Photo()

        if True:
            if update and file_exists:
                logger.info("update photo %s" % file)
            else:
                logger.info("create photo %s" % file)

            photo.url_path = "/static/camera/" + os.path.split(file)[-1]
            photo.name = name_simple
            photo.path = file
            photo.save()
            if not photo.thumbnail:
                photo.create_thumbnail()

            # TAGS
            gps_ok = False
            time_ok = False
            try:
                img = Image.open(file)
                info = img._getexif()
                # save tags in a string
                tags_dict = {TAGS.get(tag, tag): value for tag, value in info.items()}
                str_ = ""
                for key, item in tags_dict.items():
                    str_ += str(key) + ": " + str(item).replace("\x00", "") + "\n"
                photo.info = str_
                logger.debug(photo.info)
                photo.save()
                # GPS, TIME
                for tag, value in info.items():
                    key = TAGS.get(tag, tag)
                    #print(key)
                    if key == "GPSInfo":
                        gpsinfo = {}
                        for k, v in value.items():
                            decode = ExifTags.GPSTAGS.get(k, k)
                            gpsinfo[decode] = v
                        # print(gpsinfo)
                        if "GPSLatitude" in gpsinfo and "GPSLongitude" in gpsinfo:
                            lat = gpsinfo["GPSLatitude"]
                            lat_ok = (
                                lat[0][0] / lat[0][1] / 1.0
                                + lat[1][0] / lat[1][1] / 60.0
                                + lat[2][0] / lat[2][1] / 3600.0
                            )
                            lon = gpsinfo["GPSLongitude"]
                            lon_ok = (
                                lon[0][0] / lon[0][1] / 1.0
                                + lon[1][0] / lon[1][1] / 60.0
                                + lon[2][0] / lon[2][1] / 3600.0
                            )
                            photo.lat = lat_ok
                            photo.long = lon_ok
                            gps_ok=True

                        if "GPSAltitude" in gpsinfo:
                            alt = gpsinfo["GPSAltitude"]
                            alt_ok = alt[0] / alt[1] / 1.0
                            photo.alt = alt_ok

                        ## this uses UTC, so I skip it and use the local time instead
                        # if "GPSTimeStamp" in gpsinfo and "GPSDateStamp" in gpsinfo:
                        #     time = gpsinfo["GPSTimeStamp"]
                        #     date = gpsinfo["GPSDateStamp"]
                        #     year, month, day = date.split(":")
                        #
                        #     datetime_ok =  datetime(
                        #             int(year),
                        #             int(month),
                        #             int(day),
                        #             int(time[0][0]),
                        #             int(time[1][0]),
                        #             int(time[2][0]),
                        #         )
                        #     logger.debug(datetime_ok)
                        #     photo.time = datetime_ok
                        #     time_ok=True


                        photo.save()

                # parse datetime
                if not time_ok:
                    for tag, value in info.items():
                        key = TAGS.get(tag, tag)
                        if key == "DateTimeOriginal":
                            dateinfo = value
                            try:
                                photo.time =  datetime.strptime(dateinfo, "%Y:%m:%d %H:%M:%S")
                                time_ok=True
                            except:
                                pass
                        if key == "DateTime":
                            dateinfo = value
                            try:
                                photo.time = datetime.strptime(dateinfo, "%Y:%m:%d %H:%M:%S")
                                time_ok = True
                            except:
                                pass
                        if key == "DateTimeDigitized":
                            dateinfo = value
                            try:
                                photo.time = datetime.strptime(dateinfo, "%Y:%m:%d %H:%M:%S")
                                time_ok = True
                            except:
                                pass

                warn_message=""
                if time_ok:
                    photo.has_time = True
                else:
                    warn_message+="Time not set!"
                    photo.has_time=False
                if gps_ok:
                    photo.has_gps = True
                else:
                    warn_message += "GPS not set!"
                    photo.has_gps = False
                photo.save()

                if not photo.time_zone:
                    photo.set_timezone()

                if warn_message:
                    logger.warning(warn_message)

                imported_photos.append(photo)

            except Exception as e:
                logger.warning("error " + str(e))

    logger.info("End import_photos")
    return imported_photos




def handle_uploaded_file(files, update=True):
    from tracks.models import Track
    from django.core.files.base import ContentFile
    from django.core.files.storage import default_storage


    logger.info("handle_uploaded_file")
    for f in files:
        file_name = os.path.join(settings.MEDIA_ROOT, (str(f.name)))
        from_files_to_tracks([file_name], update=update, ignore_blacklist=True, manual_upload=True)
        name_simple = os.path.splitext(os.path.split(file_name)[-1])[0]
        logger.info("name simple %s" %name_simple)
        track = Track.all_objects.filter(name_wo_path_wo_ext=name_simple).first()
        if track.log:
            track.info("Handle uploaded file")
        else:
            logger.info("Handle uploaded file")
        logger.info(track.pk)
    return track.pk


def convert_to_gpx(lats,long,alts=[],times=[]):
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
            if lat is not None and lon is not None:
                gpx_segment.points.append(
                    gpxpy.gpx.GPXTrackPoint(
                        lat, lon, elevation=float(alt)
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
    return gpx

def reimport_failed_tracks():
    from django.db.models import Q
    import decimal

    tracks = Track.objects.filter(Q(avg_lat__isnull=True) | Q(avg_long__isnull=True) | Q(avg_lat=0) | Q(avg_long=0) |
                           Q(avg_lat=decimal.Decimal('NaN')) | Q(avg_long=decimal.Decimal('NaN')))

    for t in tracks:
        t.reimport()

def find_duplicated_files(dir_, extensions=[".kmz", ".kml", ".gpx", ".csv", ".tcx"]):
    """
    find files with the same names(which are considered as a single track by us)
    """
    logger.info("find_duplicated_files")
    files=find_files_in_dir(dir_=dir_, extensions=extensions)

    dict_name_files={}

    for file in files:
        base_name=name_wo_path_wo_ext(file)
        if base_name in dict_name_files:
            dict_name_files[base_name].append(file)
        else:
            dict_name_files[base_name]=[file]

    duplicated_files_list=[]
    for name, files in dict_name_files.items():
        names_wo_path = [os.path.basename(f) for f in files]
        # print(names_wo_path,set(names_wo_path))
        if len(set(names_wo_path))!=len(names_wo_path):
            import collections
            duplicated_name_extensions=set([x for x in names_wo_path if names_wo_path.count(x) > 1])
            for name_ext in duplicated_name_extensions:
                duplicated_files=[f for f in files if os.path.basename(f)==name_ext]
                duplicated_files_sizes=[os.stat(f).st_size for f in duplicated_files]
                same_size =all([a==duplicated_files_sizes[0] for a in duplicated_files_sizes])
                duplicated_files_list.append({
                    "name_wo_path":name_ext,
                    "files":[
                        {
                            "name":f,
                            "size": os.stat(f).st_size,
                        } 
                        for f in duplicated_files
                    ],
                    "same_size":same_size
                })

    ## add track infos
    track_names=set([name_wo_path_wo_ext(a["name_wo_path"]) for a in duplicated_files_list])
    
    tracks = Track.all_objects.filter(name_wo_path_wo_ext__in=track_names).only("pk","name_wo_path_wo_ext")
    dict_name_pk={t.name_wo_path_wo_ext: t.pk for t in tracks}

    for d in duplicated_files_list:
        d["track_name"] = name_wo_path_wo_ext(d["name_wo_path"])
        d["track_pk"] = dict_name_pk.get(d["track_name"],None)


    return duplicated_files_list

def name_wo_path_wo_ext(file):
    "file name wo path wo extension"
    base=os.path.basename(file)
    return os.path.splitext(base)[0]