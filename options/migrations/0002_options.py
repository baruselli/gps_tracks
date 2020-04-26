from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('options', '0001_initial'),
    ]

    def create_object(apps, schema_editor):

        OptionSet = apps.get_model("options", "OptionSet")
        OptionSet.objects.get_or_create(is_active=True)


    operations = [
        migrations.RunPython(create_object),
    ]

