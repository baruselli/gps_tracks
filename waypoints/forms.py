from django import forms
from .models import *
from dal import autocomplete
from groups.models import Group
from tracks.models import Track


class WaypointForm(forms.ModelForm):
    class Meta:
        model = Waypoint
        fields = ["lat", "long", "alt", "name","description","comment",
            "is_global","country","region","city","track","track2"]
        widgets = {
            "track":autocomplete.ModelSelect2(url='track-autocomplete') ,
            "track2":autocomplete.ModelSelect2(url='track-autocomplete') 
            }
        # track = forms.CharField(widget=forms.HiddenInput())

class FindGroupForm(forms.Form):
    
    group_pk =  	forms.ModelMultipleChoiceField(
        widget = autocomplete.ModelSelect2(url='group-autocomplete'),
        queryset = Group.objects.filter(),
        label="Group",
        required = False
    )

class FindTracksForm(forms.Form):
    
    tracks =  	forms.ModelMultipleChoiceField(
        widget = autocomplete.ModelSelect2Multiple(url='track_all-autocomplete'),
        queryset = Track.all_objects.filter(),
        label = "Tracks",
        required = False
    )

class FindWaypointsForm(forms.Form):
    
    waypoints =  	forms.ModelMultipleChoiceField(
        widget = autocomplete.ModelSelect2Multiple(url='waypoint-autocomplete'),
        queryset = Waypoint.objects.filter(),
        label = "Waypoints",
        required = False
    )