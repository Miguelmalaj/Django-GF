# Generated by Django 4.1.1 on 2023-08-12 04:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("dashboards", "0002_empresas_sucursal"),
    ]

    operations = [
        migrations.RenameField(
            model_name="empresas", old_name="numero", new_name="empresa",
        ),
    ]
