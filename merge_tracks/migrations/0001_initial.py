# Generated by Django 2.2.12 on 2020-04-26 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MergedTrack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512, unique=True, verbose_name='Name')),
                ('delete_original_tracks', models.BooleanField(default=False, verbose_name='Hide input tracks')),
                ('gpx_files', models.TextField(blank=True, null=True, verbose_name='File gpx')),
                ('kml_files', models.TextField(blank=True, null=True, verbose_name='File kml')),
                ('kmz_files', models.TextField(blank=True, null=True, verbose_name='File kmz')),
                ('csv_files', models.TextField(blank=True, null=True, verbose_name='File csv')),
                ('tcx_files', models.TextField(blank=True, null=True, verbose_name='File tcx')),
                ('modified', models.DateTimeField(auto_now=True, null=True, verbose_name='Date of modification')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date of creation')),
                ('input_tracks_names', models.TextField(blank=True, null=True)),
                ('order', models.TextField(blank=True, default='{}', null=True, verbose_name='Priority {track_pk1:order1,track_pk2:order2}')),
            ],
        ),
    ]
