# Generated by Django 3.1.1 on 2020-09-27 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fints_downloader', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='balance',
            options={'ordering': ['bk_id']},
        ),
        migrations.AlterModelOptions(
            name='holding',
            options={'ordering': ['bk_id']},
        ),
        migrations.AlterModelOptions(
            name='logincredentials',
            options={'ordering': ['bk_id']},
        ),
        migrations.AlterModelOptions(
            name='transaction',
            options={'ordering': ['bk_id']},
        ),
        migrations.AlterField(
            model_name='holding',
            name='wkn',
            field=models.TextField(blank=True, help_text='German Wertpapierkennnummer', max_length=6, null=True),
        ),
    ]
