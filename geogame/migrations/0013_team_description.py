# Generated by Django 3.1.6 on 2021-02-20 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geogame', '0012_auto_20210220_0445'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
