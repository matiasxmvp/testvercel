# Generated by Django 4.2.4 on 2023-09-05 22:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0002_alter_newuser_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='newuser',
            name='sede',
        ),
    ]
