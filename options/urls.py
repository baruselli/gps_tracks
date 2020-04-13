from django.conf.urls import url
from . import views

# from models import *
# from djgeojson.views import GeoJSONLayerView
from . import models
from django.views.decorators.cache import cache_page

urlpatterns = [
        url(r"^main$", views.OptionsSetsView.as_view(), name="options_main"),
        url(r"^options_set/(?P<id>[0-9]+)/$", views.EditOptionsView.as_view(), name="edit_options"),
        ]