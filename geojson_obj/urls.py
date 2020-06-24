from django.conf.urls import url
from . import views

# from models import *
# from djgeojson.views import GeoJSONLayerView
from . import models
from django.views.decorators.cache import cache_page
from django.views.generic import RedirectView

urlpatterns = [
    url(r"^main/", views.GeoJsonObjectListView.as_view(), name="geojson_index", ),
    url(r"^edit/(?P<geojsonobj_id>[0-9]+)/", views.CreateGeoJsonView.as_view(), name="geojsonobj_edit", ),
    url(r"^download/(?P<geojsonobj_id>[0-9]+)/", views.DwonloadGeoJsonView.as_view(), name="geojson_download", ),
    url(r"^edit/", views.CreateGeoJsonView.as_view(), name="geojsonobj_edit", ),
    url(r"^(?P<geojsonobj_id>[0-9]+)/", views.GeoJsonObjectView.as_view(), name="geojsonobj", ),
    url(r"^set_properties/(?P<geojsonobj_id>[0-9]+)/", views.GeoJsonSetPropertiesView.as_view(),name="geojsonobj_properties", ),
    url(r"^map/", views.GeoJsonObjectMapView.as_view(), name="geojson_map", ),
]