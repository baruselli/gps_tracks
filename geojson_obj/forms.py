from django import forms
from .models import GeoJsonObject

class GeoJsonObjectForm(forms.ModelForm):
    class Meta:
        model = GeoJsonObject
        fields = ["name", "geojson", "website", "is_global","feature_for_name"]


class GeoJsonObjectFormShort(forms.ModelForm):
    class Meta:
        model = GeoJsonObject
        fields = ["name", "website", "is_global","feature_for_name"]