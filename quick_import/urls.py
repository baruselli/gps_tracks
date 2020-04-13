from django.conf.urls import url
from . import views

# from models import *
# from djgeojson.views import GeoJSONLayerView
from . import models
from django.views.decorators.cache import cache_page
from django.views.generic import RedirectView

urlpatterns = [
    url(r"^tracks_photos_google$", views.TracksPhotosImportView.as_view(), name="quick_import"),
    url(r"^quick_import_tomtom", views.QuickImportTomtomView.as_view(), name="quick_import_tomtom"),
]