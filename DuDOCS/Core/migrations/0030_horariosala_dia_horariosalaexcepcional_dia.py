# Generated by Django 4.2.4 on 2023-10-18 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0029_horariosalaexcepcional_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='horariosala',
            name='dia',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='horariosalaexcepcional',
            name='dia',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]