# Generated by Django 2.2.12 on 2020-04-26 14:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('merge_tracks', '0001_initial'),
        ('tracks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mergedtrack',
            name='input_tracks',
            field=models.ManyToManyField(related_name='input_tracks', to='tracks.Track'),
        ),
        migrations.AddField(
            model_name='mergedtrack',
            name='output_track',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='output_track', to='tracks.Track'),
        ),
    ]
