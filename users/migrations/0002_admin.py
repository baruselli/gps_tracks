

from django.db import migrations
from django.contrib.auth.hashers import make_password

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    def create_object(apps, schema_editor):
        from django.contrib.auth.models import User
        User.objects.create_superuser('admin',  email="",password = 'admin')
        # this will automatically create a Profile object linked to this user
        Profile = apps.get_model("users", "Profile")
        profile = Profile.objects.get(name="admin")
        profile.is_default=True
        profile.save()

    operations = [
        # migrations.RunPython(create_object),
    ]



