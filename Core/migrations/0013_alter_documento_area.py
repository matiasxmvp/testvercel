# Generated by Django 4.2.4 on 2023-09-07 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0012_newuser_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documento',
            name='area',
            field=models.CharField(choices=[('Financiamiento', 'Financiamiento'), ('I+D+I', 'I+D+I'), ('CoordinacionDocente', 'CoordinacionDocente'), ('AsuntosEstudiantiles', 'AsuntosEstudiantiles'), ('Dara', 'Dara')], max_length=255),
        ),
    ]
