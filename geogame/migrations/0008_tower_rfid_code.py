# Generated by Django 3.1.6 on 2021-02-19 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geogame', '0007_auto_20210218_0955'),
    ]

    operations = [
        migrations.AddField(
            model_name='tower',
            name='rfid_code',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
    ]
