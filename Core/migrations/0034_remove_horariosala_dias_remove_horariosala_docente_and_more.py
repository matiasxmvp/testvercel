# Generated by Django 4.2.4 on 2023-10-20 00:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0033_alter_horariosala_sala_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='horariosala',
            name='dias',
        ),
        migrations.RemoveField(
            model_name='horariosala',
            name='docente',
        ),
        migrations.RemoveField(
            model_name='horariosala',
            name='semana',
        ),
        migrations.RemoveField(
            model_name='horariosala',
            name='tipo_programacion',
        ),
        migrations.RemoveField(
            model_name='horariosalaexcepcional',
            name='dias',
        ),
        migrations.RemoveField(
            model_name='horariosalaexcepcional',
            name='docente',
        ),
        migrations.RemoveField(
            model_name='horariosalaexcepcional',
            name='semana',
        ),
        migrations.RemoveField(
            model_name='horariosalaexcepcional',
            name='tipo_programacion',
        ),
        migrations.AddField(
            model_name='horariosala',
            name='asignatura',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='horariosalaexcepcional',
            name='asignatura',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
