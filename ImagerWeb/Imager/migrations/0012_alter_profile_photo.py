# Generated by Django 5.0.6 on 2024-06-28 07:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Imager', '0011_alter_profile_photo_alter_profile_plan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='photo',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='Imager.image', verbose_name='Photo'),
        ),
    ]
