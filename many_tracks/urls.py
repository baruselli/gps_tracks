from django.conf.urls import url
from . import views

# from models import *
# from djgeojson.views import GeoJSONLayerView
from . import models
from django.views.decorators.cache import cache_page
from django.views.generic import RedirectView

urlpatterns = [
#main
    url(r"^tracks/$" ,views.ManyTracksView.as_view() ,name="many_tracks" ,),
    url(r"^tracks_alts/$" ,views.ManyTracksAltsView.as_view() ,name="many_tracks_alts" ,),
    url(r"^delete/$" ,views.DeleteManyTracksView.as_view() ,name="many_tracks_delete" ,),
    url(r"^merge/$" ,views.ManyTracksMergeView.as_view() ,name="many_tracks_merge" ,),
    url(r"^plots/$", views.ManyTracksPlotsView.as_view(), name="many_tracks_plots", ),
    url(r"^merge/$" ,views.ManyTracksMergeView.as_view() ,name="many_tracks_source" ,),
]