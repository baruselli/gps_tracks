from django import forms
from .models import *
from dal import autocomplete
from groups.models import Group


class SmoothTrackForm(forms.Form):
    CHOICES = (('1','Ramer-Douglas-Peucker algorithm (max distance - m)'),
               ('2','Simplify (max number of points)'),
               ('3','Simplify (max fraction of points)'),
               ('4','Simplify (min distance - m)'),)
    algorithm = forms.ChoiceField(choices=CHOICES)
    parameter = forms.FloatField(label='Parameter')


class TrackGroupForm(forms.ModelForm):
    class Meta:
        model = Track
        fields = ["description","groups","user","time_zone","starting_index","ending_index", "is_active"]
        widgets = {'groups': forms.widgets.CheckboxSelectMultiple() }

    def __init__(self, *args, **kwargs):
        super(TrackGroupForm, self).__init__(*args, **kwargs)
        from groups.models import Group
        # exclude auto generated groups
        self.fields["groups"].queryset = Group.objects.exclude(is_path_group=True).exclude(hide_in_forms=True)



class FindGroupForm(forms.Form):
    
    group_pk_search =  	forms.ModelMultipleChoiceField(
        widget = autocomplete.ModelSelect2(url='group-autocomplete'),
        queryset = Group.objects.filter(),
        label="Group",
        required = False,
    )

class FindTracksForm(forms.Form):
    tracks = forms.ModelChoiceField(
        queryset=Track.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url='track-autocomplete'),
        label="Tracks",
        required = False,
    )


