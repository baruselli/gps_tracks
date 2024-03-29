from django.conf.urls import url
from . import views

# from models import *
# from djgeojson.views import GeoJSONLayerView
from . import models
from django.views.decorators.cache import cache_page
from django.views.generic import RedirectView

urlpatterns = [
    url(r"^quick_import_execute/(?P<id>[0-9]+)/$", views.QuickImportExecuteView.as_view(), name="quick_import_execute", ),
    url(r"^quick_import_edit/(?P<id>[0-9]+)/$", views.QuickImportEditView.as_view(), name="quick_import_edit", ),
    url(r"^quick_import_edit/$", views.QuickImportEditView.as_view(), name="quick_import_edit", ),
    url(r"^quick_import_delete/(?P<id>[0-9]+)/$", views.QuickImportDeleteView.as_view(), name="quick_import_delete", ),
]