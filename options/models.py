from django.db import models

from django.urls import reverse
import logging
from pprint import pprint
from photos.models import Photo
from users.models import Profile
from waypoints.models import Waypoint
from logger.models import Log
from django.conf import settings
import datetime
from django import forms

logger = logging.getLogger("gps_tracks")

class OptionSet(models.Model):

    is_active = models.BooleanField(default=False, verbose_name="Use this options set (only one set can be active)")
    #MAPBOX
    MAPBOX_TOKEN=models.CharField( max_length=200, blank=True, null=True, verbose_name="<h3> MapBox </h3>MapBox token (needed to see MapBox maps)"  )
    BASEMAPS_MAPBOX = models.TextField(blank=True, null=True, default="satellite,streets,outdoors", verbose_name="MapBox maps (enter names separated by comma")
    #TOMTOM
    TOMTOM_USER = models.CharField( max_length=200, blank=True, null=True, verbose_name="<h3> TomTom </h3> TomTom username"  )
    TOMTOM_PASSWORD = models.CharField( max_length=200, blank=True, null=True, verbose_name="TomTom password")
    TOMTOM_FILENAME = models.CharField( max_length=200, blank=True, null=True, verbose_name="TomTom file name, see https://mysports.tomtom.com/app/settings/account-manage/data-protection/", default="1.zip")
    #TOMTOM
    GARMIN_USER = models.CharField( max_length=200, blank=True, null=True, verbose_name="<h3> Garmin </h3> Garmin username"  )
    GARMIN_PASSWORD = models.CharField( max_length=200, blank=True, null=True, verbose_name="Garmin password")
    #GOOGLE
    GOOGLE_PHOTOS_DIRS = models.TextField(blank=True, null=True, verbose_name="<h3> Google Drive and Photos </h3> Google Photos dirs in Drive (separate by newline)"  )
    GOOGLE_TRACKS_DIRS = models.TextField(blank=True, null=True,verbose_name="Google Tracks dirs in Drive (separate by newline)"  )
    MIN_YEAR_GOOGLE_PHOTOS = models.IntegerField(blank=False, null=False, default=2018, verbose_name="Minimum year for Google Photos")
    # TIMELINE
    CHROME_PATH = models.CharField(max_length=200, blank=True, null=True, verbose_name="<h3>Google Timeline </h3> Chromedriver path")
    GMAIL = models.CharField( max_length=200, blank=True, null=True  )
    GMAIL_PWD = models.CharField( max_length=200, blank=True, null=True )
    MIN_DATE_GOOGLE_HISTORY = models.DateField(null=True, default=datetime.date(2017, 1, 1))
    # geopy
    LANGUAGE_GEOPY = models.CharField(max_length=15, blank=True, null=True, verbose_name="<h3>Geopy</h3> Language for location names<a href='https://developer.tomtom.com/search-api/search-api/supported-languages'> (see list)</a>")
    USE_GEOPY = models.BooleanField(blank=True, default=True, verbose_name="Use geopy")
    #TRACKS
    MAX_POINTS_TRACK = models.IntegerField(blank=False, null=False, default=1000, verbose_name="<h3>Tracks</h3> Maximum number of points shown on maps")
    MAX_POINTS_TRACK_CALCULATION = models.IntegerField(blank=False, null=False, default=10000, verbose_name="Maximum number of track points used for calculations")
    MAX_N_TRACKS_AS_LINES = models.IntegerField(blank=False, null=False, default=30, verbose_name="Maximum number of tracks plottes as lines")
    GLOBAL_OBJECTS_OPTIONS = (
        ('all', 'All'),
        ('within_bounds', 'Only those within track bounds'),
    )
    GLOBAL_OBJECTS = models.CharField(max_length=20, choices=GLOBAL_OBJECTS_OPTIONS, default="all", verbose_name="Show global objects")
    DEFAULT_POINT_RADIUS = models.IntegerField(blank=False, null=False, default=10, verbose_name="Default radius for points")
    ALWAYS_RELOAD_TRACK_JSON = models.BooleanField(default=False, verbose_name="Always refresh track info (debug feature)")
    DISTANCE_FOR_CLUSTERING = models.IntegerField(blank=False, null=False, default=50,verbose_name="Minimum distance below which features are clustered (m)")
    MAX_FEATURES_FOR_CLUSTERING = models.IntegerField(blank=False, null=False, default=300,verbose_name="Maximum number of features for which clustering is performed")
    N_BEST_TRACKS_GROUP = models.IntegerField(blank=False, null=False, default=5, verbose_name="Number of best and worst tracks in group statistics")
    #AUTO_CREATE_TOMTOM_GROUPS = models.BooleanField(default=True, verbose_name="Automatically create track groups for TomTom activities")
    # colors
    COLORSCALE_LISTS = models.CharField(max_length=200, blank=True, null=True, default="gist_rainbow", verbose_name="<h3>Colors </h3> Colorscale when seeing lists of tracks")
    COLORSCALE_RANKS = models.CharField(max_length=200, blank=True, null=True, default="Wistia",verbose_name="Colorscale when seeing ranks of tracks in a group")
    COLORSCALE_TRACK = models.CharField(max_length=200, blank=True, null=True, default="Wistia",verbose_name="Colorscale for legend of single track")
    COLORSCALE_DIVERGING = models.CharField(max_length=200, blank=True, null=True, default="seismic",verbose_name="Colorscale for slope of single track")
    #photos
    PHOTO_TRACK_CHOICES = (
        ('same_day', 'Same day'),
        ('beginning_end', 'Exact time'),
    )
    LINK_PHOTOS_TO_TRACKS = models.CharField(max_length=20, choices=PHOTO_TRACK_CHOICES, default="beginning_end", verbose_name="<h3>Photos</h3> How to link photos to track")
    PHOTO_LOCATION_CHOICES = (
        ('original', 'Original from tags'),
        ('deduced', 'Deduced from tracks'),
    )
    PHOTO_LOCATIONS = models.CharField(max_length=20, choices=PHOTO_LOCATION_CHOICES, default="original", verbose_name="Preferred location method")
    PHOTOS_DOWNLOAD_DIR = models.CharField(max_length=1023, blank=True, null=True, default="", verbose_name="Folder to which download photos, if empty default is media/Camera inside the project directory. If changed, must be added to ADDITIONAL_PHOTO_DIRS in the .env file to be able to import and show downloaded photos")
    # timezone
    import pytz
    TIMEZONE_CHOICES = [(t, t) for t in pytz.common_timezones]
    TIMEZONE=models.CharField(max_length=255, choices=TIMEZONE_CHOICES, default="Europe/Rome", verbose_name="<h3>Timezone</h3> Default timezone")
    # other
    OWM_KEY = models.CharField(max_length=200, blank=True, null=True, verbose_name="<h3>Other</h3> OWM key")
    # maps
    BASEMAPS = models.TextField(blank=False, null=False, default="['OpenStreetMap.Mapnik', 'OpenTopoMap', 'Esri.WorldTopoMap', 'Esri.WorldImagery', 'Esri.WorldTerrain', 'MtbMap', 'HikeBike.HikeBike', 'Wikimedia', 'Google.GoogleStreets', 'Google.GoogleHybrid', 'Google.GoogleTerrain']")
    # other
    FREETEXT = models.TextField(blank=True, null=True, default="",verbose_name="<h3>Personal notes</h3>")
    # centering of maps
    DEFAULT_LAT = models.FloatField(blank=True, null=True, default=0,verbose_name="<h3>Default centering for maps</h3> Default Latitude")
    DEFAULT_LNG = models.FloatField(blank=True, null=True, default=0,verbose_name="Default Longitude")

    class Meta:
        verbose_name = "OptionSet"
        ordering = ["pk"]
        #app_label = "options"

    def save(self, *args, **kwargs):
        # if set as active, all other are set as not active
        if self.is_active:
            for op in OptionSet.objects.exclude(id=self.pk):
                op.is_active=False
                op.save()
        # if set as non active, but no others are active, set it active
        else:
            if not OptionSet.objects.filter(is_active=True).exclude(id=self.pk):
                self.is_active=True
        super(OptionSet, self).save(*args, **kwargs)

    @staticmethod
    def get_option(option_name, default=None):
        try:
            active_set = OptionSet.objects.get(is_active=True)
            value = getattr(active_set, option_name)
            if not value:
                value = default
        except:
            return default
        return value

    @staticmethod
    def set_option(option_name,value):
        active_set = OptionSet.objects.get(is_active=True)
        setattr(active_set, option_name,value)
        active_set.save()
