# Generated by Django 2.2.13 on 2020-09-01 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracks', '0006_auto_20200825_2108'),
    ]

    operations = [
        migrations.AddField(
            model_name='track',
            name='n_segments_gpx',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='track',
            name='n_tracks_gpx',
            field=models.IntegerField(default=0, null=True),
        ),
    ]