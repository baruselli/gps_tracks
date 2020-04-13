from django import forms
from tracks.models import Track
from django.contrib.admin.widgets import FilteredSelectMultiple
import os
from django.conf import settings
from .models import MergedTrack
from dal import autocomplete

class MergedTrackForm(forms.ModelForm):
    class Meta:
        model = MergedTrack
        fields = ["name","delete_original_tracks","input_tracks","order"]
        widgets = {"input_tracks":autocomplete.ModelSelect2Multiple(url='track_all-autocomplete') }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['input_tracks'].queryset = Track.all_objects

    # necessario insieme a initial= se no non viene autocompletato con oggetti gia esistenti ma nascosti