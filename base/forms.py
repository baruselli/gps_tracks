from django import forms
from dal import autocomplete
from tracks.models import Track
from groups.models import Group


class TrackSearchForm(forms.Form):
    track = forms.ModelChoiceField(
        queryset=Track.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url='track-autocomplete'),
        label="Quick search tracks"
    )

class GroupSearchForm(forms.Form):
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        widget=autocomplete.ModelSelect2(url='group-autocomplete'),
        label="Quick search group"
    )