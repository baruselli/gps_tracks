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
from .models import MergedTrack
from tracks.models import Track

class MergedTracksListView(View):

    template_name = "merge_tracks/merged_tracks_index.html"

    def get(self, request, *args, **kwargs):
        logger.debug("MergedTracksListView")
        merged_tracks = MergedTrack.objects.all()

        return render(request, self.template_name, {"objs": merged_tracks})

class MergedTrackView(View):

    template_name = "merge_tracks/merged_track.html"

    def get(self, request, *args, **kwargs):
        logger.info("MergedTrackView")

        id = kwargs.get("id", None)
        object=MergedTrack.objects.get(pk=id)

        return render(
                request,
                self.template_name,
                {"obj": object, "id": id, "input_tracks":object.input_tracks(manager="all_objects").all()},
        )

class DeleteMergedTrackView(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages

        logger.info("DeleteMergedTrack")

        id = kwargs.get("id", None)
        
        object=MergedTrack.objects.get(pk=id)

        try:
            if object.output_track:
                object.output_track.delete()
            object.delete()
            message="OK Deleting MergedTrack %s" %object.name
        except Exception as e:
            message="KO deleting MergedTrack: %s" %e

        logger.info(message)
        messages.success(request, message)

        return redirect(reverse("merged_tracks_index"))

class CreateMergedTrackView(View):

    template_name = "merge_tracks/merged_track_edit.html"

    def get(self, request, *args, **kwargs):
        from .models import MergedTrack as Model

        id = kwargs.get("id", None)

        logger.debug("CreateMergedTrackView")

        if id:
            from .forms import MergedTrackForm as ModelForm
            object = Model.objects.get(pk=id)
            form = ModelForm(instance=object,
                    initial={'input_tracks': object.input_tracks(manager="all_objects").all() })
            # form.fields["input_tracks"].queryset = Track.all_objects.all()
            return render(
                request,
                self.template_name,
                {"obj": object, "id": id, "form": form,"input_tracks":object.input_tracks(manager="all_objects").all()},
            )
        else:
            from .forms import MergedTrackForm as ModelForm
            form = ModelForm()
            return render(
                request, self.template_name, {"form": form, "id": id}
            )

    def post(self, request, *args, **kwargs):
        from .models import MergedTrack as Model

        id = kwargs.get("id", None)

        if id:
            from .forms import MergedTrackForm as ModelForm
            instance = get_object_or_404(Model, pk=id)
            form = ModelForm(request.POST or None, instance=instance)
            new = False
            logger.info("Modify object %s" % id)
        else:
            from .forms import MergedTrackForm as ModelForm
            form = ModelForm(request.POST)
            new = True
            logger.info("Create object")

        if form.is_valid():
            f = form.save()
            id = f.pk
            instance = get_object_or_404(Model, pk=id)
            logger.info("Object pk %s" % f.pk)

            instance.save()

            instance.merge_tracks()

            messages.success(request, "OK")

            return HttpResponseRedirect(
                reverse("merged_track", kwargs={"id": id})
            )
        else:
            logger.error("Form")
            return render(
                request, self.template_name, {"form": form, "has_error": True}
            )

class ReimportMergedTrackView(View):

    def get(self, request, *args, **kwargs):
        from .models import MergedTrack
        id = kwargs.get("id", None)

        logger.debug("ReimportMergedTrackView")

        object = MergedTrack.objects.get(pk=id)
        object.merge_tracks()

        from django.contrib import messages
        messages.success(request, "OK reimport")

        return redirect(reverse("track_detail", kwargs={"track_id": object.output_track.pk}))
