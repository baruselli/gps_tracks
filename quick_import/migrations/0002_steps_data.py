from django.db import migrations
from django.contrib.auth.hashers import make_password

class Migration(migrations.Migration):

    dependencies = [
        ('quick_import', '0001_initial'),
    ]

    def create_objects(apps, schema_editor):
        # 1 steps
        ImportStep = apps.get_model("quick_import", "ImportStep")

        step = ImportStep.objects.create(
            name = "Google Drive Tracks (requires GOOGLE_TRACKS_DIRS)",
            step_code = "google_drive_tracks",
            step_type = "11_download_tracks",
        )
        step.save()

        step = ImportStep.objects.create(
            name = "TomTom Tracks (requires TOMTOM_USER, TOMTOM_PASSWORD)",
            step_code = "download_tomtom",
            step_type = "11_download_tracks",
        )
        step.save()

        step = ImportStep.objects.create(
            name = "Import downloaded tracks",
            step_code = "generate_tracks",
            step_type = "21_import_tracks",
        )
        step.save()

        step = ImportStep.objects.create(
            name = "Photos from Google Drive (requires GOOGLE_PHOTOS_DIRS)",
            step_code = "google_drive_photos",
            step_type = "31_download_photos",
        )
        step.save()

        step = ImportStep.objects.create(
            name = "Photos from Google Photos",
            step_code = "google_photos",
            step_type = "31_download_photos",
        )
        step.save()

        step = ImportStep.objects.create(
            name = "Import downloaded photos",
            step_code = "import_photos",
            step_type = "41_import_photos",
        )
        step.save()

        step = ImportStep.objects.create(
            name = "Associated photos to tracks",
            step_code = "associate_photos_to_tracks",
            step_type = "51_link_track_photos",
        )
        step.save()

        # 2 quick imports
        QuickImport = apps.get_model("quick_import", "QuickImport")

        quick_import = QuickImport.objects.create(
            name = "Quick Import Google",
        )
        quick_import.save()
        quick_import.steps.add(
            ImportStep.objects.get(step_code="google_drive_tracks"),
            ImportStep.objects.get(step_code="generate_tracks"),
            ImportStep.objects.get(step_code="google_drive_photos"),
            ImportStep.objects.get(step_code="google_photos"),
            ImportStep.objects.get(step_code="import_photos"),
            ImportStep.objects.get(step_code="associate_photos_to_tracks"),

        )

        quick_import = QuickImport.objects.create(
            name = "Quick Import TomTom",
        )
        quick_import.save()
        quick_import.steps.add(
            ImportStep.objects.get(step_code="download_tomtom"),
            ImportStep.objects.get(step_code="generate_tracks"),
        )


    operations = [
        migrations.RunPython(create_objects),
    ]



