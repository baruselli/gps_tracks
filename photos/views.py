from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from .models import *
from tracks.models import Track
import json
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from pprint import pprint
import logging
import traceback

logger = logging.getLogger("gps_tracks")



class PhotosShowView(View):

    template_name = "photos/photos_show.html"

    def get(self, request, *args, **kwargs):
        logger.debug("PhotosShowView")

        from .forms import FindGroupForm

        name=request.GET.get("name","")
        n_days=request.GET.get("n_days","")
        year=request.GET.get("year","")
        country=request.GET.get("country","")
        q=request.GET.get("q","")
        min_date=request.GET.get("min_date","")
        max_date=request.GET.get("max_date","")
        group_pk=request.GET.get("group_pk","")
        group_form=FindGroupForm(initial={"group_pk":group_pk})
        how_many=request.GET.get("how_many","")
        lat=request.GET.get("lat","")
        lng=request.GET.get("lng","")
        dist=request.GET.get("dist","")
        time_zone = request.GET.get('time_zone', "")
        by_id = request.GET.get('by_id', None)
        address = request.GET.get('address', "")
        track_ids = request.GET.get('track_ids', None)
        photo_ids = request.GET.get('photo_ids', None)
        view_type = request.GET.get('view_type', "show")


        ## option to avoid doing any search (for page initialization)
        no_search = request.GET.get('no_search', "")

        ## General remark: "None" is to filter for objects with the given field null or empty
        ## "" is no filtering for the given field

        country_options =  list(set(Photo.objects.values_list('country',flat=True).distinct()))
        country_options = list(set([str(y) if y else "None" for y in country_options]))
        country_options.sort()
        if "" not in country_options:
            country_options = [""]+country_options

        year_options =  set(Photo.objects.values_list('time__year',flat=True).distinct())
        year_options = [str(y) if y else "None" for y in year_options]
        year_options.sort(reverse=True)
        if "" not in year_options:
            year_options = [""]+year_options

        timezone_options =  set(Photo.objects.values_list('time_zone',flat=True).distinct())
        timezone_options = [str(y) if y else "None" for y in timezone_options]
        timezone_options.sort()
        if "" not in timezone_options:
            timezone_options = [""]+timezone_options

        if lat and lng and not dist:
            dist=3

        from .forms import FindTracksForm
        if track_ids:
            ids_list=[int(i) for i in track_ids.split("_")]
            track_form = FindTracksForm(initial={"tracks":ids_list})
            track_form.fields['tracks'].initial=ids_list
        else:
            track_form = FindTracksForm()

        from .forms import FindPhotosForm
        if photo_ids:
            ids_list=[int(i) for i in photo_ids.split("_")]
            photo_form = FindPhotosForm(initial={"photos":ids_list})
            photo_form.fields['photos'].initial=ids_list
        else:
            photo_form = FindPhotosForm()


        return render(
            request,
            self.template_name,
            {
             "request":request.GET.urlencode(),
             "name":name,
             "n_days":n_days,
             "year":year,
             "country":country,
             "q":q,
             "min_date":min_date,
             "max_date":max_date,
             "group_pk":group_pk,
             "group_form":group_form,
             "country_options": country_options,
             "how_many":how_many,
             "year_options":year_options,
             "lat":lat,
             "lng":lng,
             "dist":dist,
             "time_zone":time_zone,
             "timezone_options":timezone_options,
             "by_id":by_id,
             "address":address,
             "track_form":track_form,
             "photo_form":photo_form,
             "view_type":view_type,
             },
        )

class PhotoView(View):

    template_name = "photos/photo.html"

    def get(self, request, *args, **kwargs):

        photo_id = kwargs.get("photo_id", None)
        photo = get_object_or_404(Photo, pk=photo_id)
        logger.debug("PhotoView %s" %photo_id)
        from .forms import PhotoForm  as ModelForm
        form = ModelForm(instance=photo)

        return render(request, self.template_name, {"photo": photo,"request": request.GET.urlencode(),"form":form})


    def post(self, request, *args, **kwargs):

        from .forms import PhotoForm as ModelForm
        photo_id = kwargs.get("photo_id", None)

        instance = get_object_or_404(Photo, pk=photo_id)
        form = ModelForm(request.POST or None, instance=instance)
        logger.info("Modify object %s" % photo_id)

        if form.is_valid():
            f = form.save()
            id = f.pk
            logger.info("Object pk %s" % f.pk)

            messages.success(request, "OK")

            return HttpResponseRedirect(
                reverse("photo_detail", kwargs={"photo_id": id})
            )
        else:
            logger.error("Form")
            return render(
                request, self.template_name, {"form": form, "has_error": True}
            )

