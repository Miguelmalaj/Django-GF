# Generated by Django 4.2.3 on 2023-10-11 01:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OpcionMenu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('vista', models.CharField(max_length=100)),
                ('icono', models.CharField(max_length=50)),
                ('orden', models.IntegerField(default=0, help_text='Indica el orden en que se mostrara en el menu')),
            ],
            options={
                'verbose_name': 'Opciones del menu',
                'ordering': ['orden'],
            },
        ),
        migrations.CreateModel(
            name='Permisos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('opcion_default', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='permiso_default_relacionado', to='app_astilleros.opcionmenu')),
                ('opciones_menu', models.ManyToManyField(to='app_astilleros.opcionmenu')),
            ],
            options={
                'verbose_name': 'Permisos x usuario',
            },
        ),
    ]
