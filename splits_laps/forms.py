from django import forms
from .models import *
from tracks.models import Track

class FindLapsForm(forms.Form):
    starting_lat = forms.FloatField(label='Starting Latitude', required=False)
    starting_lon = forms.FloatField(label='Starting Longitude', required=False)
    time_threshold= forms.IntegerField(label='Minimum duration of each lap (s)',initial=300)
    space_threshold = forms.FloatField(label='Radius to find beginning of each lap (m)',initial=50)
    threshold_length = forms.FloatField(label='Tolerance on lap lengths (%)',initial=10)
    min_laps = forms.IntegerField(label='Minimum number of laps',initial=2)
    max_laps = forms.FloatField(label='Maximum number of laps',initial=100)
    back_forth = forms.BooleanField(label='Ignore everything and divide the track in half', initial=False, required=False)


class TrackSplitsForm(forms.ModelForm):
    class Meta:
        model = Track
        fields = ["splits_km"]
