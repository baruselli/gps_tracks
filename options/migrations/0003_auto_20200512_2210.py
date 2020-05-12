# Generated by Django 2.2.12 on 2020-05-12 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('options', '0002_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='optionset',
            name='LANGUAGE_GEOPY',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name="<h3>Geopy</h3> Language for location names<a href='https://developer.tomtom.com/search-api/search-api/supported-languages'> (see list)</a>"),
        ),
        migrations.AlterField(
            model_name='optionset',
            name='USE_GEOPY',
            field=models.BooleanField(blank=True, default=True, verbose_name='Use geopy'),
        ),
    ]
