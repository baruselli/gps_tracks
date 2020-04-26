

from django.db import migrations
from django.contrib.auth.hashers import make_password

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    def create_object(apps, schema_editor):
        #create django admin
        from django.contrib.auth.models import User
        User.objects.create_superuser('admin',  email="",password = 'admin')
        # create profile linked to admin
        Profile = apps.get_model("users", "Profile")
        profile = Profile.objects.create(
            name = "Default User",
            user_id = 1,
            is_default = True,
        )
        profile.save()

    operations = [
        migrations.RunPython(create_object),
    ]



