# Generated by Django 2.2.12 on 2020-04-26 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.IntegerField(blank=True, default=0, null=True)),
                ('number', models.IntegerField(blank=True, null=True, unique=True)),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Name')),
                ('color', models.CharField(blank=True, max_length=255, null=True, verbose_name='Color')),
                ('avg_lat', models.FloatField(null=True)),
                ('avg_long', models.FloatField(null=True)),
                ('min_lat', models.FloatField(null=True)),
                ('min_long', models.FloatField(null=True)),
                ('max_lat', models.FloatField(null=True)),
                ('max_long', models.FloatField(null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date of creation')),
                ('exclude_from_search', models.BooleanField(default=False, verbose_name='Exclude tracks from distance and similarities queries')),
                ('properties_json', models.TextField(blank=True, default='{}', null=True, verbose_name='Json with properties of all tracks')),
                ('auto_update_properties', models.BooleanField(default=False, verbose_name='Auto update properties for scatter plots')),
                ('modified', models.DateTimeField(auto_now=True, null=True, verbose_name='Date of modification')),
                ('min_date', models.DateField(null=True)),
                ('max_date', models.DateField(null=True)),
                ('has_freq', models.BooleanField(default=False)),
                ('has_hr', models.BooleanField(default=False)),
                ('has_times', models.BooleanField(default=True)),
                ('has_alts', models.BooleanField(default=True)),
                ('use_points_instead_of_lines', models.BooleanField(default=False)),
                ('is_path_group', models.BooleanField(default=False)),
                ('hide_in_forms', models.BooleanField(default=False, verbose_name='Hide from track form')),
                ('always_use_lines', models.BooleanField(default=False, verbose_name='Always use lines instead of points in this page')),
            ],
            options={
                'verbose_name': 'Group',
                'ordering': ['pk'],
            },
        ),
    ]
