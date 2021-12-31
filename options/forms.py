from django import forms
from .models import *
import matplotlib.cm

class OptionsForm(forms.ModelForm):
    class Meta:
        COLOR_CHOICES = [[a,a] for a in matplotlib.cm.cmap_d.keys()]
        model = OptionSet
        exclude=["BASEMAPS"]
        widgets = {
             'TOMTOM_PASSWORD': forms.PasswordInput(render_value = True),
             'GARMIN_PASSWORD': forms.PasswordInput(render_value = True),
             "GMAIL_PWD": forms.PasswordInput(render_value = True),
             "COLORSCALE_LISTS":forms.Select(choices=COLOR_CHOICES),
             "COLORSCALE_RANKS": forms.Select(choices=COLOR_CHOICES),
             "COLORSCALE_TRACK": forms.Select(choices=COLOR_CHOICES),
             "COLORSCALE_DIVERGING": forms.Select(choices=COLOR_CHOICES),
        }

