from django.conf.urls import url
from . import views

# from models import *
# from djgeojson.views import GeoJSONLayerView
from . import models
from django.views.decorators.cache import cache_page
from django.views.generic import RedirectView

urlpatterns = [
    #index
    url(r"^main$", views.GroupListView.as_view(), name="group_index"),
    #single_group
    url(r"^group/(?P<group_id>[0-9]+)/$", views.GroupView.as_view(), name="group_detail"),
    url(r"^group/create/$", views.CreateGroupView.as_view(), name="create_group", ),
    url(r"^group/modify/(?P<form>[a-zA-Z0-9-]+)/(?P<group_id>[0-9]+)/$", views.CreateGroupView.as_view(),name="edit_group", ),
    url(r"^group/resave/(?P<group_id>[0-9]+)/$", views.ResaveGroupView.as_view(), name="resave_group", ),
    url(r"^group/delete/(?P<group_id>[0-9]+)$", views.DeleteGroupView.as_view(), name="delete_group", ),
    url(r"^group/plot/(?P<group_id>[0-9]+)/$", views.GroupPlotsView.as_view(), name="group_plots", ),
    url(r"^group/statistics/(?P<group_id>[0-9]+)/$", views.GroupStatisticsView.as_view(), name="group_statistics", ),
    #many groups
    url(r"^resave_all/$$", views.ResaveAllGroupsView.as_view(), name="resave_all_groups", ),
    url(r"^delete$", views.DeleteGroups.as_view(), name="delete_groups"),
    url(r"^autocreate$",views.CreateGroups.as_view(), name="autocreate_groups",),
    #autocomplete
    url(r'^group-autocomplete/$',views.GroupAutocomplete.as_view(),name='group-autocomplete', ),
    # rules
    url(r'^group_rules/$',views.GroupRulesView.as_view(),name='group_rules', ),
    url(r'^group_rule/(?P<rule_id>[0-9]+)/$',views.GroupRuleView.as_view(),name='group_rule', ),
    url(r'^group_rule/$',views.GroupRuleView.as_view(),name='group_rule_new', ),
    url(r'^group_rule_delete/(?P<rule_id>[0-9]+)/$',views.GroupRuleDeleteView.as_view(),name='group_rule_delete', ),

]