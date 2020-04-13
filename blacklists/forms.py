from django import forms
from .models import *


class BlacklistForm(forms.ModelForm):
    class Meta:
        model = Blacklist
        fields = ["file_name", "comment","interpret_regex"]