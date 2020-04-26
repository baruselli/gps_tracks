from django.db import models
from django.contrib.postgres.fields import ArrayField
from tracks.models import call_clsinit
import logging
logger = logging.getLogger("gps_tracks")
from django.conf import settings
import json

#possible line types. if adding a new type, add the corresponding color in CreateLineView in views.py
LINE_TYPES = (
    ('path','Path'),
    ('border','Border'),
    ('canal','Canal'),
    ('river','River'),
    ('other','Other'),
    )

# def call_clsinit(cls):
#     """https://stackoverflow.com/questions/12115357/calling-a-class-method-upon-creation-of-python-classes"""
#     cls._clsinit()
#     return cls
@call_clsinit
class Line(models.Model):

    name = models.CharField(
        max_length=255, verbose_name="Name", null=True, blank=True, unique=False
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name="Date of creation", null=True, blank=True)
    modified = models.DateTimeField(auto_now=True, verbose_name="Date of modification", null=True, blank=True)
    enabled = models.BooleanField(default=True, verbose_name="Enabled")
    created_by_hand = models.BooleanField(default=True, verbose_name="Created by hand")
    beg_country = models.CharField(
        max_length=50, null=True, blank=True, unique=False, default=""
    )
    beg_region = models.CharField(
        max_length=100, null=True, blank=True, unique=False, default=""
    )
    beg_city = models.CharField(
        max_length=50, null=True, blank=True, unique=False, default=""
    )
    beg_address = models.CharField(
        max_length=250, null=True, blank=True, unique=False, default=""
    )
    end_country = models.CharField(
        max_length=50, null=True, blank=True, unique=False, default=""
    )
    end_region = models.CharField(
        max_length=100, null=True, blank=True, unique=False, default=""
    )
    end_city = models.CharField(
        max_length=50, null=True, blank=True, unique=False, default=""
    )
    end_address = models.CharField(
        max_length=250, null=True, blank=True, unique=False, default=""
    )
    lats_text = models.TextField(verbose_name="Lats", null=True, blank=True, unique=False,default="[]")
    long_text = models.TextField(verbose_name="Long", null=True, blank=True, unique=False,default="[]")
    alts_text = models.TextField(verbose_name="Alts", null=True, blank=True, unique=False,default="[]")
    if settings.USE_TEXT_INSTEAD_OF_ARRAYS:
        _lats = models.TextField( null=True, default=("[]"))
        _long = models.TextField( null=True, default=("[]"))
        _alts = models.TextField( null=True, default=("[]"))
        _lengths = models.TextField( null=True, default=("[]"))
    else:
        _lats = ArrayField(models.FloatField(), size=None, null=True, default=list)
        _long = ArrayField(models.FloatField(), size=None, null=True, default=list)
        _alts = ArrayField(models.FloatField(), size=None, null=True, default=list)
        _lengths = ArrayField(models.FloatField(), size=None, null=True, default=list)
    total_length = models.FloatField(null=True, blank=True)
    closed= models.BooleanField(default=False,verbose_name="Make first and last point coincide")
    n_points = models.IntegerField(blank=False, null=True,default=0)
    line_type = models.CharField(max_length=255, verbose_name="Type", null=True, blank=True, unique=False,choices=LINE_TYPES)
    color = models.CharField(max_length=255, verbose_name="Color", null=True, blank=True, unique=False)
    track = models.ForeignKey("tracks.Track", null=True, blank=True ,on_delete=models.SET_NULL)
    is_global = models.BooleanField(default=True, verbose_name="Shown on all maps")
    min_lat= models.FloatField(null=True)
    max_lat = models.FloatField(null=True)
    min_long = models.FloatField(null=True)
    max_long = models.FloatField(null=True)

    def array_property(property_name):
        """ Create and return a property for the given field. """
        @property
        def prop(self):
            ok_prop = getattr(self, property_name)
            if settings.USE_TEXT_INSTEAD_OF_ARRAYS:
                ok_prop=json.loads(ok_prop)

            return ok_prop

        @prop.setter
        def prop(self, value):
            logger.info("Using %s setter" %property_name)
            if settings.USE_TEXT_INSTEAD_OF_ARRAYS:
                value=json.dumps(value)
            setattr(self, property_name, value)

        return prop

    @classmethod
    def _clsinit(cls):
        """automatically create getters/setters for all given  fields, with name obtained removing first character (_), hence [1:]"""
        for field in ["_lats","_long","_alts","_length"]:
            property = cls.array_property(field)
            setattr(cls,field[1:],property)

    class Meta:
        verbose_name = "Line"
        ordering = ["pk"]
        #app_label = "tracks"


    def __unicode__(self):
        return "Line " + str(self.name)


    def __repr__(self):
        return "Line " + str(self.name)


    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if self.lats and self.long:
            self.min_lat = min(self.lats)
            self.min_long = min(self.long)
            self.max_lat = max(self.lats)
            self.max_long = max(self.long)
        super(Line, self).save(*args, **kwargs)


