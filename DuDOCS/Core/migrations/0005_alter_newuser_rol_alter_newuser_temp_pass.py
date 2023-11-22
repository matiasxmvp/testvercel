# Generated by Django 4.2.4 on 2023-09-06 00:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0004_newuser_sede'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newuser',
            name='rol',
            field=models.CharField(choices=[('Administrador', 'Administrador'), ('Ayudante', 'Ayudante'), ('Docente', 'Docente'), ('CoordinadorDocente', 'Coordinador Docente'), ('PuntoEstudiantil', 'Punto Estudiantil'), ('Dara', 'Dara')], default='administrador', max_length=30),
        ),
        migrations.AlterField(
            model_name='newuser',
            name='temp_pass',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]