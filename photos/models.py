from django.db import models
import json

from django.utils import timezone
from django.urls import reverse
import logging
from pprint import pprint
from django.conf import settings

logger = logging.getLogger("gps_tracks")

class Photo(models.Model):

    name = models.CharField(max_length=255, verbose_name="Photo name", null=False, blank=False, unique=False)
    lat = models.FloatField(null=True,default=None, blank=True)
    long = models.FloatField(null=True,default=None, blank=True)
    alt = models.FloatField(null=True, blank=True)
    time = models.DateTimeField(null=True)
    path = models.CharField(max_length=255, verbose_name="Photo name", null=False, blank=False, unique=False)
    thumbnail = models.CharField(max_length=511, verbose_name="Thumbnail name", null=True, blank=True, unique=False)
    url_path = models.CharField(max_length=255,verbose_name="Photo url path",null=False,blank=False,unique=False,    )
    thumbnail_url_path = models.CharField(max_length=255,verbose_name="Thumbnail url path",null=True,blank=True,unique=False,    )
    # track = models.ForeignKey("tracks.Track", null=True, blank=True ,on_delete=models.SET_NULL)
    # these 2 fields are to speed up menu loadings
    tracks = models.ManyToManyField("tracks.Track",blank=True)
    track_name = models.CharField(max_length=255, verbose_name="Track name", null=True, blank=True, unique=False)
    track_pk = models.IntegerField(null=True)
    #
    deduced_lat = models.FloatField(null=True,default=None)
    deduced_long = models.FloatField(null=True,default=None)
    deduced_alt = models.FloatField(null=True,default=None)
    track_how = models.CharField(
        max_length=255,
        verbose_name="Way of linkning to track",
        null=True,
        blank=True,
        unique=False,
    )
    country = models.CharField(max_length=50, null=True, blank=True, unique=False, default="")
    country_code = models.CharField(max_length=10, null=True, blank=True, unique=False, default="")
    region = models.CharField(max_length=100, null=True, blank=True, unique=False, default="")
    city = models.CharField(max_length=50, null=True, blank=True, unique=False, default="")
    address = models.CharField(max_length=250, null=True, blank=True, unique=False, default="")
    modified = models.DateTimeField(auto_now=True, verbose_name="Date of modification", null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name="Date of creation", null=True, blank=True)
    info = models.TextField(verbose_name="Infos", null=True, blank=True, unique=False)
    has_gps = models.BooleanField(default=False)
    has_time = models.BooleanField(default=False)
    is_global = models.BooleanField(default=False, verbose_name="Shown on all maps")
    description = models.TextField(verbose_name="Description", null=True, blank=True, unique=False)
    import pytz
    TIMEZONE_CHOICES = [(str(t), str(t)) for t in pytz.common_timezones]
    time_zone=models.CharField(max_length=255, choices=TIMEZONE_CHOICES, default="Europe/Rome")


    # geom =              gismodels.PointField()
    # objects =           gismodels.GeoManager()

    class Meta:
        verbose_name = "Photo"
        ordering = ["time"]
        #app_label = "tracks"

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return "Waypoints"

    def __str__(self):
        return str(self.name)

    def create_thumbnail(self,size = (384, 384)):
        """https://stackoverflow.com/questions/2612436/create-thumbnail-images-for-jpegs-with-python"""
        import os, sys
        from PIL import Image

        thumbnail_dir=os.path.join(settings.PHOTOS_DIR,"thumbnails")
        outfile=os.path.join(thumbnail_dir,self.name)+".jpg"

        try:
            os.mkdir(thumbnail_dir)
        except:
            pass

        try:
            im = Image.open(self.path)
            im.thumbnail(size)
            im.save(outfile, "JPEG")
        except IOError:
            logger.error("cannot create thumbnail for %s" %self.name)

        self.thumbnail=outfile
        rel_path_name = os.path.relpath(outfile,settings.MEDIA_BASE_DIR).replace("\\","/")
        self.thumbnail_url_path = "/media/" + rel_path_name
        self.save()
        return outfile

    def set_timezone(self):
        from timezonefinder import TimezoneFinder
        from options.models import OptionSet

        location_way = OptionSet.get_option("PHOTO_LOCATIONS")
        if location_way == "original" and self.lat and self.long:
            lat=self.lat
            lng=self.long
        elif location_way == "deduced" and self.deduced_lat and self.deduced_long:
            lat=self.deduced_lat
            lng=self.deduced_long
        elif self.lat and self.long:
            lat=self.lat
            lng=self.long
        elif self.deduced_lat and self.deduced_long:
            lat=self.deduced_lat
            lng=self.deduced_long
        else:
            logger.info("No coordinates for set_timezone %s, return" %self)
            return

        try:
            tf = TimezoneFinder()
            timezone = tf.timezone_at(lng=lng, lat=lat)
            self.time_zone = timezone
            logger.info("Setting timezone %s %s" %(self,timezone))
            self.save()
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.warning("Cannot set time_zone: %s" %e)
