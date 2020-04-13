from django.db import models
import logging
import traceback
logger = logging.getLogger("gps_tracks")

class Waypoint(models.Model):
    name = models.CharField(
        max_length=1023, verbose_name="WP name", null=False, blank=False, unique=False
    )
    lat = models.FloatField(null=False,blank=False,default=0)
    long = models.FloatField(null=False,blank=False,default=0)
    alt = models.FloatField(null=True)
    time = models.DateTimeField(null=True)
    created_by_hand = models.BooleanField(default=False)
    auto_generated = models.BooleanField(default=False)
    # geom=              PointField(null=True)
    track = models.ForeignKey("tracks.Track", null=True, blank=True,on_delete=models.CASCADE)
    track2 = models.ForeignKey("tracks.Track", null=True, blank=True, on_delete=models.CASCADE, related_name="waypoints2")
    # these 2 fields are to speed up menu loadings
    track_name = models.CharField(max_length=255, verbose_name="Track name", null=True, blank=True, unique=False)
    track_pk = models.IntegerField(null=True)
    #
    inizio = models.BooleanField(default=False)
    country = models.CharField(max_length=50, null=True, blank=True, unique=False, default="")
    country_code = models.CharField(max_length=10, null=True, blank=True, unique=False, default="")
    region = models.CharField(max_length=100, null=True, blank=True, unique=False, default="")
    city = models.CharField(max_length=50, null=True, blank=True, unique=False, default="")
    address = models.CharField(max_length=250, null=True, blank=True, unique=False, default="")
    description = models.TextField(null=True, blank=True, unique=False, default="")
    comment = models.TextField(null=True, blank=True, unique=False, default="")
    modified = models.DateTimeField(auto_now=True, verbose_name="Date of modification", null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name="Date of creation", null=True, blank=True)
    is_global = models.BooleanField(default=False, verbose_name="Shown on all maps")
    import pytz
    TIMEZONE_CHOICES = [(str(t), str(t)) for t in pytz.common_timezones]
    time_zone=models.CharField(max_length=255, choices=TIMEZONE_CHOICES, default="Europe/Rome")

    # geom =              gismodels.PointField()
    # objects =           gismodels.GeoManager()

    class Meta:
        verbose_name = "Waypoint"
        ordering = ["time"]
        #app_label = "tracks"

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return "Waypoints"

    def __str__(self):
        return str(self.name)

    def set_timezone(self):
        from timezonefinder import TimezoneFinder
        from options.models import OptionSet

        try:
            tf = TimezoneFinder()
            timezone = tf.timezone_at(lng=self.long, lat=self.lat)
            self.time_zone = timezone
            logger.info("Setting timezone %s %s" %(self,timezone))
            self.save()
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.warning("Cannot set time_zone: %s" %e)
