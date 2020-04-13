from django.conf.urls import url
from . import views

# from models import *
# from djgeojson.views import GeoJSONLayerView
from . import models
from django.views.decorators.cache import cache_page
from django.views.generic import RedirectView

urlpatterns = [
    url(r"^main", views.ProfileListView.as_view(), name="user_index"),
    url(r"^delete/(?P<user_id>[0-9]+)/$", views.DeleteProfileView.as_view(), name="delete_user", ),
    url(r"^create$", views.CreateProfileView.as_view(), name="create_user"),
    url(r"^user/(?P<user_id>[0-9]+)/$", views.ProfileView.as_view(), name="user_detail", ),
    url(r"^user/modify/(?P<user_id>[0-9]+)/$", views.CreateProfileView.as_view(), name="edit_user", ),
    url(r"^user/assignfreetrackstouser/(?P<user_id>[0-9]+)/$", views.AssignTracksProfileView.as_view(),name="assignfreetrackstouser", ),
]