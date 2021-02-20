# Generated by Django 3.1.6 on 2021-02-20 04:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('geogame', '0011_teamtowerchallenge_photo'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='teamtowerchallenge',
            options={'ordering': ['-timestamp_submitted']},
        ),
        migrations.AlterField(
            model_name='teamtowerchallenge',
            name='challenge',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='geogame.challenge'),
        ),
    ]