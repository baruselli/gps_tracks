from django.db import models
from django.contrib.postgres.fields import ArrayField
# from django.contrib.gis.db import models as gismodels
# from djgeojson.fields import PointField
import gpxpy
import gpxpy.gpx
import json
import os
from django.urls import reverse
import logging
from pprint import pprint
from photos.models import Photo
from groups.models import Group
from users.models import Profile
from waypoints.models import Waypoint
from logger.models import Log
from django.conf import settings
#from constance import config as settings
from options.models import OptionSet
import numpy as np
from .utils import get_colors
from django.core.serializers.json import DjangoJSONEncoder

logger = logging.getLogger("gps_tracks")

class TrackManagerDefault(models.Manager):
    def get_queryset(self):
        return super(TrackManagerDefault, self).get_queryset().filter(is_active=True)

class TrackManagerBase(models.Manager):
    def get_queryset(self):
        return super(TrackManagerBase, self).get_queryset()


class Track(models.Model):
    # class Meta:
    #     base_manager_name = 'all_objects'

    objects = TrackManagerDefault() #filter out inactive tracks
    all_objects = models.Manager() #TrackManagerBase()
    is_active = models.BooleanField(default=True)
    # file related data
    file = models.CharField(max_length=512,verbose_name="Last File read",null=False, blank=False, unique=False, )
    gpx_file = models.CharField(max_length=512, verbose_name="File gpx", null=True, blank=True, unique=False)
    kml_file = models.CharField(max_length=512, verbose_name="File kml", null=True, blank=True, unique=False)
    kmz_file = models.CharField(max_length=512, verbose_name="File kmz", null=True, blank=True, unique=False)
    csv_file = models.CharField(max_length=512, verbose_name="File csv", null=True, blank=True, unique=False)
    tcx_file = models.CharField(max_length=512, verbose_name="File tcx", null=True, blank=True, unique=False)
    name = models.CharField(max_length=512, verbose_name="Name by user", null=True, blank=True, unique=False)
    dir_name = models.CharField(max_length=512, verbose_name="Directory", null=False, blank=False, unique=False)
    name_wo_ext = models.CharField(max_length=512,verbose_name="Name wo extension",null=False,blank=False,unique=False)
    name_wo_path_wo_ext = models.CharField(max_length=255,verbose_name="name withput path and extension",null=False, blank=False,  unique=True,)
    extension = models.CharField(max_length=40, verbose_name="Extension(s)", null=False, blank=False, unique=False)
    file_name = models.CharField(max_length=512, verbose_name="File name", null=False, blank=False, unique=False)
    created = models.DateTimeField(auto_now_add=True, verbose_name="Date of creation", null=True, blank=True)
    modified = models.DateTimeField(auto_now=True, verbose_name="Date of modification", null=True, blank=True)
    enabled = models.BooleanField(default=True, verbose_name="Enabled for import")
    document = models.FileField(blank=True, null=True)  # for files uploaded by hand
    # geopy info
    beg_country = models.CharField(max_length=50, null=True, blank=True, unique=False, default="")
    beg_region = models.CharField(max_length=100, null=True, blank=True, unique=False, default="")
    beg_city = models.CharField(max_length=50, null=True, blank=True, unique=False, default="")
    beg_address = models.CharField(max_length=250, null=True, blank=True, unique=False, default="")
    end_country = models.CharField(max_length=50, null=True, blank=True, unique=False, default="")
    end_region = models.CharField(max_length=100, null=True, blank=True, unique=False, default="")
    end_city = models.CharField(max_length=50, null=True, blank=True, unique=False, default="")
    end_address = models.CharField(max_length=250, null=True, blank=True, unique=False, default="")
    csv_source = models.CharField(max_length=100, null=True, blank=True, unique=False, default="")
    # original data
    n_points = models.IntegerField(blank=False, null=True)
    n_points_original = models.IntegerField(blank=False, null=False,default=0)
    n_points_gpx = models.IntegerField(blank=False, null=True, default=0)
    n_points_csv = models.IntegerField(blank=False, null=True, default=0)
    n_points_tcx = models.IntegerField(blank=False, null=True, default=0)
    n_points_kml = models.IntegerField(blank=False, null=True, default=0)
    n_tracks = models.IntegerField(blank=False, null=True,default=0)
    n_segments = models.IntegerField(blank=False, null=True,default=0)
    n_tracks_kml = models.IntegerField(blank=False, null=True,default=0)
    n_segments_kml = models.IntegerField(blank=False, null=True,default=0)
    n_laps = models.IntegerField(blank=False, null=True)
    total_dist_csv = models.FloatField(null=True)  # from csv
    total_dist_tcx = models.FloatField(null=True)  # from tcx
    total_pace_csv = models.CharField( max_length=20, null=True)  # from csv
    total_speed_csv = models.FloatField(null=True)  # from csv
    total_speed_tcx = models.FloatField(null=True)  # from csv
    total_speed_kml = models.FloatField(null=True)  # from csv
    total_frequency = models.FloatField(null=True)  # from csv
    total_heartbeat = models.FloatField(null=True)  # from csv
    total_calories = models.FloatField(null=True)  # from csv
    total_step_length = models.FloatField(null=True)  # from csv
    total_steps = models.IntegerField(null=True)  # from csv
    # computed data
    length_2d = models.FloatField(null=True)
    length_3d = models.FloatField(null=True)
    # smoothed data
    length_2d_smooth = models.FloatField(null=True)
    length_3d_smooth = models.FloatField(null=True)
    n_points_smooth = models.IntegerField(blank=False, null=True)
    # smoothed data 2
    length_2d_smooth2 = models.FloatField(null=True)
    length_3d_smooth2 = models.FloatField(null=True)
    n_points_smooth2 = models.IntegerField(blank=False, null=True)
    # smoothed data 3
    length_2d_smooth3 = models.FloatField(null=True)
    length_3d_smooth3 = models.FloatField(null=True)
    n_points_smooth3 = models.IntegerField(blank=False, null=True)
    # other data
    n_waypoints = models.IntegerField(blank=False, null=True, default=0)
    avg_lat = models.FloatField(null=True)
    avg_long = models.FloatField(null=True)
    min_lat = models.FloatField(null=True)
    min_long = models.FloatField(null=True)
    max_lat = models.FloatField(null=True)
    max_long = models.FloatField(null=True)
    min_alt = models.FloatField(null=True)
    max_alt = models.FloatField(null=True)
    avg_alt = models.FloatField(null=True)
    beginning = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)
    duration = models.FloatField(null=True)
    duration_string = models.CharField(max_length=10, null=True)
    duration_string2 = models.CharField(max_length=20, null=True)
    date = models.DateField(null=True)
    year = models.IntegerField(null=True)
    color = models.CharField(max_length=255, verbose_name="Color", null=False, blank=False, unique=False)
    gpx = models.TextField(verbose_name="Gpx", null=True, blank=True, unique=False)
    infos_gpx = models.TextField(verbose_name="Infos Gpx", null=True, blank=True, unique=False)
    csv = models.TextField(verbose_name="Csv", null=True, blank=True, unique=False)
    csv_table = models.TextField(verbose_name="Csv Table", null=True, blank=True, unique=False)
    tcx = models.TextField(verbose_name="Tcx", null=True, blank=True, unique=False)
    kml = models.TextField(verbose_name="Kml", null=True, blank=True, unique=False)
    kmz = models.TextField(verbose_name="Kmz", null=True, blank=True, unique=False)
    infos_tcx = models.TextField(verbose_name="Infos Tcx", null=True, blank=True, unique=False)
    _doc = models.TextField(verbose_name="KML doc", null=True, blank=True, unique=False)
    description = models.TextField(null=True, blank=True, unique=False)
    kml_description = models.TextField(null=True, blank=True, unique=False)
    descr_json = models.TextField(null=True, blank=True, unique=False)
    groups = models.ManyToManyField("groups.Group",through=Group.tracks.through,blank=True)
    photos = models.ManyToManyField("photos.Photo",through=Photo.tracks.through,blank=True)
    # group_activity = models.ForeignKey(
    #     "tracks.Group",
    #     null=True,
    #     blank=True,
    #     on_delete=models.SET_NULL,
    #     related_name="group2",
    # )
    activity_type = models.CharField(max_length=50, null=True)
    length_kml = models.FloatField(null=True)
    moving_time = models.FloatField(null=True)
    stopped_time = models.FloatField(null=True)
    moving_distance = models.FloatField(null=True)
    stopped_distance = models.FloatField(null=True)
    max_speed = models.FloatField(null=True)
    avg_speed = models.FloatField(null=True)
    pace = models.FloatField(null=True)
    pace_string = models.CharField( max_length=50, null=True, blank=True, unique=False, default="" )
    pace_string_tcx = models.CharField( max_length=50, null=True, blank=True, unique=False, default="" )
    pace_string_kml = models.CharField( max_length=50, null=True, blank=True, unique=False, default="" )
    uphill = models.FloatField(null=True)
    downhill = models.FloatField(null=True)
    avg_distance_points = models.FloatField(null=True)
    splits_km = models.FloatField(null=False,blank=False, default=1)
    # splits = models.TextField(null=True, blank=True, unique=False, default="")
    svg_file = models.TextField(null=True, blank=True, unique=False, default="")
    png_file = models.TextField(null=True, blank=True, unique=False, default="")
    gpx_creator =  models.CharField( max_length=200, null=True)  # from gpx
    cardio_0 = models.FloatField(null=True)
    cardio_1 = models.FloatField(null=True)
    cardio_2 = models.FloatField(null=True)
    cardio_3 = models.FloatField(null=True)
    cardio_4 = models.FloatField(null=True)
    cardio_5 = models.FloatField(null=True)
    user_mhr = models.FloatField(null=True)
    max_cardio = models.FloatField(null=True)
    min_cardio = models.FloatField(null=True)
    avg_dist_points = models.FloatField(null=True)
    avg_delta_times = models.FloatField(null=True)
    n_rolling_speed= models.IntegerField(blank=True, null=True,default=60)
    n_rolling_alt = models.IntegerField(blank=True, null=True,default=10)
    n_rolling_freq = models.IntegerField(blank=True, null=True,default=120)
    n_rolling_hr = models.IntegerField(blank=True, null=True,default=1)
    n_rolling_slope = models.IntegerField(blank=True, null=True, default=60)
    min_n_speed= models.IntegerField(blank=True, null=True,default=10)
    min_n_alt = models.IntegerField(blank=True, null=True,default=5)
    min_n_freq = models.IntegerField(blank=True, null=True,default=10)
    min_n_hr = models.IntegerField(blank=True, null=True,default=1)
    min_n_slope = models.IntegerField(blank=True, null=True, default=1)
    has_times = models.BooleanField(default=False)
    has_alts = models.BooleanField(default=False)
    has_hr = models.BooleanField(default=False)
    has_freq = models.BooleanField(default=False)
    starting_index = models.IntegerField(blank=True, null=True,default=0)
    ending_index = models.IntegerField(blank=True, null=True, default=0)
    index_every = models.IntegerField(blank=True, null=True, default=1, verbose_name="Take one point every n in calculations")

    td = models.OneToOneField('TrackDetail',on_delete=models.CASCADE, null=True,related_name="td")
    user = models.ForeignKey(Profile, null=True, blank=True, on_delete=models.SET_NULL)
    has_gx = models.BooleanField(default=False, verbose_name="Has gx tags in kml/kmz")
    json_LD = models.TextField(verbose_name="JSON", null=True, blank=True, unique=False, default="")
    json_properties = models.TextField(verbose_name="JSON properties", null=True, blank=True, unique=False, default="")
    is_merged = models.BooleanField(default=False, verbose_name="Merged from other tracks")
    merged_tracks = models.ManyToManyField("self", blank=True)
    #similarity = models.FloatField(null=True)  # for similarity calcs

    import pytz
    TIMEZONE_CHOICES = [(str(t), str(t)) for t in pytz.common_timezones]
    time_zone=models.CharField(max_length=255, choices=TIMEZONE_CHOICES, default="Europe/Rome")
    corrected_times = models.BooleanField(default=False)

    log = models.OneToOneField(Log,null=True,on_delete=models.CASCADE)

    initial_lat = models.FloatField(null=True)
    initial_lon = models.FloatField(null=True)
    final_lat = models.FloatField(null=True)
    final_lon = models.FloatField(null=True)

    duplicated_group=-1

    # geom =              ArrayField(gismodels.PointField(), size=None,null=True,default=list)

    class Meta:
        verbose_name = "Track"
        ordering = ["date","beginning", "file"]
        #app_label = "tracks"

    def __unicode__(self):
        return self.__repr__()

    def __repr__(self):
        if self.is_active:
            return self.name_wo_path_wo_ext+" (%s)"%self.pk
        else:
            return "[HIDDEN] " + self.name_wo_path_wo_ext+" (%s)"%self.pk

    def __str__(self):
        return self.__repr__()

    def n_photos(self):
        return self.photos.count()

    def set_initial_final_coords(self):
        if self.td.lats and self.td.long:
            self.initial_lat = self.td.lats[0]
            self.initial_lon = self.td.long[0]
            self.final_lat = self.td.lats[-1]
            self.final_lon = self.td.long[-1]
            self.save()

    def find_file(self,ext):
        """
        try to find the import files, in case it has been moved
        """
        from import_app.utils import find_files_in_dir_by_prefix
        file_exists=False
        prop_name=ext+"_file"
        existing_path = getattr(self,prop_name,None)
        if existing_path:
            if os.path.isfile(existing_path):
                file_exists=True
        if file_exists:
            return existing_path
        else:
            self.info("Cannot find input file, trying to search for it...")
            files = find_files_in_dir_by_prefix(settings.TRACKS_DIR, self.name_wo_path_wo_ext)
            for f in files:
                _, extension = os.path.splitext(f)
                if extension.replace(".","")==ext.replace(".",""):
                    setattr(self,prop_name,f)
                    self.save()
                    self.info("..found: %s" %f)
                    return f
            else:
                self.error(".. input file not found.")
                return None

    def set_all_properties(self):
        # if It do not already have a gpx file, I create a gpx obj to use all the utilities of gpxpy
        self.info("set_all_properties")
        step=1
        self.info("_%s - set_initial_final_coords" % step)
        self.set_initial_final_coords()
        self.n_points_original=len(self.td.lats_all)
        self.set_index_every()
        self.save()
        step+=1
        times = self.td.times
        if not ".gpx" in self.extension:
            self.info("_%s - Creating gpx object" %step)
            step+=1
            from import_app.utils import convert_to_gpx
            if times:
                _gpx = convert_to_gpx(self.td.lats, self.td.long, times=times, alts=self.td.alts)
            else:
                _gpx = convert_to_gpx(self.td.lats, self.td.long, alts=self.td.alts)
            self.read_gpx(_gpx=_gpx)
            self.gpx = _gpx.to_xml()
            self.save()
            self.info("End gpx object")

        # set fields common for all extesnions
        self.info("Common infos")
        self.n_points = len(self.td.lats)
        try:
            self.info("_%s - average distance" %step)
            step += 1
            import numpy as np
            self.avg_dist_points = np.median(
                [b - a for a, b in zip(self.td.computed_dist, self.td.computed_dist[1:])])
            self.avg_delta_times = np.median(
                [(b - a).total_seconds() for a, b in zip(times, times[1:])])
            self.save()
        except Exception as e:
            self.warning(str(e) + " cannot set average distance")
            self.avg_dist_points=0
            self.avg_delta_times=0

        if times:
            self.info("_%s - delta_times" %step)
            step += 1
            try:
                initial_time = times[0]
                self.td.delta_times = [(t - initial_time).total_seconds() for t in times]
            except Exception as e:
                self.warning(str(e) + " cannot set delta_times")

        self.info("_%s - times_string" %step)
        step += 1
        try:
            self.td.times_string = [str(t) for t in times]
            self.td.times_string_nodate = [t.strftime("%H:%M:%S") for t in times]
            #the split is to to prevent "0:00:11.960000" and just have "0:00:11"
            self.td.delta_times_string = [str(t - times[0]).split(".")[0] for t in times]
            self.td.save()
        except Exception as e:
            self.warning(str(e) + " cannot set times_string")
        try:
            self.info("_%s - average quantities" %step)
            step += 1
            lats_ok=[l for l in self.td.lats if l is not None]
            lons_ok = [l for l in self.td.long if l is not None]
            alts_ok = [l for l in self.td.alts if l is not None]
            import math
            if lats_ok:
                self.avg_lat = np.median(lats_ok)
                if math.isnan(self.avg_lat):
                    # this works for tracks with only waypoints
                    self.avg_lat = np.median([wp.lat for wp in self.waypoint_set.all() if wp.lat])
                    if math.isnan(self.avg_lat):
                        self.avg_lat=None
            if lons_ok:
                self.avg_long = np.median(lons_ok)
                if math.isnan(self.avg_long):
                    self.avg_long = np.median([wp.long for wp in self.waypoint_set.all() if wp.long])
                    if math.isnan(self.avg_long):
                        self.avg_long=None
            if lats_ok or self.waypoint_set.all():
                self.min_lat = np.min(lats_ok+[wp.lat for wp in self.waypoint_set.all() if wp.lat ])
                self.max_lat = np.max(lats_ok+[wp.lat for wp in self.waypoint_set.all() if wp.lat])
            if lons_ok or self.waypoint_set.all():
                self.min_long = np.min(lons_ok+[wp.long for wp in self.waypoint_set.all() if wp.long])
                self.max_long = np.max(lons_ok+[wp.long for wp in self.waypoint_set.all() if wp.long])
            if alts_ok:
                self.min_alt = np.min(alts_ok)
                self.max_alt = np.max(alts_ok)
                self.avg_alt = np.median(alts_ok)
                if self.min_alt is not None and np.isnan(self.min_alt ):
                    self.min_alt =None
                if self.max_alt is not None and np.isnan(self.max_alt ):
                    self.max_alt =None
                if self.avg_alt is not None and np.isnan(self.avg_alt ):
                    self.avg_alt =None
            self.save()

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.warning("Error set_all_properties set avg quantities: %s" %e)

        self.info("_%s - beginning, end ,length" %step)
        step+=1
        try:
            if times:
                self.beginning = times[0].replace(tzinfo=None)
                self.end = times[-1].replace(tzinfo=None)
            else:
                self.end = None
                self.beginning = None
            if self.beginning and self.end:
                self.duration = (self.end - self.beginning).seconds / 60  # minuti
                self.date = self.beginning.date()
                self.year = self.date.year
                self.debug(self.date)
                self.duration_string = (
                str(int(self.duration // 60)) + "h:" + "{:02}".format(int(self.duration % 60)) + "m")

                import math
                self.duration_string2 = (
                    str(int(self.duration // 60))
                    + "h:"
                    + "{:02}".format(int(self.duration % 60))
                    + "m:"
                    + "{:02}".format(int(math.modf(self.duration)[0] * 60))
                    + "s"
                )
                if self.length_3d:
                    self.avg_speed = self.length_3d / self.duration / 60  # (m/s)
                    self.pace = 1 / 0.06 / self.avg_speed  # (min/km)
                    self.pace_string = (
                        str(int(self.pace))
                        + ":"
                        + "{:02}".format(int((self.pace - int(self.pace)) * 60))
                        + "min/km"
                    )
                self.save()
                self.info("OK beginning, end ,length")
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.warning("Error set_all_properties cannot set beginning, end ,length: %s" %e)

        self.info("End common infos")

        try:
            self.info("_%s - rolling_quantities" %step)
            step += 1
            self.rolling_quantities()
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.warning(str(e))

        try:
            #
            self.info("_%s - set_path_groups" %step)
            step += 1
            self.set_path_groups()
            #
            self.info("_%s - set_activity_group" %step)
            step += 1
            self.set_activity_group()
        except Exception as e:
            self.warning("Error in set_path_groups,set_activity_group: %s"  %e)
        try:
            #
            self.info("_%s - draw_svg" %step)
            step += 1
            self.draw_svg()
            #
            self.info("_%s - draw_png" %step)
            step += 1
            self.draw_png()
        except Exception as e:
            self.warning("Error in draw_svg,draw_png: %s"  %e)
        try:
            #
            self.info("_%s - check_fields" %step)
            step += 1
            self.check_fields()
        except Exception as e:
            self.warning("Error in check_fields: %s"  %e)
        try:
            #
            from geopy_app.utils import track_geopy
            if (not self.beg_address or not self.end_address or self.beg_address == "" or self.end_address == ""):
                self.info("_%s - track_geopy" % step)
                step += 1
                track_geopy(self)
        except Exception as e:
            self.warning("Error in track_geopy: %s"  %e)
        try:
            self.info("_%s - assign_country_to_wps" %step)
            step += 1
            self.assign_country_to_wps()
            #
            self.info("_%s - assign_time_to_wps" %step)
            step += 1
            self.assign_time_to_wps()
        except Exception as e:
            self.warning("Error in assign_country_to_wps,assign_time_to_wps: %s"  %e)
        try:
            #
            self.info("_%s - set_initial_final_coords" %step)
            step += 1
            self.set_initial_final_coords()
            #
            self.info("_%s - set_timezone" %step)
            step += 1
            self.set_timezone()
        except Exception as e:
            self.warning("Error in set_initial_final_coords,set_timezone: %s"  %e)
        try:
            self.info("_%s - set_splits" %step)
            step += 1
            self.set_splits()
            self.info("_%s - set_laps" %step)
            step += 1
            self.set_laps()
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.warning(str(e))

        self.info("_%s - set_json_LD" % step)
        step += 1
        self.set_json_LD(how="all")

        self.info("%s - Set single geojson" %step)
        step += 1
        self.set_track_single_geojson()


        self.save()
        self.td.save()
        self.info("OK set_all_properties")

    def set_splits(self):#TODO: move to app?
        from splits_laps.utils import get_split_indices,stats_from_slices, track_slices, get_reduced_slices
        try:
            if self.n_points>0:
                if self.td.dist_csv and not self.is_merged: 
                    indices = get_split_indices(self.td.dist_csv)
                elif self.td.dist_tcx and not self.is_merged:
                    indices = get_split_indices(self.td.dist_tcx)
                else:
                    indices = get_split_indices(self.td.computed_dist)
                self.debug("split indices: %s" % indices)
                self.td.split_indices = [int(i) for i in indices]
                self.save()
                self.td.save()
                splits = track_slices(self, self.td.split_indices, add_before_after=False, name="Split", every=1)
                splits_stats = stats_from_slices(splits)
                import json
                self.td.splits_stats = json.dumps(splits_stats)
                reduced_splits = get_reduced_slices(splits) #remove array fields
                self.td.splits = str(reduced_splits)
                self.save()
                self.td.save()
            else:
                self.warning("Cannot set splits: n_points=0")
                reduced_splits=[]   
                splits_stats = {}
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.warning("Cannot set splits: %s" %e)
            reduced_splits=[]
            splits_stats = {}
        return {"splits":reduced_splits, "splits_stats": splits_stats}

    def set_laps(self): #TODO: move to app?
        # this simply divides the track in half
        if not self.td.laps_indices or self.td.laps_indices==[0]: # don't overwrite if I have done something by hand!
            from splits_laps.utils import find_laps,stats_from_slices, track_slices, get_reduced_slices
            try:
                if self.n_points>0:
                    laps_indices = find_laps(self, back_forth=True)["indices"]
                    self.td.laps_indices = [int(i) for i in laps_indices]
                    logging.info("laps indices: %s" %self.td.laps_indices)
                    self.save()
                    self.td.save()
                    laps = track_slices(self, self.td.laps_indices, every=1)
                    laps_stats=stats_from_slices(laps)
                    import json
                    self.td.laps_stats = json.dumps(laps_stats)
                    reduced_laps= get_reduced_slices(laps)
                    self.td.laps = str(reduced_laps)
                    self.save()
                    self.td.save()
                else:
                    self.warning("Cannot set laps: n_points=0")
                    reduced_laps=[]   
                    laps_stats = {}
            except Exception as e:
                self.warning("Cannot set laps: %s" % e)
                reduced_laps = []
                laps_stats = {}
            return {"laps": reduced_laps, "laps_stats": laps_stats}

    def check_fields(self):
        if self.td.times:
            self.has_times = True
        else:
            self.has_times = False
        if self.td.alts and any(self.td.alts):
            self.has_alts = True
        else:
            self.has_alts = False
        if self.td.heartbeats and any(self.td.heartbeats):
            self.has_hr = True
        else:
            self.has_hr = False
        if self.td.frequencies  and any(self.td.frequencies):
            self.has_freq = True
        else:
            self.has_freq = False
        self.info("has_times %s, has_alts %s, has_hr %s, has_freq %s"%(self.has_times,self.has_alts, self.has_hr, self.has_freq))
        self.save()


    def get_reduced_fields(self, how="every"):
        """I copy array fields into self.td_* by taking only some points for large tracks.
        Quick and dirty way to reduce loading times when there are too many points
        These fields are not saved in DB, but are attached to the object and
        passed to the template for visualization"""
        self.debug("Reduce points: %s" %how)
        fields={}
        from django.contrib.postgres.fields import ArrayField
        # for f in TrackDetail._meta.get_fields():
        #     if isinstance(f, ArrayField):
                #f_name = f.name
        for f_name in self.td.array_fields_1+self.td.array_fields_2:
                value = getattr(self.td, f_name[1:], []) # f.name[1:] is the getter (without initial _)
                #print (f,len(value), self.n_points)
                print(f_name[1:],len(value),self.n_points)
                if len(value)==self.n_points:
                    new_name="td" +f_name # e.g. td_lats
                    if len(self.td.smooth_indices) and how=="smooth1":
                        fields[new_name]=[value[i] for i in self.td.smooth_indices]
                    elif len(self.td.smooth2_indices) and how=="smooth2":
                        fields[new_name] = [value[i] for i in self.td.smooth2_indices]
                    elif len(self.td.smooth3_indices) and how=="smooth3":
                        fields[new_name] = [value[i] for i in self.td.smooth3_indices]
                    elif how == "all":
                        fields [new_name] = value
                    else:
                        every=self.get_every()
                        fields [new_name] = value[::every]

        return fields


    def add_reduced_fields(self, how="every"):
        """I copy array fields into self.td_* by taking only some points for large tracks.
        Quick and dirty way to reduce loading times when there are too many points
        These fields are not saved in DB, but are passed to the template for visualization"""
        self.info("add_reduced_fields")
        import time
        start = time.time()
        self.debug("Reduce points: %s" %how)
        for key, value in self.get_reduced_fields(how=how).items():
            #print(key)
            setattr(self, key,value)

        end = time.time()
        #self.info("add_reduced_fields: %s" %(end - start))

    def has_only_csv(self,ext="csv"):
        if not self.is_merged:
            return ext in self.extension
        else:
            for t in self.merged_tracks:
                if not ext in t.extension:
                    return False
            return True            

    def get_json_DL(self, how="every",colorscale=None,steps=256,steps_legend=9):
        """Returns json as a dictionary of lists"""
        from .utils import numbers_to_colors, to_float_or_zero
        self.debug("get_json_DL")
        import time
        start = time.time()

        # use fields with filtered points
        self.add_reduced_fields(how=how)

        if self.user:
            mhr = self.user.max_heartrate
        else:
            mhr = 190

        track_json={}
        track_json["type"]="MultiPoint"
        ## number
        if self.n_points>0:
            if hasattr(self , 'td_lats') and self.td_lats:
                track_json["OriginalNumber"] = [i for i,l in enumerate(self.td_lats)]
            else:
                self.error("Does not have lats!")
            ## times
            #if hasattr(self , 'td_times') and self.td_times:
            #    track_json["Time"] = self.td_times
            if hasattr(self , 'td_times_string_nodate') and self.td_times_string_nodate:
                track_json["TimeString"] = self.td_times_string_nodate
            if hasattr(self , 'td_delta_times') and self.td_delta_times:
                track_json["DeltaTime"] = [t/60 for t in self.td_delta_times]
            if hasattr(self , 'td_delta_times_string') and self.td_delta_times_string:
                track_json["DeltaTimeString"] = self.td_delta_times_string
            ## lats long
            if hasattr(self , 'td_lats') and self.td_lats:
                #track_json["Latitude"] = self.td_lats
                #track_json["Longitude"] = self.td_long
                track_json["coordinates"] = [[lo,la] for lo,la in zip(self.td_long,self.td_lats)]
            ## distance
            # has_only_csv, fix for merged track with different extensions, 
            # otherwise a gpx would not have csv_dist and always have zero
            if hasattr(self , 'td_dist_csv') and self.td_dist_csv and not self.is_merged:
                distance = self.td_dist_csv
            elif hasattr(self , 'td_dist_tcx') and  self.td_dist_tcx  and not self.is_merged:
                distance = self.td_dist_tcx
            elif hasattr(self , 'td_computed_dist') and  self.td_computed_dist:
                distance = self.td_computed_dist
            else:
                distance=[0 for a in range(self.n_points)]
            #print("distance", distance)
            track_json["Distance"]=[d/1000 for d in distance]
            track_json["ColorDistance"], track_json["GradesDistance"], track_json["LegendDistance"] = numbers_to_colors(
                track_json["Distance"], colorscale, steps=steps, steps_legend=steps_legend)
            ## speed
            if hasattr(self , 'td_speed_csv') and  self.td_speed_csv:
                speed = self.td_speed_csv
                #track_json["Colors speed"], speed_grades, colors_legend=numbers_to_colors(self.td_speed_csv,colorscale,steps=steps,steps_legend=steps_legend)
                track_json["CSVSpeed"] = speed
            if hasattr(self, "td_computed_speed_rolling") and self.td_computed_speed_rolling:
                computed_speed=[to_float_or_zero(a) for a in self.td_computed_speed_rolling]
                from .utils import pace_from_speed
                computed_pace = [pace_from_speed(a) for a in computed_speed]
            else:
                if self.has_times:
                    # it is OK if it has no times, since time i needed for speed
                    self.warning("Cannot find td_computed_speed_rolling!")
                computed_speed=[0 for a in range(self.n_points)]
                computed_pace = [0 for a in range(self.n_points)]
            #track_json["ComputedSpeed"]=computed_speed
            track_json["ColorSpeed"], track_json["GradesSpeed"], track_json["LegendSpeed"] = numbers_to_colors(computed_speed, colorscale, steps=steps, steps_legend=steps_legend)
            track_json["Speed"] = computed_speed
            track_json["Pace"] = computed_pace
            ## frequency
            if hasattr(self , 'td_frequency_rolling') and  self.td_frequency_rolling:
                track_json["Frequency"]=self.td_frequency_rolling
                track_json["ColorFrequency"], track_json["GradesFrequency"], track_json["LegendFrequency"] = numbers_to_colors(self.td_frequency_rolling, colorscale,
                                                                                steps=steps, steps_legend=steps_legend)
            ## altitude
            if  hasattr(self , 'td_alt_rolling') and   self.td_alt_rolling:
                track_json["Altitude"] = self.td_alt_rolling
                track_json["AltitudeOriginal"] = self.td_alts
                track_json["ColorAltitude"], track_json["GradesAltitude"], track_json["LegendAltitude"]=numbers_to_colors(self.td_alt_rolling,colorscale,steps=steps,steps_legend=steps_legend)
            elif  hasattr(self , 'td_alts') and  self.td_alts:
                track_json["Altitude"] = self.td_alts
                track_json["Altitude - Original"] = self.td_alts
                track_json["ColorAltitude"], track_json["GradesAltitude"], track_json["LegendAltitude"] = numbers_to_colors(self.td_alts, colorscale,steps=steps, steps_legend=steps_legend)
            ## vertical speed
            if hasattr(self , 'td_vertical_speed_rolling') and   self.td_vertical_speed_rolling:
                track_json["VerticalSpeed"] = self.td_vertical_speed_rolling
                track_json["ColorVerticalSpeed"],  track_json["GradesVerticalSpeed"],  \
                    track_json["LegendVerticalSpeed"] = numbers_to_colors(self.td_vertical_speed_rolling, colorscale,steps=steps,
                                                                                    steps_legend=steps_legend,diverging=True)
            ## slope
            if hasattr(self , 'td_slope_rolling') and   self.td_slope_rolling:
                track_json["Slope"] = self.td_slope_rolling
                track_json["ColorSlope"],  track_json["GradesSlope"],  track_json["LegendSlope"] = numbers_to_colors(self.td_slope_rolling, colorscale,steps=steps,
                                                                                    steps_legend=steps_legend,diverging=True)        
            ## step length
            if  hasattr(self , 'td_step_length_rolling') and  self.td_step_length_rolling:
                track_json["StepLength"]= [to_float_or_zero(a) for a in self.td_step_length_rolling]
            ## heartrate
            if  hasattr(self , 'td_heartbeat_rolling') and self.td_heartbeat_rolling:
                track_json["Heartrate"] = [to_float_or_zero(a) for a in self.td_heartbeat_rolling]
                track_json["ColorHeartrate"], track_json["GradesHeartrate"],  track_json["LegendHeartrate"]=numbers_to_colors(self.td_heartbeat_rolling, colorscale,steps=steps,steps_legend=steps_legend)
                from .utils import get_cardio_zone
                track_json["Heartrate Group"] = [get_cardio_zone(a, mhr)[1] for a in self.td_heartbeat_rolling]
                track_json["ColorHeartrate Group"] = [get_cardio_zone(a,mhr)[0] for a in self.td_heartbeat_rolling]
            elif hasattr(self , 'td_heartbeats') and self.td_heartbeats:
                track_json["HeartrateOriginal"] = [to_float_or_zero(a) for a in self.td_heartbeats]
                track_json["Heartrate"] = [to_float_or_zero(a) for a in self.td_heartbeats]
                track_json["ColorHeartrate"],  track_json["GradesHeartrate"],  track_json["LegendHeartrate"] = numbers_to_colors(self.td_heartbeats,
                                                                                                colorscale, steps=steps,
                                                                                                steps_legend=steps_legend)
                from .utils import get_cardio_zone
                track_json["HeartrateGroup"] = [get_cardio_zone(a, mhr)[1] for a in self.td_heartbeat]
                track_json["ColorHeartrateGroup"] = [get_cardio_zone(a,mhr)[0] for a in self.td_heartbeat]
            if hasattr(self , 'td_heartbeats') and self.td_heartbeats:
                track_json["HeartrateOriginal"] = [to_float_or_zero(a) for a in self.td_heartbeats]
        else:
            self.warning("Cannot do get_json_DL: n_points=0")

        end = time.time()
        self.info("get_json_DL: %ss" %(end - start))

        return track_json

    def set_json_LD(self, how="all"):
        """Returns json as a list of dictionaries, one for each point"""
        self.info("set_json_LD")
        import time
        start = time.time()
        # track_json is a dict of lists
        self.info("__1 - track_json from get_json_DL")
        track_json = self.get_json_DL(how=how)
        track_json_ok = {k: v for k, v in track_json.items() if isinstance(v, list) and not "Grades" in k and not "Legend" in k}
        # i transform it in a list of dicts
        # pprint(track_json)
        self.info("__2 - track_json_2")
        track_json_2 = [dict(zip(track_json_ok, t)) for t in zip(*track_json_ok.values())]
        # added to be GEOJSON compatible!
        for it in track_json_2:
            it.update({"type": "Point"})
        self.info("__3 - track_json_3")
        track_json_3={}
        #add legend and grades
        for k,v in track_json.items():
            if "Grades" in k or "Legend" in k:
                 track_json_3[k]=v

        self.info("__4 - splits, laps, segments, subtracks in track_json_2")
        ##splits
        #print(self.td.split_indices)
        try:
            if (self.td.split_indices):
                import bisect
                split_indices = self.td.split_indices
                from .utils import get_colors
                colors_splits = get_colors(len(split_indices) - 1)
                for i,a in enumerate(track_json_2):
                    split = bisect.bisect_right(split_indices, a["OriginalNumber"])
                    split=min(split, len(split_indices)-1) #otherwise the last one gets a +1
                    a.update({"Split": split,
                            "SplitName": "Split "+str(split),
                            "ColorSplit": colors_splits[split-1] if colors_splits else ""})
                    if "Distance" in a.keys():
                        a.update({
                            "SplitDistance": a["Distance"]-track_json_2[split_indices[split-1]]["Distance"] #distance wrt first point in the split
                            })
        except Exception as e:
            self.error("Error in set_json_LD splits: %s" %e)

        ##segments
        # print(self.td.split_indices)
        try:
            if not self.td.segment_indices:
                self.td.segment_indices=[0]
                self.td.save()
            if self.td.segment_indices:
                import bisect
                from .utils import get_colors
                split_indices = self.td.segment_indices
                colors_splits = get_colors(len(split_indices))
                for i, a in enumerate(track_json_2):
                    ### segments (here named splits) start from 1
                    split = bisect.bisect_right(split_indices, a["OriginalNumber"])
                    split = min(split, len(split_indices))  # otherwise the last one gets a +1, max is
                    a.update({"Segment": split,
                            "SegmentName": "Segment " + str(split),
                            "ColorSegment": colors_splits[split - 1]})
                    if "Distance" in a.keys():
                        a.update({
                            "SegmentDistance": a["Distance"] - track_json_2[split_indices[split - 1]]["Distance"]
                        # distance wrt first point in the split
                        })
        except Exception as e:
            self.error("Error in set_json_LD segments: %s" %e)

        #subtracks
        try:
            if not self.td.subtrack_indices:
                self.td.subtrack_indices=[0]
                self.td.save()
            if self.td.subtrack_indices:
                import bisect
                from .utils import get_colors
                split_indices = self.td.subtrack_indices
                colors_splits = get_colors(len(split_indices))
                for i, a in enumerate(track_json_2):
                    split = bisect.bisect_right(split_indices, a["OriginalNumber"])
                    split = min(split, len(split_indices))  # otherwise the last one gets a +1
                    a.update({"Subtrack": split,
                            "SubtrackName": "Subtrack " + str(split),
                            "ColorSubtrack": colors_splits[split - 1]})
                    if "Distance" in a.keys():
                        a.update({
                            "SubtracktDistance": a["Distance"] - track_json_2[split_indices[split - 1]]["Distance"]
                        # distance wrt first point in the split
                        })
        except Exception as e:
            self.error("Error in set_json_LD subtracks: %s" %e)


        ##laps
        #print(self.td.laps_indices)
        #print(self.td.laps_indices)
        try:
            if (self.td.laps_indices):
                import bisect
                from .utils import get_colors
                laps_indices = self.td.laps_indices
                colors_laps = get_colors(len(laps_indices) - 1)
                colors_laps = ["gray"]+colors_laps+["silver"]
                laps_indices = [0]+ laps_indices + [laps_indices[-1]] # these are to eliminate "after" and "before"
                for i, a in enumerate(track_json_2):
                    lap = bisect.bisect_right(laps_indices, a["OriginalNumber"])-1 #start from zero with "before"
                    lap = min(lap, len(laps_indices) - 2)  # otherwise the last one gets a +1
                    if lap==0:
                        lap_name="Before"
                    elif lap==len(laps_indices) - 2:
                        lap_name="After"
                    else:
                        lap_name="Lap %s" %lap

                    a.update({"Lap": lap,
                            "LapName": lap_name,
                            "ColorLap": colors_laps[lap],
                            "LapDistance": a["Distance"] - track_json_2[laps_indices[lap]]["Distance"]
                            # distance wrt first point in the split
                            })
                #print(lap,lap_name)
        except Exception as e:
            self.error("Error in set_json_LD laps: %s" %e)


        import json
        self.info("__5 - dump track_json_3 to json_LD")
        track_json_3["points"]= track_json_2
        self.json_LD=json.dumps(track_json_3)
        self.save()

        end = time.time()

        self.info("set_json_LD: %.3f s" %(end - start))

        return track_json_3

    def get_json_LD(self, reduce_points="every",do_waypoints=True,do_photos=True,
                    global_wps=True, global_photos=True,global_lines=True,global_geojson=True,
                    color=None,every=None, is_from_many_tracks=False):
        """
        Returns json for track as a list of dictionaries, one dict per point.
        Plus other infos:legend, which features track has.
        Plus waypoints, photos, etc.

        json_tot=
            {
                features: {
                    'has_alts': True,
                     'has_freq': False,
                     'has_hr': False,
                     'has_times': True,
                     'use_points': False
                     },
                legend: {
                    "Distance":{
                        "grades":[],
                        "legend":[],
                        "decimals":
                        "title":
                    },
                    "Speed":{},
                    "Altitude":{},
                    "Slope":{},
                },
                Track: {
                    points: [
                        {'OriginalNumber': 0,
                         'TimeString': '10:18:12',
                         'DeltaTime': 0.0,
                         'DeltaTimeString': '0:00:00',
                         'coordinates': [14.122699, 45.822386],
                         'Distance': 0.0,
                         'ColorDistance': '#000004',
                         'ColorSpeed': '#f8cd37',
                         'Speed': 6.071936085398113,
                         'Pace': '9:52min/km',
                         'Altitude': 686.9300000000001,
                         'AltitudeOriginal': 694.1,
                         'ColorAltitude': '#0b0724',
                         'VerticalSpeed': -0.2026530612244911,
                         'Slope': -1.9124250890847672,
                         'ColorSlope': '#64156e',
                         'type': 'Point',
                         'Segment': 1,
                         'SegmentName': 'Segment 1',
                         'ColorSegment': '#ff0029',
                         'Subtrack': 1,
                         'SubtrackName': 'Subtrack 1',
                         'ColorSubtrack': '#ff0029',
                         'ReducedNumber': 0,
                         'point_type': 'track',
                         'track_name': '30_nov_2019_11_18_18_Bukovje_podkraj'},
                         {},
                         {}, one for each point
                     ] --> this is saved in json_LD, the rest is built on the fly
                },
                Waypoints: [],
                Photos: [],
                Global Photos: [],
                Global Waypoints: [],
                Global Lines: [],
                Global Geojson: []
            }
        """

        import time
        start = time.time()

        self.info("get_json_LD, do_waypoints %s" %do_waypoints)

        ## read json_LD
        #if not self.json_LD:
        from options.models import OptionSet
        if  OptionSet.get_option("ALWAYS_RELOAD_TRACK_JSON"):
            self.set_json_LD(how="all")

        try:
            track_json_3=json.loads(self.json_LD)
            track_json_2=track_json_3["points"]
        except:
            self.set_json_LD(how="all")
            track_json_3=json.loads(self.json_LD)
            from pprint import pprint
            # pprint(track_json_3)
            # print(track_json_3.__class__)
            track_json_2=track_json_3["points"]

        #print(track_json_2[0])

        ## take only some indices
        json_ok=[]
        if len(self.td.smooth_indices) and reduce_points == "smooth1":
            json_ok=[track_json_2[i] for i in self.td.smooth_indices]
        elif len(self.td.smooth2_indices) and reduce_points == "smooth2":
            json_ok = [track_json_2[i] for i in self.td.smooth2_indices]
        elif len(self.td.smooth3_indices) and reduce_points == "smooth3":
            json_ok = [track_json_2[i] for i in self.td.smooth3_indices]
        elif reduce_points == "all":
            json_ok=track_json_2
        elif reduce_points == "single":
            json_ok=[{
                "coordinates":[self.avg_long,self.avg_lat],
                "type":"Point"
            }]
        else:
            if not every:
                every = self.get_every()
            json_ok = track_json_2[::int(every)]

        ## update number & other stuff
        for i,a in enumerate(json_ok):
            a.update({"ReducedNumber":i,"point_type":"track","track_name":self.name_wo_path_wo_ext,
            "track_pk":self.pk})
            if color is not None:
                a.update({"color":color})
            if is_from_many_tracks:
                a.update({"is_from_many_tracks":1})

        json_tot={}
        use_points=False
        for g in self.groups.all():
            if g.use_points_instead_of_lines:
                use_points=True
                break
        json_prop = {"has_alts":self.has_alts,
                     "has_freq":self.has_freq,
                     "has_hr":self.has_hr,
                     "has_times":self.has_times,
                     "use_points":use_points}

        json_tot["features"]=json_prop

        # grades, legend
        legend={}
        grades={}
        legends={}
        for k,v in track_json_3.items():
            if "Grades" in k:
                grades[k.replace("Grades","")]=v
            if "Legend" in k:
                legends[k.replace("Legend","")]=v
        from .utils import get_cardio_colors
        if self.has_hr:
            grades["Heartrate Group"] = get_cardio_colors()["labels"]
            legends["Heartrate Group"] = get_cardio_colors()["colors"]

        from .utils import get_colors # for some reason the global import does not work
        ## laps
        laps_indices = self.td.laps_indices
        n_laps = len(laps_indices)
        grades["Lap"] = list((range(1,n_laps)))
        legends["Lap"] =get_colors(n_laps - 1)

        ## splits
        split_indices = self.td.split_indices
        n_splits = len(split_indices)
        grades["Split"] = list((range(1,n_splits)))
        legends["Split"] = get_colors(n_splits - 1)

        ## Segment, subtrack
        if "gpx" in self.extension:
            n_tracks=self.n_tracks
            n_segments=self.n_segments
        elif "kml" in self.extension or  "kmz" in self.extension:
            n_tracks=self.n_tracks_kml
            n_segments=self.n_segments_kml
        else:
            n_tracks=self.n_tracks
            n_segments=self.n_segments

        if n_tracks and n_tracks>1:
            grades["Subtrack"] = list((range(1,n_tracks+1)))
            legends["Subtrack"] =get_colors(n_tracks )
        if n_segments and n_segments>1:
            grades["Segment"] = list((range(1,n_segments+1)))
            legends["Segment"] =get_colors(n_segments)


        #json_tot["grades"]=grades
        #json_tot["legends"] = legends

        decimals={"Speed":1,"Altitude":0, "Frequency":0, "Heartrate":0, "Heartrate Group": -1, 
                "Slope":1,"Distance":1,
                "Lap":0, "Split":0,"":0, "Subtrack":0, "Segment":0, "VerticalSpeed":2}
        legend_titles = {"Speed": "Speed(km/h)",
                  "Altitude":  "Altitude(m)",
                  "Frequency": "Frequency",
                  "Heartrate": "Heartrate(bpm)",
                  "Heartrate Group": "Heartrate Group",
                  "Slope":  "Slope(%)",
                  "Distance": "Distance(km)",
                  "Lap":"Lap",
                  "Split":"Split",
                  "Subtrack":"Subtrack",
                  "Segment":"Segment",
                  "VerticalSpeed":"Vertical Speed (m/s)"
                }

        hide_in_map={
            "VerticalSpeed":True,
        }


        for k in grades.keys():
            try:
                legend[k]={
                    "grades":grades[k],
                    "legend":legends[k],
                    "decimals":decimals[k],
                    "title":legend_titles[k],
                    "hide_in_map":hide_in_map.get(k,False)
                }
            except Exception as e:
                self.warning("Cannot read legend %s: %s" % (k,e))
                #print("")
                #print("grades",grades)
                #print("")
                #print("legends", legends)
                #print("")
                #print("decimals", decimals)
                #print("")
                #print("legend_titles", legend_titles)
                #print("")

        json_tot["legend"] = legend

        json_tot["Track"]= {"points":json_ok}
        from json_views.utils import waypoints_json
        from json_views.utils import photos_json
        from json_views.utils import lines_json
        from json_views.utils import geojson_json
        ## waypoints
        if do_waypoints:
            json_tot["Waypoints"]=waypoints_json(wps=self.waypoint_set.all()|self.waypoints2.all())["Waypoints"]
        else:
            json_tot["Waypoints"]=[]
        ## photos
        if do_photos:
            json_tot["Photos"] = photos_json(photos=self.photos.all())["Photos"]
        else:
            json_tot["Photos"] = []
        ### global objects
        bounds={
            "min_lat":self.min_lat,
            "max_lat": self.max_lat,
            "min_long": self.min_long,
            "max_long": self.max_long,
        }
        from .utils import loosen_bounds
        bounds=loosen_bounds(bounds)

        ## global wps
        if global_wps:
            json_tot["Global Waypoints"] = waypoints_json(is_global=True, bounds=bounds)["Waypoints"]
        else:
            json_tot["Global Waypoints"] = []
        ## global photos
        if global_photos:
            json_tot["Global Photos"] = photos_json(is_global=True, bounds=bounds)["Photos"]
        else:
            json_tot["Global Photos"] = []
        ## global lines
        if global_lines:
            json_tot["Global Lines"] = lines_json(is_global=True, bounds=bounds)
        else:
            json_tot["Global Lines"] = []
        ## global geojson
        if global_geojson:
            json_tot["Global GeoJSON"] = geojson_json(is_global=True, bounds=bounds)
        else:
            json_tot["Global GeoJSON"] = []

        end = time.time()
        logger.info("get_json_LD: %s" %(end - start))

        #print(json_tot.keys())

        return json_tot

    def reimport(self,extension=None):
        from import_app.utils import from_files_to_tracks

        self.info("Reimport Track %s" %self.pk)
        #self.starting_index = 0
        #self.ending_index = 0
        self.save()
        try:
            self.log.reset()
            if extension:
                # use file with fiven extension
                file_path = self.find_file(ext=extension)
                if file_path:
                    from_files_to_tracks([file_path], update=True,ignore_blacklist=True)
                else:
                    status="Cannot find input file!"
            else:
                for extension in ["csv","gpx","tcx","kml","kmz"]:
                    file_path = self.find_file(ext=extension)
                    if file_path:
                        from_files_to_tracks([file_path], update=True,ignore_blacklist=True)
                        break
            status = "OK reimport"

        except Exception as e:
            import traceback
            traceback.print_exc()
            status = "KO reimport %s" %e
            logger.error(status)

        return status

    def get_track_single_geojson(self, color=None, points_line="MultiPoint", reduce_points="every", 
                        add_flat=True, number=0,waypoints=False,photos=False,
                        every=0):
        # try to read from db

        if self.json_properties and not OptionSet.get_option("ALWAYS_RELOAD_TRACK_JSON"):
            try:
                track_json = json.loads(self.json_properties)
            except Exception as e:
                self.error("Cannot read json_properties from db: %s" % e)
                track_json = self.set_track_single_geojson()
        # otherwise construct json (and save it in db)
        else:
            track_json = self.set_track_single_geojson()

        ## add other features
        # properties added on runtime
        track_json["color"]=color
        track_json["number"] = number
        if hasattr(self, "similarity"):  # exists only if it comes from filtering similar_to=track.pk
            track_json["similarity"] = self.similarity
        if hasattr(self, "duplicated_group") and self.duplicated_group!=-1:  # exists only if it comes from filtering with fuplicated tracks
            track_json["duplicated_group"] = self.duplicated_group
        if hasattr(self, "distance"):  # exists only if it comes from filtering distance to a point
            track_json["distance"] = {
                "distance": self.distance,
                "distance_string": "{0:.2f}".format(self.distance) + "km"}

        # properties which might change easily
        track_json["n_waypoints"]= self.waypoint_set.count()
        track_json["n_photos"]= self.photos.count()

        # choose which geometry
        track_json["geometry"]={"type": points_line}
        # line vs points
        if points_line=="LineString" or points_line=="MultiLineString":
            track_json["point_type"]= "track_as_line"
        elif points_line=="MultiPoint" or points_line=="Point":
            track_json["point_type"]= "track"
        # coordinates
        if reduce_points=="single":
            track_json["geometry"]={
                "coordinates":[self.avg_long,self.avg_lat],
                "type":"Point"
            }
            track_json["point_type"]= "track"
        #this case is cached because used frequently
        # the [] are for lit of lists of points
        elif reduce_points=="smooth2":
            try:
                track_json["geometry"]["coordinates"]=track_json["coordinates_smooth2"]
            except:
                try:
                    self.set_track_single_geojson()
                    track_json["geometry"]["coordinates"]=track_json["coordinates_smooth2"]
                except:
                    # copied form below
                    try:
                        coordinates_all=track_json["coordinates_all"]
                    except:
                        coordinates_all=[[lon, lat] for lon,lat in zip(self.td.long, self.td.lats) ]
                    track_json["geometry"]["coordinates"]=self.get_reduced_coordinates(coordinates_all,
                                                            reduce_points=reduce_points,
                                                            every=every)
        else:
            try:
                coordinates_all=track_json["coordinates_all"]
            except:
                coordinates_all=[[lon, lat] for lon,lat in zip(self.td.long, self.td.lats) ]
            track_json["geometry"]["coordinates"]=self.get_reduced_coordinates(coordinates_all,
                                                    reduce_points=reduce_points,
                                                    every=every)
        # if how == "line_smooth2" or how=="smooth2":
        #     track_json["geometry"]={
        #                     "type": "LineString",
        #                     "coordinates": self.get_reduced_coordinates(coordinates,how=2)
        #                 },
        #     track_json["point_type"]: "track_as_line"
        #     # track_json["geometry"]=track_json["geometry_1"]
        #     # track_json["point_type"] = track_json["point_type_1"]
        #     #track_json["geometry"]={"type":}
        # elif how == "points_smooth2":
        #     track_json["geometry"]={
        #                     "type": "MultiPoint",
        #                     "coordinates": self.get_reduced_coordinates(coordinates,how=2)
        #                 },
        #     track_json["point_type"] = "track"
        #     # track_json["geometry"]=track_json["geometry_2"]
        #     # track_json["point_type"] = track_json["point_type_2"]
        # elif how == "every":
        #     track_json["geometry"]={
        #                     "type": "MultiPoint",
        #                     "coordinates": self.get_reduced_coordinates(coordinates, how="every")
        #                 },
        #     track_json["point_type"] = "track"
        #     # every=self.get_every()
        #     # track_json["geometry"] = track_json["geometry_0"]
        #     # track_json["geometry"]["coordinates"]=track_json["geometry"]["coordinates"][::every]
        #     # track_json["point_type"] = track_json["point_type_0"]
        # elif how == "smooth1":
        #     track_json["geometry"]={
        #                     "type": "LineString",
        #                     "coordinates": self.get_reduced_coordinates(coordinates,how=2)
        #                 },
        #     track_json["point_type"]: "track_as_line"
        #     # track_json["geometry"] = track_json["geometry_0"]
        #     # track_json["point_type"] = track_json["point_type_0"]
        #     # track_json["geometry"]["coordinates"] = [track_json["geometry"]["coordinates"][i] for i in self.td.smooth_indices]
        # elif how == "smooth3":
        #     track_json["geometry"] = track_json["geometry_0"]
        #     track_json["point_type"] = track_json["point_type_0"]
        #     track_json["geometry"]["coordinates"] = [track_json["geometry"]["coordinates"][i] for i in self.td.smooth3_indices]
        # else:
        #     track_json["geometry"]=track_json["geometry_3"]
        #     track_json["point_type"] = track_json["point_type_3"]

        # choose if flatten nested dicts
        # flat is used for scatter plots, where I do not want subdicts
        # (subdicts are needed for representation in datatables)
        # I keep both representations for flexibility
        if add_flat:
            from .utils import flatten
            track_json_2 = flatten(track_json)
            track_json={**track_json,**track_json_2}

        from json_views.utils import waypoints_json,photos_json
        ## waypoints
        if waypoints:
            track_json["Waypoints"]=waypoints_json(wps=self.waypoint_set.all()|self.waypoints2.all())["Waypoints"]
        else:
            track_json["Waypoints"]=[]
        ## photos
        if photos:
            track_json["Photos"] = photos_json(photos=self.photos.all())["Photos"]
        else:
            track_json["Photos"] = []


        return track_json

    def get_reduced_coordinates(self, coordinates,reduce_points="smooth2",every=0):
        """
        coordinates->LineString is list of pairs
        coordinates->MultiLineString is list of lists pairs
        I reduce to list of pairs
        """
        try:
            # if i pass a list of lists of pairs
            coordinates[0][0][0]
            # convert to list of pairs
            coordinates_lp = [item for sublist in coordinates for item in sublist]
            coordinates_llp = coordinates
        except:
            # if i pass list of pairs
            coordinates_lp = coordinates
            # convert to list of lists of pairs
            coordinates_llp = [coordinates_lp]

        if reduce_points=="smooth1":
            if self.td.smooth_indices:
                coordinates_1 = [coordinates_lp[i] for i in self.td.smooth_indices  if i<len(coordinates_lp)]
            else:
                every = int(self.n_points / 100) + 1
                coordinates_1 = coordinates_lp[::every]
        elif reduce_points=="smooth2":
            if self.td.smooth2_indices:
                coordinates_1 = [coordinates_lp[i] for i in self.td.smooth2_indices  if i<len(coordinates_lp)]
            else:
                every = int(self.n_points / 100) + 1
                coordinates_1 = coordinates_lp[::every]
        elif reduce_points=="smooth3":
            if self.td.smooth3_indices:
                coordinates_1 = [coordinates_lp[i] for i in self.td.smooth3_indices  if i<len(coordinates_lp)]
            else:
                every = int(self.n_points / 100) + 1
                coordinates_1 = coordinates_lp[::every]

        else: #elif how=="every":
            if not every:
                every=self.get_every()
            #coordinates_1 = coordinates[::every]
            coordinates_1 = [segment[::every] for segment in coordinates_llp]


        # return  in any case a list of lists of pairs for multilinestring
        try:
            coordinates_1[0][0][0]
        except:
            coordinates_1=[coordinates_1]

        return coordinates_1

    def get_coordinates_for_multilinestring(self):
        all_coordinates = []
        try:
            coordinates_0 = [[lon, lat] for lon,lat in zip(self.td.long, self.td.lats) ]
            segments = self.td.segment_indices or [0]
            subtracks = self.td.subtrack_indices or [0]
            # for history I have one segment per point, so I would get no lines
            if len(segments)>=self.n_points:
                segments=[0]
            lons = self.td.long
            lats = self.td.lats
            all_indices = sorted(list(set(segments + subtracks)))
            all_indices.append(len(lons))
            for ind,ind_p1 in zip(all_indices,all_indices[1:]):
                coordinates = [ [lons[i], lats[i]] for i in range(ind,ind_p1)  if i <len(lons)]
                all_coordinates.append(coordinates)
        except Exception as e:
            self.error("Error in get_coordinates_for_multilinestring: %s" %e)
        return all_coordinates


    def set_track_single_geojson(self):
        """Single dict with global properties and geometry (no arrays of alt, speed, etc);
        creates a single, valid geojson object (as LineString or MultiPoint or Point)"""
        from .utils import numbers_to_colors, to_float_or_zero, get_cardio_zone
        import math
        import time
        start = time.time()

        json_ok = []

        self.info("set_track_single_geojson")

        if not self.avg_speed:
            self.avg_speed = 0
        if not self.total_frequency:
            self.total_frequency = 0

        # types = {"LineString":"track_as_line","MultiPoint":"track","Point":"track"}
        # point_type = ["track_as_line","track"]

        # geometry options
        # all points
        #type_0 = "LineString"
        ##coordinates_all = [[lon, lat] for lon,lat in zip(self.td.long, self.td.lats) ]
        coordinates_all = self.get_coordinates_for_multilinestring()
        # point_type_0 = "track_as_line"
        # type_1 = "LineString"
        # point_type_1 = "track_as_line"
        # try:
        try:
            if True:
                if self.td.smooth2_indices:
                    coordinates_1 = [[self.td.long[i], self.td.lats[i]] for i in self.td.smooth2_indices if i<len(self.td.long)]
                else:
                    every = int(self.n_points / 100) + 1
                    coordinates_1 = [[self.td.long[i], self.td.lats[i]] for i in
                                range(0, self.n_points - 1, every)]
        except Exception as e:
            self.error("Error in set_track_single_geojson coordinates_1: %s" %e)
            coordinates_1=[]
        # except:
        #     type_1 = "Point"
        #     coordinates_1 = [self.avg_long, self.avg_lat]
        #     point_type_1 = "track"
        # type_2 = "MultiPoint"
        # coordinates_2 = [[self.td.long[i], self.td.lats[i]] for i in self.td.smooth2_indices if i<len(self.td.lats)]
        # point_type_2 = "track"
        # type_3 = "Point"
        # coordinates_3 = [self.avg_long, self.avg_lat]
        # point_type_3 = "track"

        # various features
        time_number = 0
        month = 0
        cardio_zone = None
        cardio_zone_color = None
        cmeters_per_beat = None
        steps_per_beat = None
        delta_alt = None
        try:
            time_number = int(self.date.strftime("%Y%m%d"))
            month = self.date.strftime("%Y-%m") + "-01"
        except:
            pass
        if self.total_heartbeat and not math.isnan(self.total_heartbeat) and self.user:
            cardio_zone = get_cardio_zone(self.total_heartbeat, self.user.max_heartrate)[1]
            cardio_zone_color = get_cardio_zone(self.total_heartbeat, self.user.max_heartrate)[0]
            cmeters_per_beat = self.avg_speed / self.total_heartbeat * 1000
        else:
            pass
        if self.total_heartbeat and not math.isnan(self.total_heartbeat) and self.total_frequency and not  math.isnan(self.total_frequency):
            steps_per_beat = self.total_frequency / self.total_heartbeat
        else:
            pass
        try:
            delta_alt = to_float_or_zero(self.max_alt - self.min_alt)
        except:
            pass


        # same as in DB
        # ["end_country","end_city","end_region","pk","min_lat","max_lat","avg_lat","avg_long","min_long",
        #  "max_long","png_file"]

        # different name
        {
            "id": "pk",
            "name": self.name_wo_path_wo_ext,

        }
        #nested dicts
        try:
            frequency_string = str(int(self.total_frequency))
        except:
            frequency_string=""
            
        features = {
            # directly from DB
            "name": self.name_wo_path_wo_ext,
            "end_country": self.end_country,
            "end_city": self.end_city,
            "end_region": self.end_region,
            "id": self.pk,
            "pk": self.pk,
            "min_lat": self.min_lat,
            "max_lat": self.max_lat,
            "avg_lat": self.avg_lat,
            "avg_long": self.avg_long,
            "min_long": self.min_long,
            "max_long": self.max_long,
            "png_file": self.png_file,
            "duration": {
                "duration_string1": self.duration_string,
                "duration_string2": self.duration_string2,
                "duration": self.duration,
                "duration_ms": int((self.duration or 0)*60000),
            },
            "length": {
                "length_string": "{0:.2f}".format(self.length_3d / 1000) + "km",
                "length": self.length_3d,
                "length_km": self.length_3d / 1000
            },
            "speed": {
                "speed_string": "{0:.1f}".format(self.avg_speed * 3.6) + "km/h",
                "speed": self.avg_speed,
                "speed_kmh": self.avg_speed * 3.6,
            },
            "frequency": {
                "frequency_string": frequency_string,
                "frequency": self.total_frequency,
            },
            "pace": {
                "pace": self.pace,
                "pace_string": self.pace_string,
                "pace_ms": int((self.pace or 0) *60000),
            },
            "n_laps": to_float_or_zero(self.n_laps),
            "total_frequency": to_float_or_zero(self.total_frequency),
            "total_heartrate": to_float_or_zero(self.total_heartbeat),
            "total_calories": to_float_or_zero(self.total_calories),
            "total_step_length": to_float_or_zero(self.total_step_length),
            "total_steps": to_float_or_zero(self.total_steps),
            "min_alt": to_float_or_zero(self.min_alt),
            "max_alt": to_float_or_zero(self.max_alt),
            "date": self.date,
            "year": self.year,
            "activity_type": self.activity_type,
            "max_cardio": to_float_or_zero(self.max_cardio),
            "min_cardio": to_float_or_zero(self.min_cardio),
            "uphill": self.uphill,
            "downhill": self.downhill,
            ##derivated
            "time": str(self.date),
            "link": reverse("track_detail", kwargs={"track_id": self.pk}),
            "photos_link": reverse('track_photos_detail', kwargs={"track_id": self.pk}),

            ## calculated
            "time_number": time_number,
            "delta_alt": delta_alt,
            "month": month,
            "total_heartrate_group": cardio_zone,
            "total_heartrate_color_group": cardio_zone_color,
            "cmeters_per_beat": cmeters_per_beat,
            "steps_per_beat": steps_per_beat,

            #geometry
            "type": "Feature",
            "coordinates_all": coordinates_all, #all coordinates, as list of lits of pairs
            "coordinates_smooth2": [coordinates_1], #smooth2, less than 100 points, as list of list of  pairs
            #"coordinates_1point": [self.avg_long,self.avg_lat], # 1 point
            #"coordinates_all": [[lon, lat] for lon,lat in zip(self.td.long, self.td.lats) ],
            # "coordinates_smooth2" : [[self.td.long[i], self.td.lats[i]] for i in self.td.smooth2_indices if i <len(self.td.long)],
            # # 0
            # "geometry_0": {"type": type_0,
            #                "coordinates": coordinates_0},
            # "point_type_0": point_type_0,
            # # 1
            # "geometry_1": {"type": type_1,
            #                "coordinates": coordinates_1},
            # "point_type_1": point_type_1,
            # # 2
            # "geometry_2": {"type": type_2,
            #                "coordinates": coordinates_2},
            # "point_type_2": point_type_2,
            # # 3
            # "geometry_3": {"type": type_3,
            #                "coordinates": coordinates_3},
            # "point_type_3": point_type_3,

        }

        self.info("Saving json_properties to DB %s" %self)
        import json
        self.json_properties = json.dumps(features, cls=DjangoJSONEncoder)
        self.save()

        end = time.time()

        self.info("OK set_track_single_geojson: %.3f s" %(end-start))

        return features

    def debug(self,string):
        string=str(string)+"\n"
        from datetime import datetime
        logger.debug("%s - %s" %(self,string[:-1]))


    def info(self,string):
        string=str(string)+"\n"
        from datetime import datetime
        info="%s: %s" %(datetime.now(),string)
        logger.info("%s - %s" %(self,string[:-1]))
        self.log.infos=info+self.log.infos
        self.log.save()

    def warning(self,string):
        from datetime import datetime
        string=str(string)+"\n"
        warn="%s: %s" %(datetime.now(),string)
        warn2="%s: WARNING %s" %(datetime.now(),string)
        logger.warning("%s - %s" %(self,string[:-1]))
        self.log.infos=warn2+self.log.infos
        self.log.warnings=warn+self.log.warnings
        self.log.save()

    def error(self,string):
        string=str(string)+"\n"
        from datetime import datetime
        error="%s: %s" %(datetime.now(),string)
        error2="%s: ERROR %s" %(datetime.now(),string)
        logger.error("%s - %s" %(self,string[:-1]))
        self.log.infos=error2+self.log.infos
        self.log.errors=error+self.log.errors
        self.log.save()

    def draw_svg(self):
        import utm,pygal,os
        self.info("Draw SVG")
        every = self.get_every()
        try:
            lats=self.td.lats[::every]
            long=self.td.long[::every]
            from pygal.style import Style
            custom_style = Style(
              background='transparent',
              plot_background='transparent',
            #  foreground='#53E89B',
            #  foreground_strong='#53A0E8',
            #  foreground_subtle='#630C0D',
            #  opacity='.6',
            #  opacity_hover='.9',
            #  transition='400ms ease-in',
                #height=1000,
                #width=10,
                colors=('#0000FF','#E853A0', '#E8537A', '#E95355', '#E87653', '#E89B53')
            )
            xs=[]
            ys = []
            for lat, long in zip(lats, long):
                xs.append(utm.from_latlon(lat, long)[0])
                ys.append(utm.from_latlon(lat, long)[1])

            #ADJUST AXIS RATIOS BY HAND'
            if xs and ys:
                # ugly hack otherwise pygal goes into an infinite loop if max and min are too close
                if max(xs)-min(xs)<1e-9:
                    self.info("Correcting xs[0]")
                    xs[0]+=1e-8
                if max(ys)-min(ys)<1e-9:
                    self.info("Correcting ys[0]")
                    ys[0]+=1e-8
                
                delta_x=max(max(xs)-min(xs),1e-7)
                delta_y = max(max(ys) - min(ys),1e-7)

                xy_chart = pygal.XY(show_legend=False,stroke=False,show_x_labels=False,show_y_labels=False,
                                    style=custom_style,width=500, height=500*delta_y/delta_x)
                xy_chart.add('', [[x,y] for x,y in zip(xs,ys)])
                
                svg_file=  os.path.join(settings.BASE_DIR, "media", "svg",self.name_wo_path_wo_ext+'.svg')
                xy_chart.render_to_file(svg_file)
                #xy_chart.render_to_png(png_file)
                self.svg_file="/static/svg/" + self.name_wo_path_wo_ext+".svg"
                self.save()
                self.info("OK Draw SVG")
                return svg_file
            else:
                self.info("KO Draw SVG: no xs or ys")
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error(e)
        

    def draw_png(self):
        import utm,os
        import matplotlib.pyplot as plt
        self.info("Draw png")
        every=self.get_every()
        try:
            lats=self.td.lats[::every]
            long=self.td.long[::every]
            x=[utm.from_latlon(lat, long)[0] for lat,long in zip(lats,long)]
            y=[utm.from_latlon(lat, long)[1] for lat,long in zip(lats,long)]
            plt.gca().set_aspect('equal', adjustable='box')
            plt.axis('off')
            plt.scatter(x,y)
            png_file=  os.path.join(settings.BASE_DIR, "media", "png",self.name_wo_path_wo_ext+'.png')
            plt.savefig(png_file, bbox_inches='tight',transparent=True)
            plt.cla()
            self.png_file="/static/png/" + self.name_wo_path_wo_ext+".png"
            self.save()
            self.info("OK Draw png")
            return png_file
        except Exception as e:
            self.error("Error in draw_png: %s" %e)

    def set_path_groups(self):
        '''automatically assign groups according to path of imported file(s)'''
        import os
        from pathlib import Path
        self.info("set_path_groups")

        for file in (self.gpx_file,self.kml_file,self.kmz_file,self.csv_file,self.tcx_file):
            if file and file !="":
                try:
                    self.debug(file)
                    dir_=Path(os.path.relpath(file,settings.MEDIA_BASE_DIR )).parent
                    while dir_!=Path(""):
                        group_name="|"+str(dir_)
                        self.debug(group_name)
                        dir_=dir_.parent

                        query = Group.objects.filter(name=group_name)
                        if query.count() == 1:
                            group = query.first()
                        elif query.count() == 0:
                            group = Group()
                            group.name = group_name
                            group.is_path_group = True
                            group.save()
                        self.groups.add(group)
                except Exception as e:
                    self.warning("Error in set_path_groups, file %s: %s" %(file,e))
                #group.set_attributes() #might be slow
        self.info("OK set_path_groups")
        self.save()          

    def set_activity_group(self):
        import os
        self.info("Set activity group")
        try:

            #(1) tomtom files
            if self.csv_file is not None and self.csv_file != "" and self.csv_source=="tomtom":
                #self.info(self.csv_file)
                group_name = self.name_wo_path_wo_ext.split("_")[0]
                query = Group.objects.filter(name=group_name)
                if query.count() == 1:
                    group = query.first()
                elif query.count() == 0:
                    group = Group()
                    group.name = group_name
                    group.save()
                self.groups.add(group)
                #group.set_attributes()
                self.activity_type = group_name
                self.save()

            #(2) google timeline files
            if self.kml_file is not None and self.kml_file != "" and \
                        self.name_wo_path_wo_ext.startswith("history-20"):
                group_name = "Google timeline"
                self.info(group_name)
                query = Group.objects.filter(name=group_name)
                if query.count() == 1:
                    group = query.first()
                elif query.count() == 0:
                    group = Group()
                    group.name = group_name
                    group.save()
                self.groups.add(group)
                # try:
                #     group.set_attributes()
                # except:
                #     pass
                self.activity_type = group_name
                #guess date from name
                self.info("Setting date from file name")
                _,year,month,day,*rest=self.name_wo_path_wo_ext.split("-")
                import datetime
                self.info("%s %s %s" %(year,month,day) )
                date=datetime.datetime(int(year),int(month),int(day))
                self.info(date)
                self.beginning=date
                self.end=date+datetime.timedelta(days=1)
                self.date=date
                self.save()

            #(3) sygic  files
            import re
            pattern = re.compile("^[0-9]{6}_[0-9]{6}$") #190101_235959
            if self.kml_file is not None and self.kml_file != "" and \
                    pattern.match(self.name_wo_path_wo_ext):
                # guess date from name
                if True: #not self.beginning or not self.date:
                    self.info("Setting date from file name")
                    date,time = self.name_wo_path_wo_ext.split("_")
                    import datetime
                    year=2000+int(self.name_wo_path_wo_ext[0:2])
                    month = int(self.name_wo_path_wo_ext[2:4])
                    day = int(self.name_wo_path_wo_ext[4:6])
                    self.info("%s %s %s" % (year, month, day))
                    hour=int(self.name_wo_path_wo_ext[7:9])
                    minute = int(self.name_wo_path_wo_ext[9:11])
                    second = int(self.name_wo_path_wo_ext[11:13])
                    self.info("%s %s %s" % (hour, minute, second))
                    date = datetime.datetime(int(year), int(month), int(day))
                    date_t = datetime.datetime(int(year), int(month), int(day), hour,minute,second)
                    self.info(date_t)
                    self.beginning = date_t
                    self.date = date
                    self.save()

                try:
                    if self.kml_description:
                        self.info("Setting duration from description")
                        for a in self.kml_description.split("<tr>"):
                            if "Duration" in a:
                                for b in a.split("<td>"):
                                    if not "Duration" in b:
                                        duration_string = b[:-11]
                        self.info(duration_string)
                        if not self.duration_string: self.duration_string=duration_string
                        if not self.duration_string2: self.duration_string2 = duration_string
                        self.save()
                        from datetime import datetime, timedelta
                        try:
                            t = datetime.strptime(duration_string, "%Mmin %Ss")
                            delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
                        except:
                            try:
                                t = datetime.strptime(duration_string, "%Hh %Mm")
                                delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
                            except:
                                if duration_string=="1h":
                                    delta = timedelta(hours=1)
                                #usually <1min
                                else:
                                    delta = timedelta(seconds=0)

                        if not self.end: self.end=self.beginning+delta
                        if not self.duration: self.duration = delta.total_seconds()
                        self.save()

                        group_name = "Sygic"
                        self.info(group_name)
                        query = Group.objects.filter(name=group_name)
                        if query.count() == 1:
                            group = query.first()
                        elif query.count() == 0:
                            group = Group()
                            group.name = group_name
                            group.save()
                        self.groups.add(group)
                        # try:
                        #     group.set_attributes()
                        # except:
                        #     pass

                except Exception as e:
                    self.error("Error in reading sygic style: %s" %e)

            self.info("OK Set activity group")
            self.save()

        except Exception as e:
            self.error("Error in set_activity_group: %s" %e)

    def read_csv(self):
        """Reads csv files using the pandas library"""
        import pandas as pd

        self.info("Reading csv file" + self.csv_file)

        #leggo il file raw
        try:
            import io
            csv = io.open(self.csv_file, mode="r", encoding="utf-8")
            self.csv = csv.read()
        except Exception as e:
            self.error(e)

        #uso pandas per il resto
        try: #tomtom style
            self.info("Trying to read tomtom style")
            df_orig = pd.read_csv(self.csv_file)
            self.csv_table=df_orig.to_html(index=False, table_id="csv_table")
            self.info("CSV points original %s" %len(df_orig))
            self.n_points_csv = len(df_orig)
            #last point is nan for tomtom files
            ## csv often has different number of points form other files, and this is a problem for computed quantitites
            if self.n_points and (
                "gpx" in self.extension or 
                "kml" in self.extension or 
                "kmz" in self.extension or 
                "tcx" in self.extension) and \
                self.index_every==1:
                from .utils import get_sub_indices
                if len(df_orig)==self.n_points:
                    logger.info("OK length DF")
                    df = df_orig
                elif len(get_sub_indices(df_orig["time"],self.td.delta_times))==self.n_points:
                    logger.info("length DF from get_sub_indices")
                    inds = get_sub_indices(df_orig["time"],self.td.delta_times)
                    inds_ok=[i for i in inds if i<self.n_points]
                    df = df_orig.iloc[inds_ok]
                elif len(df_orig[df_orig["activityType"]!=-1])==self.n_points:
                    logger.info("length DF from activityType!=-1")
                    df = df_orig[df_orig["activityType"]!=-1]
                elif len(df_orig.dropna(subset=["lat"]))==self.n_points:
                    logger.info("length DF from dropna")
                    df = df_orig.dropna(subset=["lat"])
                else:
                    logger.error("cannot have right number of points in CSV!")
                    self.td.dist_csv=[]
                    self.td.speed_csv = []
                    self.td.calories = []
                    self.td.heartbeats = []
                    self.td.frequencies = []
                    self.save()
                    raise ValueError("cannot have right number of points in CSV!")
            # no other extension imported before
            else:
                df = df_orig
            npoints=len(df)
            if not self.n_points:
                self.n_points=npoints
                self.save()
            self.info("CSV points %s" %npoints)
            df = df.ffill().bfill()
            self.td.delta_times = list(df["time"])
            self.td.dist_csv = list(df["distance"])
            self.td.speed_csv = [s*3.6 for s in df["speed"]]
            self.td.calories = list(df["calories"])
            self.td.heartbeats = list(df["heartRate"])
            self.td.lats = list(df["lat"])
            self.td.long = list(df["long"])
            self.td.alts = list(df["elevation"])
            self.td.frequencies = list(df["cycles"])
            self.csv_source = "tomtom"
            self.total_steps= float(df["cycles"].sum())
            self.total_dist_csv = float(df["distance"].tail(1))
            self.total_speed_csv = (float(df["distance"].tail(1)) / float(df["time"].tail(1)) * 3.6)  # km/h
            pace = 1 / 0.06 /  self.total_speed_csv *3.6  # (min/km)
            self.total_pace_csv = (
                str(int(pace))
                + ":"
                + "{:02}".format(int((pace - int(pace)) * 60))
                + "min/km"
            )
            self.total_calories = float(df["calories"].tail(2).head(1))
            self.total_frequency = (float(df["cycles"].sum()) / float(df["time"].tail(1)) * 60)
            self.total_heartbeat = df_orig["heartRate"].mean()
            self.debug("total_heartbeat %s" %self.total_heartbeat)
            self.total_step_length = (float(df["distance"].tail(1)) / float(df["cycles"].sum()) )  # m
            
            if not df["heartRate"].isnull().all():
                self.set_cardio(df["heartRate"])
            self.info("OK Trying to read tomtom style")
        except Exception as e: #polar style
            import traceback
            traceback.print_exc()
            try:
                self.info("Failed with error %s! Trying to read polar style" %e)
                df_init = pd.read_csv(self.csv_file,nrows=1,sep=",")
                #print(df_init)
                self.total_calories=df_init["Calories"].head(1)
                self.total_speed_csv=df_init["Average speed (km/h)"].head(1)
                self.info(df_init["Average pace (min/km)"].head(1))
                self.total_pace_csv=(df_init["Average pace (min/km)"])[0]+"min/km"
                init_datetime=df_init.loc[0,"Date"]+" "+df_init.loc[0,"Start time"]
                self.info(init_datetime)
                import datetime
                naive_dt=datetime.datetime.strptime(init_datetime,"%d-%m-%Y %H:%M:%S")
                from django.utils import timezone
                #self.beginning=timezone.make_aware(naive_dt, timezone.get_current_timezone())
                self.beginning=naive_dt

                self.info("Beginning ", self.beginning)
                duration=df_init.loc[0,"Duration"]
                duration_obj=datetime.datetime.strptime(duration,"%H:%M:%S")-datetime.datetime(1900,1,1)
                self.duration=duration_obj.total_seconds()
                
                #TODO: parse of datetime
                #print (df_init.to_dict())
                #{'Name': {0: 'Pier Paolo  Baruselli '}, 'Sport': {0: 'HIKING'}, 'Date': {0: '18-11-2018'}, 'Start time': {0: '12:03:12'}, 'Duration': {0: '02:37:30'}, 'Total distance (km)': {0: 25.74}, 'Average heart rate (bpm)': {0: 119}, 'Average speed (km/h)': {0: 9.8}, 'Max speed (km/h)': {0: 19.6}, 'Average pace (min/km)': {0: '06:07'}, 'Max pace (min/km)': {0: '03:04'}, 'Calories': {0: 1191}, 'Fat percentage of calories(%)': {0: 30}, 'Average cadence (rpm)': {0: nan}, 'Average stride length (cm)': {0: nan}, 'Running index': {0: nan}, 'Training load': {0: nan}, 'Ascent (m)': {0: nan}, 'Descent (m)': {0: nan}, 'Notes': {0: nan}, 'Height (cm)': {0: 163.0}, 'Weight (kg)': {0: 64.0}, 'HR max': {0: nan}, 'HR sit': {0: nan}, 'VO2max': {0: nan}, 'Unnamed: 25': {0: nan}}

                df_orig = pd.read_csv(self.csv_file,skiprows=2,sep=",")
                df_orig.ffill(inplace=True)
                df_orig.bfill(inplace=True)
                self.info(df_orig.columns)
                df=df_orig
                #self.delta_times=Time
                self.td.heartbeats=list(df["HR (bpm)"])
                self.td.speed_csv=list(df["Speed (km/h)"])
                self.td.frequencies=list(df["Cadence"])
                self.td.alts=list(df["Altitude (m)"])
                self.td.dist_csv=list(df["Distances (m)"])
                self.csv_source="polar"
                self.total_dist_csv = float(df["Distances (m)"].tail(1))
                #self.total_speed_csv = (float(df["distance"].tail(1)) / float(df["time"].tail(1)) * 3.6)  # km/h
                # pace = 1 / 0.06 /  self.total_speed_csv *3.6  # (min/km)
                # self.total_pace_csv = (
                # str(int(pace))
                # + ":"
                # + "{:02}".format(int((pace - int(pace)) * 60))
                # + "min/km"
                # )
                self.total_heartbeat = df_orig["HR (bpm)"].mean()
                if not df["HR (bpm)"].isnull().all():
                    self.set_cardio(df["HR (bpm)"])


                duration_list=list(df["Time"])
                delta_times=[datetime.datetime.strptime(dt,"%H:%M:%S")-datetime.datetime(1900,1,1) for dt in duration_list]
                self.td.delta_times=[dt.total_seconds() for dt in delta_times]
                self.td.times=[dt+ self.beginning for dt in delta_times]
                self.info("OK Trying to read polar style")

            except Exception as e:
                self.error(e)

        self.save()
        self.td.save()



        # times
        from datetime import timedelta
        from datetime import datetime
        from django.utils import timezone

        try:
            self.info("Times")
            if False: #self.beginning:  # puo esistere da gpx, ma meglio ricalcolare se l'offset e' sbagliato
                beginning = self.beginning
            else:
                 try:
                      _, date_, time_ = self.name_wo_path_wo_ext.split("_")
                      beginning = datetime.strptime(date_ + "_" + time_, "%Y-%m-%d_%H-%M-%S")
                      self.beginning = beginning
                      self.corrected_times=True # I am reading time from the file name, so it is local time, not utc
                      self.info("Read beginning from filename: %s" %beginning)
                 except Exception as e:
                     self.warning("Cannot read beginning from filename: %s" %e)
                 pass
            self.save()

            if self.beginning:
                times = [self.beginning + timedelta(seconds=t) for t in self.td.delta_times]
                self.td.times = times
            self.info("OK times")
        except Exception as e:
            self.error(e)


        # splits: done later
        # try:
        #     self.get_split_indices()
        # except Exception as e:
        #     self.error(e)
        # try:
        #     if self.csv_source=="tomtom":
        #         self.info("Splits")
        #         from .utils import get_split_indices, sec_to_str
        #
        #         indices = get_split_indices(self.td.dist_csv)
        #         self.info("split indices: %s" %indices)
        #         self.split_indices=indices
        #         self.save()
        #         for i, ind in enumerate(indices):
        #             logger.debug("%s %s" %(i, ind))
        #             abs_time = self.td.delta_times[ind]
        #             if i == 0:
        #                 delta_t = abs_time
        #             else:
        #                 delta_t = self.td.delta_times[ind] - self.td.delta_times[ind_old]
        #             ind_old = ind
        #
        #             name = (
        #                 "KM"
        #                 + "{:02}".format(i + 1)
        #                 + "_"
        #                 + sec_to_str(abs_time)
        #                 + "_"
        #                 + sec_to_str(delta_t)
        #                 + "_"
        #                 + self.name_wo_path_wo_ext
        #             )
        #
        #             query = Waypoint.objects.filter(name=name).filter(track_pk=self.pk)
        #             if query.count() == 0:
        #                 waypoint = Waypoint()
        #                 waypoint.name = name
        #                 self.n_waypoints += 1
        #             else:
        #                 waypoint = query.first()
        #
        #             #puo essere null
        #             if self.td.lats[ind] is not None:
        #                 lat=self.td.lats[ind]
        #                 long=self.td.long[ind]
        #             else:
        #                 lat=self.td.lats[ind+1]
        #                 long=self.td.long[ind+1]
        #
        #             self.info("%s %s" %(lat,long))
        #
        #             waypoint.track = self
        #             waypoint.track_name = self.name_wo_path_wo_ext
        #             waypoint.track_pk = self.pk
        #             waypoint.lat = lat
        #             waypoint.long = long
        #             waypoint.alt = self.td.alts[ind]
        #             waypoint.time = self.td.times[ind]
        #             waypoint.auto_generated = True
        #             waypoint.save()
        #         self.get_splits_pace_()
        #
        #         self.info("OK splits")
        # except Exception as e:
        #     self.error(e)
        
        self.save()
        self.td.save()

        self.info("OK CSV reading")

    def get_every(self):
        """get the parameter every for visualization purposes"""
        import math
        from options.models import OptionSet
        try:
            every = math.ceil(self.n_points / OptionSet.get_option("MAX_POINTS_TRACK"))
            every=max(every,1)
        except:
            every = 1
        #logger.info("every %s" % every)
        return every

    def set_index_every(self):
        """set the parameter index_every for calculation purposes"""
        import math
        from options.models import OptionSet
        try:
            every = math.ceil(self.n_points_original / OptionSet.get_option("MAX_POINTS_TRACK_CALCULATION"))
            every=max(every,1)
        except:
            every = 1
        #logger.info("every %s" % every)
        self.info("set_index_every at %s" %every)
        self.index_every = every
        self.save()
        return self.index_every


    def get_split_indices(self):#TODO: move to app?
        n_km = self.splits_km
        from splits_laps.utils import get_split_indices
        if self.td.dist_csv:
            indices = get_split_indices(self.td.dist_csv, n_km)
        elif self.td.dist_tcx:
            indices = get_split_indices(self.td.dist_tcx, n_km)
        else:
            indices = get_split_indices(self.td.computed_dist, n_km)
        #self.info("split indices: %s" % indices)
        self.td.split_indices = [int(i) for i in indices]
        self.td.save()

    def set_cardio(self,series):

        self.info("Set cardio")

        try:
            if self.user:
                mhr = self.user.max_heartrate
                self.user_mhr = mhr
            else:
                mhr = 190    
            count=series.count()
            from .utils import get_cardio_colors
            ts=get_cardio_colors()["thresholds"]
            self.cardio_0 = (series<ts[0]*mhr).sum()/count*100
            self.cardio_1 = (series.between(ts[0]*mhr, ts[1]*mhr)).sum()/count*100
            self.cardio_2 = (series.between(ts[1]*mhr, ts[2]*mhr)).sum()/count*100
            self.cardio_3 = (series.between(ts[2]*mhr, ts[3]*mhr)).sum()/count*100
            self.cardio_4 = (series.between(ts[3]*mhr, ts[4]*mhr)).sum()/count*100
            self.cardio_5 = (series>=ts[4]*mhr).sum()/count*100
            import math
            if math.isnan(self.cardio_0): self.cardio_0=None
            if math.isnan(self.cardio_1): self.cardio_1 = None
            if math.isnan(self.cardio_2): self.cardio_2 = None
            if math.isnan(self.cardio_3): self.cardio_3 = None
            if math.isnan(self.cardio_4): self.cardio_4 = None
            if math.isnan(self.cardio_5): self.cardio_5 = None
            self.max_cardio = series.max()
            self.min_cardio = series.min()
            self.total_heartbeat = series.mean()
            self.save()
            self.debug("cardio0 %s" %self.cardio_0)
            self.info("OK set cardio")
        except Exception as e:
            self.error(e)

    def read_tcx(self):
        """Reads  tcx files using the tcx library"""
        import tcxparser
        from django.utils import timezone

        self.info("Read tcx")

        try:
            import io
            with io.open(self.tcx_file, 'r') as myfile:
                data=myfile.read()
                self.tcx=data
            self.save()

            import dateutil.parser

            tcx_obj=tcxparser.TCXParser(self.tcx_file)
            times=[dateutil.parser.parse(a,ignoretz=True) for a in tcx_obj.time_values()]
            alts=tcx_obj.altitude_points()
            dists=[int(a) if a else None for a in tcx_obj.distance_values()]
            lats=[a[0] for a in tcx_obj.position_values()]
            lons=[a[1] for a in tcx_obj.position_values()]
            heart=tcx_obj.hr_values()
            self.info("TCX points %s" %len(times))

            delta_times=[(t- times[0]).total_seconds() for t in times]

            ## tcx package, not used anymore
            #import tcx
            # tcx_obj=tcx.TCX()
            # tcx_tree=tcx_obj.parse(data)
            # from pprint import pprint
            # pprint(tcx_tree)
            # times=[a["properties"]["time"] if a["properties"]["time"]  else None for a in tcx_tree["features"] ]          
            # times = [a.replace(tzinfo=None) for a in times]
            # lats=[a["geometry"]["coordinates"][0][1] if a["geometry"]["coordinates"][0] else None for a in tcx_tree["features"]]          
            # long=[a["geometry"]["coordinates"][0][0] if a["geometry"]["coordinates"][0]  else None for a in tcx_tree["features"] ] 
            # dist=[a["properties"]["distance_meters"] if "distance_meters" in a["properties"] else None for a in tcx_tree["features"]  ]
            # try:                   
            #     heart=[a["properties"]["heart_rate_bpm"] if "heart_rate_bpm" in a["properties"] else None for a in tcx_tree["features"]]
            # except:
            #     heart=[]

            # to fill empty values, needed in any case for heart
            import pandas as pd
            df=pd.DataFrame({"lats":pd.Series(lats),"long":pd.Series(lons), 
                             "dist":pd.Series(dists),"heart":pd.Series(heart),
                             "alts":pd.Series(alts)})
            df.ffill(inplace=True)
            df.bfill(inplace=True)
            self.td.lats=list(df["lats"])
            self.td.alts=list(df["alts"])
            self.td.long=list(df["long"])
            self.td.heartbeats=list(df["heart"])
            self.td.dist_tcx=list(df["dist"])

            if len(heart)>0:
                self.set_cardio(df["heart"])

            self.td.delta_times=delta_times
            self.td.times=times
            self.total_dist_tcx=self.td.dist_tcx[-1]

            self.total_speed_tcx=self.total_dist_tcx/delta_times[-1]
            pace = 1 / 0.06 /  self.total_speed_tcx  # (min/km)
            self.pace_string_tcx = (
                str(int(pace))
                + ":"
                + "{:02}".format(int((pace - int(pace)) * 60))
                + "min/km"
            )
            #self.pace_string_tcx=
            self.td.save()
            self.n_points_tcx=len(lats)
            self.save()
            self.info("OK read tcx")

        except Exception as e:
            self.error(e)


    def read_gpx(self,_gpx=None):
        """Reads gpx files using the gpxpy library"""
        self.info("Read Gpx")
        from django.utils import timezone

        #if I don't pass a gpxpy object, I am reading a file
        try:
            if _gpx is None:
                reading_file=True
                try:
                    #save raw file under self.gpx
                    import io
                    try:
                        gpx = io.open(self.gpx_file, mode="r", encoding="utf-8")
                        _gpx = gpxpy.parse(open(self.gpx_file, "r", encoding="utf8"))
                    except Exception as e:
                        self.warning("Cannot read gpx with utf8, now trying without: %s" %e)
                        gpx = io.open(self.gpx_file, mode="r")
                        _gpx = gpxpy.parse(open(self.gpx_file, "r"))
                    self.gpx = gpx.read()
                    #read file into a gpxpy object
                except Exception as e:
                    self.error(self.gpx_file + " read _gpx " + str(e))
            #otherwise, I am reading a gpxpy object created form a kml/csv/tcx
            else:
                reading_file=False

        except Exception as e:
            self.error(e)

        #if I am not passing a gpxpy object, read alts, lats, long etc. from file
        if reading_file:
            self.info("Reading from file!")
            #read lats, long, alts, times, speed
            try:
                lats = []
                long = []
                alts = []
                times = []
                speed = []
                n_tracks=0
                n_segments=0
                subtrack_indices=[]
                segment_indices=[]
                point_number=0
                for track in _gpx.tracks:
                    n_tracks+=1
                    subtrack_indices.append(point_number) #index of first point in subtrack
                    for segment in track.segments:
                        segment_indices.append(point_number)#index of first point in segment
                        n_segments+=1
                        for point in segment.points:
                            point_number+=1
                            lats.append(point.latitude)
                            long.append(point.longitude)
                            alts.append(point.elevation)
                            times.append(point.time)
                            speed.append(point.speed)
                
                self.td.segment_indices = segment_indices
                self.td.subtrack_indices = subtrack_indices

                self.info("gpx: n_tracks %s n_segments %s n_times %s" %(n_tracks,n_segments,len(times)))
                self.n_tracks=n_tracks
                self.n_segments=n_segments

                self.td.lats = lats
                self.td.long = long
                self.n_points_gpx = len(lats)
                self.n_points = self.n_points_gpx

                try:
                    times_ok = times
                    delta_times=[(t- times_ok[0]).total_seconds() for t in times_ok]
                except:
                    times_ok=[]
                    delta_times=[]

                self.td.times = times_ok
                self.td.delta_times = delta_times

                # print(alts)
                counter_none = 0
                for a in alts:
                    if a is None:
                        counter_none += 1
                if counter_none / len(alts) < 0.9:
                    self.td.alts = alts
                counter_none = 0
                for s in speed:
                    if s is None:
                        counter_none += 1
                if counter_none / len(speed) < 0.9:
                    self.td.speed = speed

            except Exception as e:
                self.error(e)



            #read waypoints
            try:
                self.n_waypoints = 0
                for wp in _gpx.waypoints:
                    self.n_waypoints += 1

                    self.debug(wp.name)
                    query = Waypoint.objects.filter(
                        name=wp.name, lat=wp.latitude, long=wp.longitude
                    ).first()
                    if query is not None:
                        waypoint = query
                    else:
                        waypoint = Waypoint()

                    #if wp.description:
                    #    waypoint.name = wp.name+" "+wp.description
                    #else:
                    waypoint.name = wp.name
                    waypoint.lat = wp.latitude
                    waypoint.long = wp.longitude
                    waypoint.alt = wp.elevation
                    if wp.description: waypoint.description = wp.description.replace("<BR>","\n")
                    if wp.comment: waypoint.comment = wp.comment.replace("<BR>","\n")
                    waypoint.time = wp.time + self.get_timezone_offset()
                    waypoint.track = self
                    waypoint.track_pk = self.pk
                    waypoint.track_name = self.name_wo_path_wo_ext
                    # waypoint.geom = {'type': 'Point', 'coordinates': [waypoint.lat, waypoint.long]}
                    # waypoint.geom=Point(lat, long)
                    waypoint.set_timezone()
                    waypoint.save()

            except Exception as e:
                self.error(e)

            self.save()
            self.td.save()

        #this part I do for both reading file and passing a gpxpy object
        try:
            self.debug("Part for both reading and passing an object")
            if hasattr(_gpx,"creator"):
                self.gpx_creator = _gpx.creator
            self.length_2d = _gpx.length_2d()  # m
            self.length_3d = _gpx.length_3d()
            try:
                self.moving_time, self.stopped_time, self.moving_distance, self.stopped_distance, self.max_speed = (
                    _gpx.get_moving_data()
                )
            except Exception as e:
                self.warning("Error in _gpx.get_moving_data(): %s" %e)

            # self.avg_speed = self.moving_distance / self.moving_time
            self.uphill, self.downhill = _gpx.get_uphill_downhill()

            #points_no = len(list(_gpx.walk(only_points=True)))

            dists = []
            for point in _gpx.get_points_data():
                dists.append(point.distance_from_start)

            if dists and self.n_points  and len(dists)==self.n_points-1:
                dists.append(dists[-1])
            self.td.dist = dists

            # speed
            computed_speed = []
            for track in _gpx.tracks:
                for segment in track.segments:
                    for i, point in enumerate(segment.points):
                        try:
                            computed_speed.append(segment.get_speed(i)*3.6) #get speed return m/s
                        except:
                            computed_speed.append(0)
            if self.n_points and len(computed_speed)==self.n_points-1:
                computed_speed.append(computed_speed[-1])

            ##fix case gpx read from file ( original length) vs gpx created from existing data(length already reduced)
            # for length of computed_speed
            ## I limit the points when I am importing from file  
            if reading_file:
                self.td.computed_speed = computed_speed[::self.index_every][self.starting_index:self.ending_index]
            else:
                self.td.computed_speed = computed_speed

            # dist
            dists = []
            for point in _gpx.get_points_data():
                dists.append(point.distance_from_start)
            if self.n_points and len(dists) == self.n_points - 1:
                dists.append(dists[-1])
            ## I limit the points when I am importing from file  
            if reading_file:
                self.td.computed_dist = dists[::self.index_every][self.starting_index:self.ending_index]
            else:
                self.td.computed_dist = dists

            self.td.computed_dist = dists
            # print("self.td.computed_dist",len(self.td.computed_dist))
            self.save()

            # if points_no > 0:
            #     distances = []
            #     previous_point = None
            #     for point in _gpx.walk(only_points=True):
            #         if previous_point:
            #             distance = point.distance_2d(previous_point)
            #             distances.append(distance)
            #         previous_point = point

            # self.avg_distance_points=sum(distances) / len(list(_gpx.walk()))
            ############smoothing is done in place
            # print("reduce_points")
            import copy

            _gpx2 = copy.deepcopy(_gpx)
            _gpx3 = copy.deepcopy(_gpx)

            self.info("Reducing points with gpxpy")

            ###################original data, so I can understand which points are selected by the algorithms
            original_times=[]
            original_lats = []
            use_time = True
            for track in _gpx.tracks:
                for segment in track.segments:
                    for i, point in enumerate(segment.points):
                        if hasattr(point,"time") and point.time:
                            original_times.append(point.time)
                        else:
                            use_time=False
                        original_lats.append(point.latitude)

            _gpx.simplify(max_distance=10)  # algorithm
            _gpx2.reduce_points(max_points_no=100)  # min_distance or max_points_no
            _gpx3.reduce_points(min_distance=10)

            ###################_gpx
            times=[]
            lats = []
            use_time = True
            for track in _gpx.tracks:
                for segment in track.segments:
                    for i, point in enumerate(segment.points):
                        if hasattr(point,"time") and point.time:
                            times.append(point.time)
                        else:
                            use_time=False
                        lats.append(point.latitude)

            from .utils import get_sub_indices
            
            if(use_time):
                sub_indices = get_sub_indices(original_times,times)
            else:
                sub_indices = get_sub_indices(original_lats, lats)
            
            self.td.smooth_indices = sub_indices
            self.save()

            # self.info("length %s"  %self.n_points)
            self.info("_gpx smoothed length %s" %len(lats))
            self.length_2d_smooth = _gpx.length_2d()  # m
            self.length_3d_smooth = _gpx.length_3d()
            self.n_points_smooth = len(times)

            dists = []
            for point in _gpx.get_points_data():
                dists.append(point.distance_from_start)
            self.td.computed_dist_smooth = dists

            computed_speed = []
            for track in _gpx.tracks:
                for segment in track.segments:
                    for i, point in enumerate(segment.points):
                        speed= segment.get_speed(i)
                        if speed:
                            computed_speed.append(speed*3.6)
                        else:
                            computed_speed.append(0)
            self.td.computed_speed_smooth = computed_speed

            ################### _gpx2
            times=[]
            lats = []
            use_time = True
            for track in _gpx2.tracks:
                for segment in track.segments:
                    for i, point in enumerate(segment.points):
                        if hasattr(point,"time")  and point.time:
                            times.append(point.time)
                        else:
                            use_time=False
                        lats.append(point.latitude)

            from .utils import get_sub_indices
            if(use_time):
                self.td.smooth2_indices=get_sub_indices(original_times,times)
            else:
                self.td.smooth2_indices = get_sub_indices(original_lats, lats)

            self.info("_gpx2 smoothed length2 %s" %len(lats))
            self.length_2d_smooth2 = _gpx2.length_2d()  # m
            self.length_3d_smooth2 = _gpx2.length_3d()
            self.n_points_smooth2 = len(times)

            dists = []
            for point in _gpx2.get_points_data():
                dists.append(point.distance_from_start)
            self.td.computed_dist_smooth2 = dists

            computed_speed = []
            for track in _gpx2.tracks:
                for segment in track.segments:
                    for i, point in enumerate(segment.points):
                        speed= segment.get_speed(i)
                        if speed:
                            computed_speed.append(speed*3.6)
                        else:
                            computed_speed.append(0)
            self.td.computed_speed_smooth2 = computed_speed
            ################### _gpx3 to be left for playing by user
            times=[]
            lats = []
            use_time = True
            for track in _gpx3.tracks:
                for segment in track.segments:
                    for i, point in enumerate(segment.points):
                        if hasattr(point,"time")  and point.time:
                            times.append(point.time)
                        else:
                            use_time=False
                        lats.append(point.latitude)

            from .utils import get_sub_indices
            if(use_time):
                self.td.smooth3_indices=get_sub_indices(original_times,times)
            else:
                self.td.smooth3_indices = get_sub_indices(original_lats, lats)

            self.info("_gpx3 smoothed length3 %s" %len(lats))
            self.length_2d_smooth3 = _gpx3.length_2d()  # m
            self.length_3d_smooth3 = _gpx3.length_3d()
            self.n_points_smooth3 = len(times)

            dists = []
            for point in _gpx3.get_points_data():
                dists.append(point.distance_from_start)
            self.td.computed_dist_smooth3 = dists

            computed_speed = []
            for track in _gpx3.tracks:
                for segment in track.segments:
                    for i, point in enumerate(segment.points):
                        speed= segment.get_speed(i)
                        if speed:
                            computed_speed.append(speed*3.6)
                        else:
                            computed_speed.append(0)
            self.td.computed_speed_smooth3 = computed_speed
            dists = []

            self.save()
            self.td.save()
            self.info("End reducing points with gpxpy")
        except Exception as e:
            self.error("Error in Part for both reading and passing an object: %s" %e)
        
        self.info("End Read Gpx")

    def read_kml(self):
        """Reads  kml files using the xml.etree library; 
        based on https://gist.github.com/larsyencken/4577143"""

        self.info("Read kml")

        try:
            import io
            try:
                self.kml =io.open(self.kml_file, mode="r", encoding="utf-8").read()  
            except:
                self.kml =io.open(self.kml_file, mode="r").read()  
            self.save() 

            self.has_gx=self.check_for_gx(self.kml)
            self.info("Has gx? %s" %self.has_gx)

            #fastkml cannot read gx tags
            if self.has_gx:
                _doc=self.get_tree(self.kml)
                self.read_xml(_doc)
            else:
                n_points = self.read_fastkml(self.kml)
                if not n_points:
                    self.read_xml_general(self.kml)

        except Exception as e:
            self.error(e)

    def read_kmz(self):
        """Reads  kmz files using zipfile and xml.etree libraries; 
        based on https://gist.github.com/larsyencken/4577143"""
        from zipfile import ZipFile

        self.info("Read kmz")
        try:
            try:
                self.kmz=ZipFile(self.kmz_file, "r").open("doc.kml", "r").read()
            except:
                self.kmz=ZipFile(self.kmz_file, "r").open("doc.kml", "r", encoding="utf-8").read()
            self.save()

            self.has_gx=self.check_for_gx(self.kmz)
            self.info("Has gx? %s" %self.has_gx)

            #fastkml cannot read gx tags
            if self.has_gx:
                _doc=self.get_tree(self.kmz)
                self.read_xml(_doc)
            else:
                n_points = self.read_fastkml(self.kmz)
                if not n_points:
                    self.read_xml_general(self.kmz)

        except Exception as e:
            self.error(e)

    def get_tree(self,string):
        """Builds a tree via ElementTree from a string"""

        self.info("Get tree via ElementTree")
        from xml.etree import ElementTree
        try:
            _tree = ElementTree.fromstring(string)
            _doc = _tree.getchildren()[0] #this gives the Doc or main Folder

            from .utils import get_all_nodes
            return _doc
        except Exception as e:
            self.error(e)
            raise(e)

    def check_for_gx(self, string):
        self.info("check_for_gx")
        string=str(string)
        has_gx = "gx:Track" in string or "gx:MultiTrack" in string
        self.has_gx=has_gx
        return has_gx

    def read_fastkml(self,string):
        from fastkml import kml
        from .utils import get_all_nodes
        self.info("Read Xml using fastkml")

        lats=[]
        try:
            #initialize a fastkml object
            k = kml.KML()
            #and read content from provided string
            try:
                k.from_string(string)
            except:
                k.from_string(string.encode("utf-8"))
        except Exception as e:
            self.error(e)
            raise(e)

        except Exception as e:
            self.error(e)
            raise (e)

        try:
            self.info("Reading points")
            features=list(k.features())
            if features:
                main_folder=features[0]
                self.info("Main folder: %s %s " %(main_folder.name,main_folder))
                #folders=list(main_folder.features())[0]

                # all_folders=[n for n in get_all_nodes(main_folder,"features") if n.__class__.__name__=="Folder"]
                # self.info("All folders: %s" %([f.name for f in all_folders]))
                
                all_placemarks=[n for n in get_all_nodes(main_folder,"features") if n.__class__.__name__=="Placemark"]
                from pprint import pformat
                try:
                    self.info("All placemarks: %s" %pformat(([(p.geometry,p.name,p.description, p.geometry.__class__.__name__) for p in all_placemarks if p])))
                except:
                    pass
                #self.info("All placemarks: %s" %pformat(([p.geometry.__class__ for p in all_placemarks])))

                try:
                    tracks=[p for p in all_placemarks if p and p.geometry and p.geometry.__class__.__name__ in ["MultiLineString","LineString"] ]
                    ok_lc=True
                except:
                    ok_lc=False
                if not ok_lc:
                    tracks=[]
                    for p in all_placemarks:
                        try:
                            if p and p._geometry and  p.geometry and p.geometry.__class__.__name__ in ["MultiLineString","LineString"]:
                                    tracks.append(p)
                        except Exception as e:
                            import traceback
                            traceback.print_exc()
                            self.error("Cannot add track %s: %s" %(p,e))
                try:
                    waypoints=[p for p in all_placemarks if p and p.geometry and p.geometry.__class__.__name__=="Point"]
                    ok_lc=True
                except:
                    ok_lc=False
                if not ok_lc:
                    waypoints=[]
                    for p in all_placemarks:
                        try:
                            if p and p._geometry and  p.geometry and p.geometry.__class__.__name__ in ["Point",]:
                                    waypoints.append(p)
                        except Exception as e:
                            import traceback
                            traceback.print_exc()
                            self.error("Cannot add waypoint %s: %s" %(p,e))

                d=""
                for i,p in enumerate(all_placemarks):
                    try:
                        d+="(%s) %s : %s \n" %(i+1, p.name, p.description)
                    except:
                        pass
                self.kml_description=d
                self.info(d)
                self.save()

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error("Error read_fastkml in Reading points: %s" %e)
            tracks = []
            waypoints = []
            #raise(e)

        #track
        try:
            self.info("Setting track points")
            lats=[]
            longs=[]
            alts=[]
            times=[]
            segment_indices=[]
            subtrack_indices=[]
            self.n_tracks_kml=0
            self.n_segments_kml=0
            try:
                tracks.sort(key=lambda x: x._time_span.begin[0])
            except:
                pass

            point_number=0
            for t in tracks:
            #     print("t",t)
            #     print(t.name)
            #     print(t.description)
            #     print(list(t.styles()))
            #     print(t.styleUrl)
            #     for el in t.extended_data.elements:
            #         print(el.ns,el.name,el.value,el.display_name)
            #     print(t._time_span.ns)
            #     print(t._time_span.id)
            #     print(t._time_span.begin)
            #    print(t._time_span.begin_res)
            #     print(t._time_span.end)
            #    print(t._time_span.end_res)
                self.n_tracks_kml+=1
                subtrack_indices.append(point_number)
                for g in t.geometry.geoms:
                    self.n_segments_kml+=1
                    segment_indices.append(point_number)
                    for c in g.coords:
                        lats.append(c[1])
                        longs.append(c[0])
                        try:
                            alts.append(c[2])
                        except:
                            alts.append(None)
                        point_number+=1
                            
                        #TODO times

            self.td.lats=lats
            self.td.long=longs
            self.n_points_kml=len(lats)
            self.info("Fastkml points %s" %len(lats))
            if not None in alts: self.td.alts=alts
            #self.td.times=times
            if not "gpx" in self.extension:
                self.td.segment_indices=segment_indices
                self.td.subtrack_indices=subtrack_indices
            self.save()



        except Exception as e:
            self.error("Error read_fastkml Setting track points:%s" %e)

        #waypoints
        try:
            self.info("Waypoints")
            self.n_waypoints = 0
            for i,wp in enumerate(waypoints):
                # print(i,wp)
                self.n_waypoints += 1
                if wp.name is None:
                    try:
                        name=wp.snippet["text"]
                    except:
                        name=self.name_wo_path_wo_ext+"__wp_"+str(i)
                else:
                    name=wp.name
                
                lat=wp.geometry.coords[0][1]
                long=wp.geometry.coords[0][0]
                try:
                    alt=wp.geometry.coords[0][2]
                except:
                    alt=0
                time=wp.timeStamp
                self.info("%s %s %s" %(name,lat,long))

                ## these sometimes duplicates wps, due to problems with float?
                #query = Waypoint.objects.filter(track=name, lat=lat, long=long).first()
                ## query = Waypoint.objects.filter(track=self, lat=lat, long=long).first()
                # this does not duplicates, but could fail if 2 waypoints have the same name
                ##query = Waypoint.objects.filter(track=self,name=name).first()
                # this should be robust
                query = Waypoint.objects.filter(
                    track=self, name=name, 
                    lat__gt=lat-1e-7, lat__lt=lat+1e-7, 
                    long__gt=long-1e-7, long__lt=long+1e-7, 
                ).first()
                
                if query is not None:
                    waypoint = query
                else:
                    waypoint = Waypoint()

                waypoint.name = name
                waypoint.lat = lat
                waypoint.long = long
                waypoint.alt = alt
                if time:
                    try:
                        waypoint.time = time + self.get_timezone_offset()
                    except:
                        pass
                elif wp._time_span and wp._time_span.begin:
                    waypoint.time = wp._time_span.begin[0]

                waypoint.track = self
                # waypoint.geom = {'type': 'Point', 'coordinates': [waypoint.lat, waypoint.long]}
                if any(x in name for x in ("Start", "Inizio")):
                    waypoint.inizio = True
                # print(lat,long)
                # waypoint.geom=Point((lat, long))
                waypoint.description=wp.description.replace("<BR>","\n")
                waypoint.set_timezone()
                waypoint.save()

        except Exception as e:
            self.error(e)
        
        return len(lats)

        self.info("End read fastkml")

    def read_xml_general(self, _doc):
        """when fastkml fails..."""
        from .utils import get_all_nodes

        try:
            self.info("Try read_xml_general")
            from xml.etree import ElementTree
            _tree = ElementTree.fromstring(_doc)
            tree = _tree.getchildren()[0]
            all_nodes=get_all_nodes(tree,"getchildren")

            _where_list = [c for tr in all_nodes for c in tr.getchildren() if "coord" in c.tag]

            lats=[]
            lons=[]
            alts=[]
            for w in _where_list:
                for latlonalt in w.text.split():
                    lon,lat,alt=latlonalt.split(",")
                    lats.append(float(lat))
                    lons.append(float(lon))
                    alts.append(float(alt))

            self.info("Points: " + str(len(lats)))
            self.info("Xml points %s" %len(lats))
            self.td.long = lons
            self.td.lats = lats
            self.td.alts = alts
            #self.td.times = times
            self.n_points_kml=len(lats)
            self.save()
            self.td.save()

        except Exception as e:
            self.error(e)

        return len(lats)

    def read_xml(self, _doc):
        """Extract coordinates from the xml tree contained in doc
        It assumes the format:
               DOC
           /    |   \
         P1    Pn    F        Placemarks and Folders
          |          |
        Multitrack   Placemark
          |          |
        Track        list of waypoints
          |
        list of when and coords
        """
        import dateutil.parser

        self.info("Read Xml from kml/kmz")
        # points
        try:
            self.info("Read coordinates")
            from pprint import pprint

            self.info("doc: %s" %_doc)
            _placemark = [c for c in _doc.getchildren() if "Placemark" in c.tag]
            self.info("placemark: %s" %_placemark)
            #pprint([p.tag for p in _placemark])
            #pprint([c.tag for p in _placemark for c in p.getchildren() ])
            _track = [c for p in _placemark for c in p.getchildren() if "Track" in c.tag]
            self.info("track: %s" %_track)
            _track2 = [c for p in _track for c in p.getchildren() if "Track" in c.tag]
            self.info("track2: %s" %_track2)
            all_children = [c  for tr in _track2 for c in tr.getchildren() ]
            _when_list_1 = [c  if "when" in c.tag else None  for c in all_children ]
            _when_list_2 = [c  for c in all_children if "when" in c.tag]
            _where_list = [c for tr in _track2 for c in tr.getchildren() if "coord" in c.tag]
            if len(_when_list_1)==len(_where_list):
                _when_list = _when_list_1
            else:
                _when_list = _when_list_2
            #assert len(_when_list) == len(_where_list)
            long = []
            lats = []
            alts = []
            times = []
            i=1
            for when, where in zip(_when_list, _where_list):
                try:
                    lon = float(where.text.split()[0])
                except:
                    lon=None
                try:
                    lat = float(where.text.split()[1])
                except:
                    lat=None
                long.append(lon)
                lats.append(lat)
                try:
                    alt=float(where.text.split()[2])
                except:
                    alt=None
                alts.append(alt)
                try:
                    time=dateutil.parser.parse(when.text,ignoretz=True)
                except:
                    time=None
                times.append(time)
                #print(i,time,lat,lon,alt)
                i+=1
            self.info("Points: " + str(len(lats)))
            self.info("Xml points %s" %len(lats))
            self.td.long = long
            self.td.lats = lats
            self.td.alts = alts
            self.td.times = times
            self.n_points_kml=len(lats)
            self.save()
            self.td.save()

        except Exception as e:
            self.error("Error in read_xml Read coordinates: %s" %e)

        # waypoints
        # print("waypoints")
        waypoints = []
        try:
            self.info("Waypoints parsing")
            _folders = [c for c in _doc.getchildren() if "Folder" in c.tag]
            self.info("Folders: %s" %_folders)
            _placemarks_folders = [
                c for f in _folders for c in f.getchildren() if "Placemark" in c.tag
            ]
            self.info("Placemark Folders: %s" %_folders)
            _name_list = [
                c.text
                for p in _placemarks_folders
                for c in p.getchildren()
                if "name" in c.tag
            ]
            self.info("Name list: %s" %_name_list)
            _time_list = [
                c.getchildren()[0].text
                for p in _placemarks_folders
                for c in p.getchildren()
                if "Time" in c.tag
            ]
            _lats_list = [
                c.getchildren()[0].text.split(sep=",")[0]
                for p in _placemarks_folders
                for c in p.getchildren()
                if "Point" in c.tag
            ]
            _long_list = [
                c.getchildren()[0].text.split(sep=",")[1]
                for p in _placemarks_folders
                for c in p.getchildren()
                if "Point" in c.tag
            ]
            _alts_list = [
                c.getchildren()[0].text.split(sep=",")[2]
                for p in _placemarks_folders
                for c in p.getchildren()
                if "Point" in c.tag
            ]
        except Exception as e:
            self.error("Error in read_xml Waypoints parsing: %s" %e)

        try:
            self.info("Waypoints list")
            _waypoints = _placemark[:-1]  # last one is track
            self.info("_waypoints: %s" %_waypoints)
            # pprint(_waypoints)
            _waypoints2 = [p for w in _waypoints for p in w.getchildren()]
            self.info("_waypoints2: %s" %_waypoints2)
            # print(_waypoints2)
            _name_list += [w.text for w in _waypoints2 if "name" in w.tag]
            self.info("_name_list: %s" %_name_list)
            # print(_name_list)
            _time_list += [
                w.getchildren()[0].text for w in _waypoints2 if "Time" in w.tag
            ]
            # pprint(_time_list)
            _lats_list += [
                w.getchildren()[0].text.split(sep=",")[0]
                for w in _waypoints2
                if "Point" in w.tag
            ]
            # pprint(_lats_list)
            _long_list += [
                w.getchildren()[0].text.split(sep=",")[1]
                for w in _waypoints2
                if "Point" in w.tag
            ]
            # pprint(_long_list)
            # pprint(_alts_list+=[w.getchildren()[0].text.split(sep=',')[2] for w in _waypoints2 if "Point" in w.tag])
            # i waypont messi a mano non hanno l'altitudine!
            def get_alt(w):
                try:
                    return w.getchildren()[0].text.split(sep=",")[2]
                except:
                    return "0"

            _alts_list += [get_alt(w) for w in _waypoints2 if "Point" in w.tag]
            # pprint(_alts_list)

            self.n_waypoints = 0
            for name, time, long, lat, alt in zip(
                _name_list, _time_list, _lats_list, _long_list, _alts_list
            ):

                self.n_waypoints += 1
                query = Waypoint.objects.filter(name=name, lat=lat, long=long).first()
                if query is not None:
                    waypoint = query
                else:
                    waypoint = Waypoint()

                waypoint.name = name
                waypoint.lat = float(lat)
                waypoint.long = float(long)
                waypoint.alt = float(alt or 0)
                import dateutil.parser
                time = dateutil.parser.parse(time).replace(tzinfo=None)
                waypoint.time = time + self.get_timezone_offset()
                waypoint.track = self
                # waypoint.geom = {'type': 'Point', 'coordinates': [waypoint.lat, waypoint.long]}
                if any(x in name for x in ("Start", "Inizio")):
                    waypoint.inizio = True
                # print(lat,long)
                # waypoint.geom=Point((lat, long))
                waypoint.set_timezone()
                waypoint.save()

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error("Error in read_xml Waypoints list: %s" %e)
        self.info("End waypoints")
        self.info("WayPoints: " + str(self.n_waypoints))

        # other data
        self.info("Other data")
        _extended_data = []
        speed = []
        bearing = []
        accuracy = []
        try:
            _extended_data = [
                c for c in _track2[0].getchildren() if "ExtendedData" in c.tag
            ]
        except Exception as e:
            self.warning("Warning in read_xml _extended_data: %s" %e)
        try:
            # self._speed0= [c.text for c in self.extended_data[0].getchildren()[0].getchildren()[0].getchildren()]#
            speed = [
                self.text_to_float(c.text)
                for c in _extended_data[0]
                .getchildren()[0]
                .getchildren()[0]
                .getchildren()
            ]  #
            self.td.speed = speed
        except Exception as e:
            self.warning("Warning in read_xml speed: %s" %e)
        try:
            # self._bearing0= [c.text for c in self.extended_data[0].getchildren()[0].getchildren()[1].getchildren()]#
            bearing = [
                self.text_to_float(c.text)
                for c in _extended_data[0]
                .getchildren()[0]
                .getchildren()[1]
                .getchildren()
            ]  #
            self.td.bearing = bearing
        except Exception as e:
            self.info("Warning in read_xml bearing: %s" %e)
        try:
            accuracy = [
                self.text_to_float(c.text)
                for c in _extended_data[0]
                .getchildren()[0]
                .getchildren()[2]
                .getchildren()
            ]  #
            self.td.accuracy = accuracy
        except Exception as e:
            self.info("Warning in read_xml accuracy: %s" %e)
        self.td.save()
        try:
            self.info("Description")
            self.kml_description = _doc.getchildren()[-1].getchildren()[1].text
            if self.kml_description:
                _descr_lines = self.kml_description.split("\n")
                _descr_fields = [l.split(":", 1) for l in _descr_lines]
                _descr_1 = [f[0] for f in _descr_fields if len(f) == 1]
                _descr_1a = [f[0] for f in _descr_fields if (len(f) == 2)]
                _descr_1b = [f[1] for f in _descr_fields if len(f) == 2]
                # I put entries of description in a dict, but I want to keep their order (keys have different languages!)
                #print(_descr_1b)
                import json
                #from collections import OrderedDict
                self.descr_json = json.dumps(dict(zip(_descr_1a, _descr_1b)))
                self.length_kml = float(_descr_1b[3].split()[0].replace(",", "."))  # in km
                self.total_speed_kml = float(_descr_1b[6].split()[0].replace(",", "."))  # in km/h
                self.pace_string_kml = str(_descr_1b[9].split()[0].replace(",", "."))+"min/km"
                self.save()
                    #print(self.td.speed)
                #            self.descr_json = json.dumps(OrderedDict(zip(_descr_1a, _descr_1b)))
                #['Name', 'Art der Aktivität', 'Beschreibung', 'Gesamtstrecke', 'Gesamtzeit', 'Zeit in Bewegung', 'Durchschnittliche Geschwindigkeit', 'Durchschnittliche Geschwindigkeit in Bewegung', 'Maximale Geschwindigkeit', 'Durchschnittliches Tempo', 'Durchschnittliches Tempo in Bewegung', 'Schnellstes Tempo', 'Maximale Höhe', 'Minimale Höhe', 'Höhenunterschied', 'Maximales Gefälle', 'Minimales Gefälle', 'Aufgezeichnet']
                #[' 22.05.2016 10:51 Kokos', ' Walking', ' -', ' 3,04 km (1,9 Meile/n)', ' 2:52:37', ' 1:00:41', ' 1,06 km/h (0,7 Meile/h)', ' 3,00 km/h (1,9 Meile/h)', ' 5,47 km/h (3,4 Meile/h)', ' 56:48\xa0min/km (91:25\xa0min/Meile)', ' 19:58\xa0min/km (32:08\xa0min/Meile)', ' 10:58\xa0min/km (17:39\xa0min/Meile)', ' 673 m (2210 Fuß)', ' 264 m (865 Fuß)', ' 248 m (814 Fuß)', ' 24 %', ' -23 %', ' 22.05.2016 10:51']
        except Exception as e:
            self.warning("Warning in read_xml Description: %s" %e)
            self.kml_description = ""
            self.descr_json = ""

        self.info("End read xml")

    def rolling_quantities(self):
        self.info("__1 - Rolling quantities")
        #choose which distance to use
        if self.td.dist_csv:
            dist=self.td.dist_csv
        elif self.td.dist_tcx:
            dist=self.td.dist_tcx
        else:
            dist = self.td.computed_dist

        from .utils import rolling_speed,rolling_quantity
        #speed in km/h
        if self.td.times:
            self.debug("Rolling speed %s %s " %(self.n_rolling_speed,self.min_n_speed))
            # print("computed_dist", len(self.td.computed_dist))
            # print("delta_times", len(self.td.delta_times))
           
            self.td.computed_speed_rolling=list(rolling_speed(self.td.computed_dist,self.td.delta_times,n_rolling=self.n_rolling_speed,min_periods=self.min_n_speed)*3.6)
            self.td.speed_rolling=list(rolling_speed(dist,self.td.delta_times,n_rolling=self.n_rolling_speed,min_periods=self.min_n_speed)*3.6)
        # alt in m and slope in %
        if self.td.alts:
            self.debug("Rolling alt %s %s " % (self.n_rolling_alt, self.min_n_alt))
            self.td.alt_rolling = list(rolling_quantity(self.td.alts, n_rolling=self.n_rolling_alt, min_periods=self.min_n_alt))
            import numpy as np
            delta_x=[np.sqrt(s**2-y**2) if s is not None and y is not None and s>y else 0 for s,y in zip(self.td.computed_dist,self.td.alts)]
            slope_0 =  rolling_speed(self.td.alts, self.td.computed_dist, n_rolling=self.n_rolling_slope,
                                                       min_periods=self.min_n_slope,diff_x=True,diff_t=True,
                                                       only_positive=False) # delta_y / delta_s
            slope_0 = list(slope_0)
            slope_0 = [x if x else 0 for x in slope_0]
            slope_1 = [100*x/np.sqrt(1-x**2) if x<1 else 100*x for x in slope_0] # delta_y / delta_x
            slope_2 = [x if not np.isnan(x) else None for x in slope_1]
            self.td.slope_rolling = slope_2
        # vertical speed in m/s
        if self.td.alts and self.td.delta_times:
            self.debug("Rolling vert speed %s %s " % (self.n_rolling_slope, self.min_n_alt))
            self.td.vertical_speed_rolling = list(rolling_speed(self.td.alts,self.td.delta_times,
                n_rolling=self.n_rolling_slope,min_periods=self.min_n_alt, only_positive=False))
        #frequency in min(-1)
        # step length in m
        if self.td.frequencies:
            self.debug("Rolling freq %s %s " % (self.n_rolling_freq, self.min_n_freq)) 
            self.td.frequency_rolling=list(rolling_quantity(self.td.frequencies,n_rolling=self.n_rolling_freq,min_periods=self.min_n_freq,mult_by=60))
            self.td.save()
            #print("frequency_rolling",len(self.td.frequency_rolling ))
            import numpy as np
            #print([x for x in self.td.frequency_rolling if x is not None and np.isnan(x)])
            self.td.step_length_rolling= list(rolling_speed(dist,self.td.frequencies,n_rolling=self.n_rolling_freq,min_periods=self.min_n_freq,diff_x=True,diff_t=False)) # in m
            #print(len( self.td.step_length_rolling),len(self.td.lats))
        #heartbeats in (min)-1
        if self.td.heartbeats:
            self.debug("Rolling hr %s %s " % (self.n_rolling_hr, self.min_n_hr))
            self.td.heartbeat_rolling=list(rolling_quantity(self.td.heartbeats,n_rolling=self.n_rolling_hr,min_periods=self.min_n_hr))

        # self.info("__2 - set_json_LD")
        # self.set_json_LD(how="all")

        self.save()
        self.td.save()
        self.info("OK Rolling quantities")

    @staticmethod
    def text_to_float(a):
        """Sometimes data in bearing are empty, 
        so I put a np.nan instead of float(None) which raises an exception"""
        import numpy as np

        try:
            return float(a)
        except:
            return np.nan

    def set_timezone(self):
        from timezonefinder import TimezoneFinder

        try:
            tf = TimezoneFinder()
            if self.initial_lon:
                lng = self.initial_lon
                lat = self.initial_lat
            elif self.final_lon:
                lng = self.final_lon
                lat = self.final_lat
            # this will raise an exception if I have no coordinates, no problem, cannot do any better
            elif self.td.long and self.td.lats:
                lng =self.td.long[0]  
                lat = self.td.lats[0]
            else:
                logger.warning("No coordinates for set_timezone %s, return" %self)
                return

            timezone = tf.timezone_at(lng=float(lng), lat=float(lat))
            self.time_zone = timezone
            self.info("Setting timezone %s" %timezone)
            self.save()
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.warning("Cannot set time_zone: %s" %e)
            # TODO: add the default one
            # and keep the default one

    def get_timezone_offset(self,time=None, timezone=None):
        import datetime
        import pytz

        try:
            if not timezone:
                timezone = pytz.timezone(self.time_zone)
            if isinstance(timezone,str):
                timezone = pytz.timezone(timezone)
            if not time:
                if self.beginning:
                    time = self.beginning
                    print(self.beginning)
                elif self.td.times:
                    time = self.td.times[0]
                else:
                    time=datetime.datetime.now()
            time = time.replace(tzinfo=None)
            return timezone.utcoffset(time)
        except Exception as e:
            self.error("error with get_timezone_offset: %s" %e)
            import traceback
            traceback.print_exc()
            return datetime.timedelta(0)

    def fix_times(self,fake=False, offset=None, force=False):
        if not offset:
            if not fake:
                offset = self.get_timezone_offset()
            else:
                import datetime
                offset = datetime.timedelta(0)
        if offset is not None and (not self.corrected_times or force) and self.td.times:
            try:
                self.info("Fixing times with offset %s" %offset)
                times_ok=[]
                times = self.td.times
                for t in times:
                    times_ok.append(t + offset)
                self.td.times=times_ok

                self.beginning=times_ok[0]
                self.end = times_ok[-1]
                self.td.times_string = [str(t) for t in times_ok]
                self.td.times_string_nodate = [t.strftime("%H:%M:%S") for t in times_ok]
                self.td.delta_times_string = [str(t - times_ok[0]).split(".")[0] for t in times_ok]
                self.corrected_times=True
                self.save()
                self.td.save()
            except Exception as e:
                self.error("Cannot fix times: %s" %e)

    def assign_country_to_wps(self):
        """assign the same country, region, city of the track to its waypoints, only if
        waypoint does not already them set"""
        self.info("assign_country_to_wps")
        for wp in self.waypoint_set.all():
            if not wp.country and not wp.region and not wp.city:
                if self.end_country:
                    wp.country=self.end_country
                    wp.region = self.end_region
                    wp.city = self.end_city
                    wp.save()
                elif self.beg_country:
                    wp.country = self.beg_country
                    wp.region = self.beg_region
                    wp.city = self.beg_city
                    wp.save()

    def assign_time_to_wps(self):
        """assign the same time of the track to its waypoints, only if
        waypoint does not already it set"""
        self.info("assign_time_to_wps")
        for wp in self.waypoint_set.all():
            try:
                if not wp.time:
                    if self.end:
                        wp.time = self.end
                        wp.save()
                    elif self.beginning:
                        wp.time = self.beginning
                        wp.save()
            except Exception as e:
                self.warning("Error in assign_time_to_wps, %s: %s" %(wp,e))

    def set_heartrate_freq(self):
        """only used when merging tracks (it is usually done when importing)"""
        import pandas as pd
        import numpy as np
        if self.has_hr:
            series = pd.Series(self.td.heartbeats)
            self.set_cardio(series)
        else:
            self.td.heartbeats=[]
            self.td.heartbeat_rolling=[]
            self.cardio_0 = None
            self.cardio_1 = None
            self.cardio_2 = None
            self.cardio_3 = None
            self.cardio_4 = None
            self.cardio_5 = None
            self.max_cardio = None
            self.min_cardio = None
            self.total_heartbeat = None
        if self.td.frequencies and self.has_freq:
            self.total_frequency = np.nanmean([x for x in self.td.frequencies if x is not None])*60
            if np.isnan(self.total_frequency):
                self.total_frequency=None
        else:
            self.td.frequencies=[]
            self.td.frequency_rolling=[]
            self.total_frequency=None
        self.save()

    def get_arrays_smooth3(self):

        lats_smooth3=[self.td.lats[i] for i in self.td.smooth3_indices]
        long_smooth3=[self.td.long[i] for i in self.td.smooth3_indices]
        if self.td.alts:
            alts_smooth3=[self.td.alts[i] for i in self.td.smooth3_indices]
        else:
            alts_smooth3=[]
        times=self.td.times
        if times:
            times_smooth3=[times[i] for i in self.td.smooth3_indices]
        else:
            times=[]
        return{
            "lats_smooth3":lats_smooth3,
            "long_smooth3":long_smooth3,
            "alts_smooth3":alts_smooth3,
            "times_smooth3":times_smooth3,
        }

# def get_splits_pace_(self):
    #     from .utils import get_splits_pace, get_splits_hr
    #
    #     self.info("Get splits pace")
    #
    #     try:
    #         if self.td.dist_csv and self.td.delta_times:
    #             splits,self.td.splits_speeds = get_splits_pace(self.td.dist_csv, self.td.delta_times)
    #             self.splits=str(splits)
    #             logger.debug("self.td.splits_speeds %s" %self.td.splits_speeds)
    #             if self.td.heartbeats:
    #                 self.td.splits_hrs=get_splits_hr(self.td.dist_csv,self.td.heartbeats)
    #             if self.td.frequencies:
    #                 self.td.splits_frequencies=[a*60 for a in get_splits_hr(self.td.dist_csv,self.td.frequencies)]
    #             self.td.save()
    #             self.save()
    #     except Exception as e:
    #         self.error(e)
    #
    #     self.info("End splits pace")


def call_clsinit(cls):
    """https://stackoverflow.com/questions/12115357/calling-a-class-method-upon-creation-of-python-classes"""
    cls._clsinit()
    return cls

@call_clsinit
class TrackDetail(models.Model):
    #qui metto tutti gli arrayfield
    # original data
    laps = models.TextField(null=True, blank=True, unique=False, default="[]")
    laps_stats = models.TextField(null=True, blank=True, unique=False, default="{}")
    splits = models.TextField(null=True, blank=True, unique=False, default="[]")
    splits_stats = models.TextField(null=True, blank=True, unique=False, default="{}")

    if settings.USE_TEXT_INSTEAD_OF_ARRAYS:
        _times =models.TextField( null=True, default=("[]"))
        _delta_times =models.TextField( null=True, default=("[]"))  # in seconds
        _times_string =models.TextField(  null=True, default=("[]"))
        _times_string_nodate =models.TextField( null=True, default=("[]"))
        _delta_times_string =models.TextField(  null=True, default=("[]"))
        _lats =models.TextField( null=True, default=("[]"))
        _long =models.TextField( null=True, default=("[]"))
        _alts =models.TextField( null=True, default=("[]"))
        _speed_csv =models.TextField( null=True, default=("[]"))  # read directly from csv
        _dist_csv =models.TextField( null=True, default=("[]"))  # from csv
        _dist_tcx =models.TextField( null=True, default=("[]"))  # from tcx
        _calories =models.TextField( null=True, default=("[]"))  # from csv
        _frequencies =models.TextField( null=True, default=("[]"))  # from csv
        _heartbeats =models.TextField( null=True, default=("[]"))  # from csv
        # computed data
        _computed_speed =models.TextField( null=True, default=("[]")) #from gpx
        _computed_dist =models.TextField( null=True, default=("[]"))
        # rolling
        _speed_rolling =models.TextField( null=True, default=("[]"))
        _frequency_rolling =models.TextField( null=True, default=("[]"))
        _step_length_rolling =models.TextField( null=True, default=("[]"))
        _heartbeat_rolling =models.TextField( null=True, default=("[]"))
        _alt_rolling =models.TextField( null=True, default=("[]"))
        _slope_rolling =models.TextField( null=True, default=("[]"))
        _vertical_speed_rolling =models.TextField( null=True, default=("[]"))
        _computed_speed_rolling =models.TextField( null=True, default=("[]"))
        # smoothed data (with reduced number of points)
        _computed_speed_smooth =models.TextField( null=True, default=("[]"))
        _computed_dist_smooth =models.TextField( null=True, default=("[]"))
        _smooth_indices =models.TextField(null=True, default=("[]"))
        # smoothed data 2
        _computed_speed_smooth2 =models.TextField( null=True, default=("[]"))
        _computed_dist_smooth2 =models.TextField( null=True, default=("[]"))
        _smooth2_indices =models.TextField(null=True, default=("[]"))
        # smoothed data 3
        _computed_speed_smooth3 =models.TextField( null=True, default=("[]"))
        _computed_dist_smooth3 =models.TextField( null=True, default=("[]"))
        _smooth3_indices =models.TextField(null=True, default=("[]"))
        # other data
        _bearing =models.TextField( null=True, default=("[]"))
        _accuracy =models.TextField( null=True, default=("[]"))
        # laps, indices
        _laps_indices =models.TextField(null=True, default=("[]"))
        _split_indices =models.TextField(null=True, default=("[]"))
        _segment_indices =models.TextField(null=True, default=("[]"))
        _subtrack_indices =models.TextField(null=True, default=("[]"))
    else:
        _times = ArrayField(models.DateTimeField(), size=None, null=True, default=list)
        _delta_times = ArrayField(models.FloatField(), size=None, null=True, default=list)  # in seconds
        _times_string = ArrayField(models.CharField(max_length=255), size=None, null=True, default=list)
        _times_string_nodate = ArrayField(models.CharField(max_length=15), size=None, null=True, default=list)
        _delta_times_string = ArrayField(models.CharField(max_length=255), size=None, null=True, default=list)
        _lats = ArrayField(models.FloatField(), size=None, null=True, default=list)
        _long = ArrayField(models.FloatField(), size=None, null=True, default=list)
        _alts = ArrayField(models.FloatField(), size=None, null=True, default=list)
        _speed_csv = ArrayField(models.FloatField(), size=None, null=True, default=list)  # read directly from csv
        _dist_csv = ArrayField(models.FloatField(), size=None, null=True, default=list)  # from csv
        _dist_tcx = ArrayField(models.FloatField(), size=None, null=True, default=list)  # from tcx
        _calories = ArrayField(models.FloatField(), size=None, null=True, default=list)  # from csv
        _frequencies = ArrayField(models.FloatField(), size=None, null=True, default=list)  # from csv
        _heartbeats = ArrayField(models.FloatField(), size=None, null=True, default=list)  # from csv
        # computed data
        _computed_speed = ArrayField(models.FloatField(), size=None, null=True, default=list) #from gpx
        _computed_dist = ArrayField(models.FloatField(), size=None, null=True, default=list)
        # rolling
        _speed_rolling = ArrayField(models.FloatField(), size=None, null=True, default=list)
        _frequency_rolling = ArrayField(models.FloatField(), size=None, null=True, default=list)
        _step_length_rolling = ArrayField(models.FloatField(), size=None, null=True, default=list)
        _heartbeat_rolling = ArrayField(models.FloatField(), size=None, null=True, default=list)
        _alt_rolling = ArrayField(models.FloatField(), size=None, null=True, default=list)
        _slope_rolling = ArrayField(models.FloatField(), size=None, null=True, default=list)
        _vertical_speed_rolling = ArrayField(models.FloatField(), size=None, null=True, default=list)
        _computed_speed_rolling = ArrayField(models.FloatField(), size=None, null=True, default=list)
        # smoothed data (with reduced number of points)
        _computed_speed_smooth = ArrayField(models.FloatField(), size=None, null=True, default=list)
        _computed_dist_smooth = ArrayField(models.FloatField(), size=None, null=True, default=list)
        _smooth_indices = ArrayField(models.IntegerField(), size=None, null=True, default=list)
        # smoothed data 2
        _computed_speed_smooth2 = ArrayField(models.FloatField(), size=None, null=True, default=list)
        _computed_dist_smooth2 = ArrayField(models.FloatField(), size=None, null=True, default=list)
        _smooth2_indices = ArrayField(models.IntegerField(), size=None, null=True, default=list)
        # smoothed data 3
        _computed_speed_smooth3 = ArrayField(models.FloatField(), size=None, null=True, default=list)
        _computed_dist_smooth3 = ArrayField(models.FloatField(), size=None, null=True, default=list)
        _smooth3_indices = ArrayField(models.IntegerField(), size=None, null=True, default=list)
        # other data
        _bearing = ArrayField(models.FloatField(), size=None, null=True, default=list)
        _accuracy = ArrayField(models.FloatField(), size=None, null=True, default=list)
        # laps, indices
        _laps_indices = ArrayField(models.IntegerField(), size=None, null=True, default=list)
        _split_indices = ArrayField(models.IntegerField(), size=None, null=True, default=list)
        _segment_indices = ArrayField(models.IntegerField(), size=None, null=True, default=list)
        _subtrack_indices = ArrayField(models.IntegerField(), size=None, null=True, default=list)



    class Meta:
        verbose_name = "Track Detail"
        ordering = ["pk"]
        #app_label = "tracks"

    def __unicode__(self):
        return "Track Detail" + str(self.pk)

    def __repr__(self):
        return "TrackDetail"

    def __str__(self):
        return str(self.td.name_wo_path_wo_ext)

    @property
    def lats_all(self):
        """returns a list of all lats, just to know how many original points there are"""
        if settings.USE_TEXT_INSTEAD_OF_ARRAYS:
            return json.loads(self._lats)
        else:
            return self._lats

    def array_property(property_name,limit_initial_final=True, use_every=False):
        """ Create and return a property for the given field. """
        @property
        def prop(self):
            if use_every:
                every = self.td.index_every
            else:
                every = 1
            ok_prop = getattr(self, property_name)
            # only if i am using textfields instead of arrays
            if settings.USE_TEXT_INSTEAD_OF_ARRAYS:
                ok_prop=json.loads(ok_prop)
                # correct for times, which are stored as strings
                if property_name in ["_times"]:
                    import dateutil.parser
                    ok_prop = [dateutil.parser.parse(x).replace(tzinfo=None) for x in ok_prop]

            if limit_initial_final:
                if self.td.ending_index:
                    return ok_prop[::every][self.td.starting_index:self.td.ending_index]
                else:
                    return ok_prop[::every][self.td.starting_index:]
            else:
                return ok_prop[::every]

        @prop.setter
        def prop(self, value):
            logger.debug("Using %s setter" %property_name)
            if settings.USE_TEXT_INSTEAD_OF_ARRAYS:
                value=json.dumps(value,cls=DjangoJSONEncoder)
            setattr(self, property_name, value)

        return prop

    ## these fields are n_points long, and are limited by initial_index, final_index, and every
    ## they are fields directly imported from files
    array_fields_1 = (
        "_times",
        "_lats",
        "_long",
        "_alts",
        "_speed_csv",
        "_dist_csv",
        "_dist_tcx",
        "_calories",
        "_frequencies",
        "_heartbeats",
        "_bearing",
        "_accuracy",
        # these two are computed at import time if ifle is gpx,
        ##but already limited by hand
        # for other extensions , they are computed from points in list 1
        #  so they are of the same number as the original
        "_computed_speed",
        "_computed_dist",

    )

    ## these fields are n_points long, and are limited by initial_index and final_index (?)
    ## but not index_every
    ## they are calculated from the group 1
    ## they are of the size of fields in group 1 but already reduced by initial_index, final_index, and every
    # TODO: check initial and final index, they shouldnt be here
    array_fields_2 = (
        "_delta_times",
        "_times_string",
        "_times_string_nodate",
        "_delta_times_string",
        "_speed_rolling",
        "_frequency_rolling",
        "_step_length_rolling",
        "_heartbeat_rolling",
        "_alt_rolling",
        "_slope_rolling",
        "_vertical_speed_rolling",
        "_computed_speed_rolling",
    )

    ## these are not limited by starting_index e final_index
    ## they derive from reducing groups 1 and 2 the number of points in a dynamic way,
    ## so no need to reduce them further
    array_fields_3 = (
        "_computed_speed_smooth",
        "_computed_dist_smooth",
        "_smooth_indices",
        "_computed_speed_smooth2",
        "_computed_dist_smooth2",
        "_smooth2_indices",
        "_computed_speed_smooth3",
        "_computed_dist_smooth3",
        "_smooth3_indices",
        "_laps_indices",
        "_split_indices",
        "_segment_indices",
        "_subtrack_indices"
    )

    @classmethod
    def _clsinit(cls):
        """automatically create getters/setters for all given  fields, with name obtained removing first character (_), hence [1:]"""
        for field in cls.array_fields_1:
            property = cls.array_property(field,limit_initial_final=True,use_every=True)
            setattr(cls,field[1:],property)
        for field in cls.array_fields_2:
            property = cls.array_property(field,limit_initial_final=False,use_every=False)
            #property = cls.array_property(field,limit_initial_final=True,use_every=False)
            setattr(cls,field[1:],property)
        for field in cls.array_fields_3:
            property = cls.array_property(field, limit_initial_final=False,use_every=False)
            setattr(cls, field[1:], property)

