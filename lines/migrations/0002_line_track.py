# Generated by Django 2.2.12 on 2020-04-26 14:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('lines', '0001_initial'),
        ('tracks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='line',
            name='track',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tracks.Track'),
        ),
    ]
