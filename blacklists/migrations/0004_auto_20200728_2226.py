# Generated by Django 2.2.13 on 2020-07-28 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blacklists', '0003_auto_20200728_2222'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blacklist',
            name='method',
            field=models.CharField(choices=[['Exact', 'Exact'], ['Contains', 'Contains'], ['Regex', 'Regex']], default='Exact Match', max_length=15, verbose_name='Method of comparison'),
        ),
    ]
