# Generated by Django 2.2.13 on 2021-08-17 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('options', '0005_optionset_tomtom_filename'),
    ]

    operations = [
        migrations.AddField(
            model_name='optionset',
            name='PHOTOS_DOWNLOAD_DIR',
            field=models.CharField(blank=True, default='', max_length=1023, null=True, verbose_name='Folder to which download photos, if empty default is media/Camera inside the project directory. If changed, must be added to ADDITIONAL_PHOTO_DIRS in the .env file to be able to import and show downloaded photos'),
        ),
    ]
