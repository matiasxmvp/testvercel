# Generated by Django 4.2.4 on 2023-09-18 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0018_remove_userprofile_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documento',
            name='nombre',
            field=models.CharField(db_index=True, max_length=255),
        ),
    ]