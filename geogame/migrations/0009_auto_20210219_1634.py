# Generated by Django 3.1.6 on 2021-02-19 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geogame', '0008_tower_rfid_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tower',
            name='rfid_code',
            field=models.CharField(blank=True, max_length=16, null=True, unique=True),
        ),
    ]