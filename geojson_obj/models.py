from django.db import models
import json

from django.urls import reverse
from pprint import pprint
import traceback

import logging
logger = logging.getLogger("gps_tracks")


class GeoJsonObject(models.Model):
    name = models.CharField(max_length=512, verbose_name="Object Name", null=False, blank=False, unique=True)
    geojson = models.TextField(verbose_name="GeoJSON", null=True, blank=True, unique=False)
    website = models.TextField(verbose_name="Website address", null=True, blank=True, unique=False)
    modified = models.DateTimeField(auto_now=True, verbose_name="Date of modification", null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name="Date of creation", null=True, blank=True)
    is_global = models.BooleanField(default=False, verbose_name="Shown on all maps")
    is_valid = models.CharField(default="", verbose_name="Is valid GeoJSON", max_length=10)
    errors = models.TextField(verbose_name="GeoJSON validation errors", null=True, blank=True, unique=False)
    min_lat = models.FloatField(null=True, blank=True)
    min_lon = models.FloatField(null=True, blank=True)
    max_lat = models.FloatField(null=True, blank=True)
    max_lon = models.FloatField(null=True, blank=True)
    feature_for_name=models.CharField(max_length=512, null=True, blank=True,verbose_name="Property name under properties to be shown on popup (only for FeatureCollection)")

    class Meta:
        verbose_name = "GeoJsonObject"
        ordering = ["pk"]
        #app_label = "tracks"


    def __unicode__(self):
        return "GeoJsonObject" + str(self.pk)

    def __repr__(self):
        return "GeoJsonObject"

    def __str__(self):
        return str(self.name)

    def get_geojson(self):
        if self.geojson:
            logger.debug("reading saved text")
            json_ok = json.loads(self.geojson)
            # in FeatureCollection I give to all subfeatures feature_for_name to get their name
            if "type" in json_ok and "features" in json_ok and json_ok["type"]=="FeatureCollection":
                for f in json_ok["features"]:
                    f["feature_for_name"] = self.feature_for_name
                    f["point_type"] = "external_geojson" # not needed, just for info
            # otherwise, i assign name by hand
            json_ok["external_geojson_name"] = self.name
            json_ok["point_type"] = "external_geojson" # not needed, just for info
        elif self.website:
            logger.info("downloading from website")
            import urllib.request

            url = self.website
            response = urllib.request.urlopen(url)
            data = response.read()
            text = data.decode('utf-8')
            json_ok = json.loads(text)
            self.geojson = text
            self.save()
            self.set_properties()
            logger.info("OK downloading and saving to db")
        else:
            json_ok = {}
        return json_ok

    def set_properties(self):
        logger.info("set_properties")
        import geojson
        obj=geojson.loads(self.geojson)
        self.is_valid=obj.is_valid
        self.errors = obj.errors()
        min_lat=1000
        max_lat = -1000
        min_lon = 1000
        max_lon = -1000


        if "bbox" in obj.keys():
            try:
                min_lon,min_lat,max_lon,max_lat = obj["bbox"]
            except:
                pass
        if min_lat==1000:
            try:
                lats = [a[1] for a in geojson.utils.coords(obj)]
                long = [a[0] for a in geojson.utils.coords(obj)]
                min_lat = min(min_lat,min(lats))
                min_lon = min(min_lon, min(long))
                max_lat = max(max_lat, max(lats))
                max_lon = max(max_lon, max(long))
            except:
                pass
        if min_lat==1000:
            for child in obj:
                try:
                    lats = [a[1] for a in geojson.utils.coords(obj[child])]
                    long = [a[0] for a in geojson.utils.coords(obj[child])]
                    min_lat = min(min_lat, min(lats))
                    min_lon = min(min_lon, min(long))
                    max_lat = max(max_lat, max(lats))
                    max_lon = max(max_lon, max(long))
                except:
                    pass
        #print(min_lat, min_lon, max_lat,max_lon)
        self.min_lat = min_lat
        self.min_lon = min_lon
        self.max_lat = max_lat
        self.max_lon = max_lon
        self.save()