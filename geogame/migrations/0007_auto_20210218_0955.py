# Generated by Django 3.1.6 on 2021-02-18 09:55

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geogame', '0006_auto_20210218_0852'),
    ]

    operations = [
        migrations.AlterField(
            model_name='zone',
            name='color',
            field=colorfield.fields.ColorField(default='#000000', max_length=18),
        ),
    ]