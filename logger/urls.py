from django.conf.urls import url
from . import views

# from models import *
# from djgeojson.views import GeoJSONLayerView
from . import models
from django.views.decorators.cache import cache_page
from django.views.generic import RedirectView

urlpatterns = [
    url(r"^track/(?P<track_id>[0-9]+)/log/$" ,views.TrackLogView.as_view() ,name="track_log" ,),
    url(r"^main/$" ,views.LogsView.as_view() ,name="logs" ,),
    url(r"^log/$" ,views.LogView.as_view() ,name="log" ,),
    url(r"^download_log/$" ,views.DownloadLogView.as_view() ,name="download_log" ,),
]