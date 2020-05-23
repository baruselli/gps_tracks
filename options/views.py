from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
import json
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from pprint import pprint
import logging
import traceback
logger = logging.getLogger("gps_tracks")
from django.conf import settings
from .models import *

class EditOptionsView(View):

    template_name = "options/edit_options.html"

    def get(self, request, *args, **kwargs):
        from .forms import OptionsForm as ModelForm
        from .models import OptionSet as Model

        id = kwargs.get("id", None)

        logger.debug("EditOptionsView")

        show_google_maps=settings.SHOW_GOOGLE_MAPS

        if id:
            object = Model.objects.get(pk=id)
            form = ModelForm(instance=object)
            basemaps = eval(object.BASEMAPS)
            return render(
                request,
                self.template_name,
                {"object": object, "id": id, "form": form, "basemaps":basemaps,"show_google_maps":show_google_maps},
            )
        else:
            form = ModelForm()
            return render(
                request, self.template_name, {"form": form, "id": id, "basemaps":[]}
            )

    def post(self, request, *args, **kwargs):
        from .forms import OptionsForm as ModelForm
        from .models import OptionSet as Model

        id = kwargs.get("id", None)

        if id:
            instance = get_object_or_404(Model, pk=id)
            form = ModelForm(request.POST or None, instance=instance)
            new = False
            logger.info("Modify object %s" %id)
        else:
            form = ModelForm(request.POST)
            new = True
            logger.info("Create object")

        if form.is_valid():
            f = form.save()
            id = f.pk
            instance = get_object_or_404(Model, pk=id)
            logger.info("Object pk %s" %f.pk)

            instance.BASEMAPS=str(request.POST.getlist('maps_checks'))
            instance.save()

            messages.success(request, "OK")

            return HttpResponseRedirect(
                reverse("edit_options",  kwargs={"id": id} )
            )
        else:
            logger.error("Form")
            return render(
                request, self.template_name, {"form": form, "has_error": True}
            )


class OptionsSetsView(View):

    template_name = "options/options_sets.html"

    def get(self, request, *args, **kwargs):

        sets = OptionSet.objects.all()

        logger.debug("OptionsSetsView")

        return render(
            request, self.template_name, {"sets": sets}
        )