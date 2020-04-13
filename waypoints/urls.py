from django.conf.urls import url
from . import views

# from models import *
# from djgeojson.views import GeoJSONLayerView
from . import models
from django.views.decorators.cache import cache_page
from django.views.generic import RedirectView

urlpatterns = [
    #main
    # url(r"^main", views.WaypointListView.as_view(), name="waypoint_index"),
    url(r"^main$", views.WaypointListGeneralView.as_view(), name="waypoint_gen_index"),
    url(r"^waypoints_list", views.WaypointListView.as_view(), name="waypoint_index"),
    #single
    url(r"^waypoint/(?P<waypoint_id>[0-9]+)/$", views.WaypointView.as_view(), name="waypoint_detail", ),
    url(r"^waypoint/create/$", views.CreateWaypointView.as_view(), name="create_waypoint", ),
    url(r"^waypoint/delete/(?P<waypoint_id>[0-9]+)/$", views.DeleteWaypointView.as_view(), name="delete_waypoint", ),
    url(r"^waypoint/modify/(?P<waypoint_id>[0-9]+)/$", views.CreateWaypointView.as_view(),name="create_waypoint", ),
    #many
    url(r"^map$", views.AllWaypointsView.as_view(), name="waypoints_map"),
    url(r"^delete$", views.DeleteWaypoints.as_view(), name="delete_wps"),
    #autocomplete
    url(r'^waypoint-autocomplete/$',views.WaypointAutocomplete.as_view(),name='waypoint-autocomplete', ),

]