# Generated by Django 2.2.13 on 2020-07-08 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracks', '0003_auto_20200707_2250'),
    ]

    operations = [
        migrations.AddField(
            model_name='track',
            name='gpx_author',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