class DeletePhotos(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages
        from .models import Photo

        logger.info("DeletePhotos")
        Photo.objects.all().delete()

        message = "All photos deleted"
        messages.success(request, message)
        logger.info(message)

        return redirect(reverse("import"))

class LinkPhotos(View):
    def get(self, request, *args, **kwargs):
        from .utils import associate_photos_to_tracks
        import threading
        from django.contrib import messages
        logger.info("LinkPhotos")

        t = threading.Thread(target=associate_photos_to_tracks())
        t.start()

        message = "Started import in a parallel thread, check logs for details"
        messages.success(request, message)

        return redirect(reverse("import"))

class LinkPhotosTrackView(View):
    def get(self, request, *args, **kwargs):
        from .utils import associate_photos_to_tracks
        import threading
        from django.contrib import messages
        logger.info("LinkPhotos")

        track_id = kwargs.get("track_id", None)
        track = get_object_or_404(Track.all_objects, pk=track_id)

        result=associate_photos_to_tracks(track_list=[track])
        from django.contrib import messages
        messages.success(request, result)

        return redirect(reverse("track_detail", args=(track_id,)))

class EditPhotoView(View):

    template_name = "photos/photo_edit.html"

    def get(self, request, *args, **kwargs):
        from .models import Photo as Model

        from .forms import PhotoForm as ModelForm

        id = kwargs.get("id", None)

        logger.info("EditPhotoView %s" %form_id)


        if id:
            object = Model.objects.get(pk=id)
            form = ModelForm(instance=object)
            return render(
                request,
                self.template_name,
                {"object": object, "id": id, "form": form},
            )
        else:
            form = ModelForm()
            return render(
                request, self.template_name, {"form": form, "id": id}
            )

    def post(self, request, *args, **kwargs):
        from .models import Photo as Model

        from .forms import PhotoForm as ModelForm

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

            messages.success(request, "OK")

            return HttpResponseRedirect(
                reverse("photo_detail",  kwargs={"photo_id": id} )
            )
        else:
            logger.error("Form")
            return render(
                request, self.template_name, {"form": form, "has_error": True}
            )

class PhotosListGeneralView(View):

    template_name = "photos/photo_index_gen.html"

    def get(self, request, *args, **kwargs):

        logger.debug("PhotosListGeneralView")
        import datetime
        from datetime import datetime, timedelta
        today=datetime.today()

        from .utils import filter_photos

        #by date
        n_days=[1,7,30,120,365,9999]

        count_dict={
            d : filter_photos({"n_days":d}).count() for d in n_days
        }

        all_photos=Photo.objects.all().count()
        nulldate_photos = filter_photos({"n_days":-1}).count()

        #by year
        times = set(Photo.objects.values_list('time', flat=True))
        years = set([t.year for t in times if t])
        #years = sorted(list(years))
        count_years_list=[
            {"year":y,"n_photos": filter_photos({"year":y}).count()}
        for y in years
        ]

        # by country
        countries=set(Photo.objects.values_list('country', flat=True))
        if ""  in countries and None in countries:
            countries=countries-set([""])
        countries=list(countries)
        if None in countries:
            countries.remove(None)
            countries.append("None")
        if "" in countries:
            countries.remove("")
            countries.append("None")
        count_country_dict={
            c : filter_photos({"country":c}).count() for c in countries
        }

        return render(request, self.template_name, {"count_dict": count_dict,
                                                    "all_photos":all_photos,
                                                    "nulldate_photos":nulldate_photos,
                                                    "count_years_list":count_years_list,
                                                    "count_country_dict":count_country_dict
                                                    })

## autocomplete
from dal import autocomplete

class PhotoAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        qs = Photo.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q).order_by("-pk")

        return qs                                                    