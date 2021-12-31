from django.conf.urls import url
from . import views

# from models import *
# from djgeojson.views import GeoJSONLayerView
from . import models
from django.views.decorators.cache import cache_page
from django.views.generic import RedirectView

urlpatterns = [
    url(r"^tomtom", views.DownloadTomtom.as_view(), name="download_tomtom", ),
    url(r"^garmin", views.DownloadTomtom.as_view(), name="download_garmin", ),
    url(r"^googledrive/tracks",views.GoogleDriveTracksView.as_view(),name="google_drive_tracks",),
    url(r"^googledrive/photos", views.GoogleDrivePhotosView.as_view(), name="google_drive_photos", ),
    url(r"^googlephotos", views.GooglePhotosView.as_view(), name="google_photos", ),
]
