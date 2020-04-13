from django import forms
from .models import *
from dal import autocomplete
from groups.models import Group
from tracks.models import Track

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ["lat", "long", "alt", "name","description","tracks","is_global",
                "country","region","city"]
        widgets = {
            "tracks":autocomplete.ModelSelect2Multiple(url='track-autocomplete') ,
            }

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

class FindPhotosForm(forms.Form):
    
    photos =  	forms.ModelMultipleChoiceField(
        widget = autocomplete.ModelSelect2Multiple(url='photo-autocomplete'),
        queryset = Photo.objects.filter(),
        label = "Photos",
        required = False
    )