# Generated by Django 3.1.1 on 2020-10-17 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fints_downloader', '0006_auto_20201011_1749'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.CharField(help_text='ID containing the hashed business key', max_length=64, primary_key=True, serialize=False)),
                ('bk_id', models.CharField(help_text='Unhashed business key', max_length=1024)),
                ('last_update', models.DateTimeField(auto_now=True, help_text='Last update timestamp')),
                ('name', models.CharField(help_text='Tag name', max_length=1024)),
                ('pattern', models.CharField(help_text='Search pattern for this tag', max_length=1024)),
                ('type', models.CharField(choices=[('ct', 'Category'), ('ot', 'Other')], help_text='Type of tag', max_length=2)),
            ],
            options={
                'ordering': ['bk_id'],
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='transaction',
            name='tags',
            field=models.ManyToManyField(help_text='Tags', to='fints_downloader.Tag'),
        ),
    ]
