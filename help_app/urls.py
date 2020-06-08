from django.conf.urls import url
from . import views

# from models import *
# from djgeojson.views import GeoJSONLayerView
from . import models
from django.views.decorators.cache import cache_page
from django.views.generic import RedirectView



urlpatterns = [
        url(r"^main/$", views.HelpView.as_view(), name="help", ),
        url(r"^about/$", views.AboutView.as_view(), name="about", ),
]