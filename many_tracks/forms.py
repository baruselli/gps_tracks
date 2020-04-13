from django import forms
import os
from django.conf import settings
from tracks.models import Track
from dal import autocomplete
from groups.models import Group

class FindTracksForm(forms.Form):
    
    tracks =  	forms.ModelMultipleChoiceField(
        widget = autocomplete.ModelSelect2Multiple(url='track_all-autocomplete'),
        queryset = Track.all_objects.filter(),
        required=True
    )

