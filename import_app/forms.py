from django import forms
from tracks.models import Track

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = Track
        fields = ("document",)
