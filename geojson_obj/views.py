from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from .models import GeoJsonObject
import json
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from pprint import pprint
import logging
import traceback
logger = logging.getLogger("gps_tracks")



class CreateGeoJsonView(View):

    template_name = "geojson_obj/geojson_edit.html"
    from .forms import GeoJsonObjectForm

    def get(self, request, *args, **kwargs):
        from .forms import GeoJsonObjectForm, GeoJsonObjectFormShort

        geojsonobj_id = kwargs.get("geojsonobj_id", None)

        logger.debug("CreateGeoJsonView")

        if geojsonobj_id:
            geojsonobj = GeoJsonObject.objects.get(pk=geojsonobj_id)
            # if you have a long geojson, it takes ages to load, so i dont show it
            if len(geojsonobj.geojson)<10000:
                form = GeoJsonObjectForm(instance=geojsonobj)
            else:
                form = GeoJsonObjectFormShort(instance=geojsonobj)
            return render(
                request,
                self.template_name,
                {"obj": geojsonobj, "geojsonobj_id": geojsonobj_id, "form": form},
            )
        else:
            form = GeoJsonObjectForm(
                {
                }
            )
            return render(
                request, self.template_name, {"form": form, "geojsonobj_id": geojsonobj_id}
            )

    def post(self, request, *args, **kwargs):
        from .forms import GeoJsonObjectForm, GeoJsonObjectFormShort
        from datetime import datetime

        geojsonobj_id = kwargs.get("geojsonobj_id", None)

        if geojsonobj_id:
            instance = get_object_or_404(GeoJsonObject, pk=geojsonobj_id)
            if len(instance.geojson)<10000:
                form = GeoJsonObjectForm(request.POST or None, instance=instance)
            else:
                form = GeoJsonObjectFormShort(request.POST or None, instance=instance)
            new = False
            logger.info("Modify geojsonobj %s" %geojsonobj_id)
        else:
            form = GeoJsonObjectForm(request.POST)
            new = True
            logger.info("Create geojsonobj")

        if form.is_valid():
            f = form.save()
            geojsonobj_id = f.pk
            logger.info("geojsonobj pk %s" %f.pk)

            geojsonobj = GeoJsonObject.objects.get(pk=geojsonobj_id)

            if geojsonobj.website:
                geojsonobj.geojson=""
            geojsonobj.geojson = geojsonobj.geojson.replace("'", "\"")
            geojsonobj.save()



            return HttpResponseRedirect(
                reverse("geojsonobj", kwargs={"geojsonobj_id": geojsonobj_id})
            )
        else:
            logger.error("Form geojsonobj_id")
            return render(
                request, self.template_name, {"form": form, "has_error": True}
            )

class GeoJsonObjectView(View):
    template_name = "geojson_obj/geojson.html"
    def get(self, request, *args, **kwargs):

        obj_id = kwargs.get("geojsonobj_id", None)
        obj = get_object_or_404(GeoJsonObject, pk=obj_id)
        logger.info("GeoJsonObjectView %s" % obj_id)

        return render(
            request, self.template_name, {"obj":obj}
        )

class GeoJsonObjectListView(View):
    template_name = "geojson_obj/geojson_index.html"
    def get(self, request, *args, **kwargs):
        logger.info("GeoJsonObjectListView")

        objs =GeoJsonObject.objects.all()

        return render(
            request, self.template_name, {"objs":objs}
        )

class GeoJsonSetPropertiesView(View):
    def get(self, request, *args, **kwargs):
        logger.info("GeoJsonSetPropertiesView")

        obj_id = kwargs.get("geojsonobj_id", None)
        obj = get_object_or_404(GeoJsonObject, pk=obj_id)
        logger.info("GeoJsonObject %s" % obj_id)

        obj.set_properties()

        return redirect(reverse("geojsonobj", args=(obj_id,)))

class GeoJsonObjectMapView(View):
    template_name = "geojson_obj/geojson_map.html"
    def get(self, request, *args, **kwargs):
        logger.info("GeoJsonObjectMapView")

        objs =GeoJsonObject.objects.all()

        return render(
            request, self.template_name, {"objs":objs}
        )
