# Generated by Django 2.2.13 on 2020-06-22 23:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geojson_obj', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='geojsonobject',
            name='feature_for_name',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='Property name under properties to be shown on popup (only for FeatureCollection)'),
        ),
    ]
