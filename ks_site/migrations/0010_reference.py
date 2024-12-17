# Generated by Django 4.2.4 on 2023-11-24 18:48

from django.db import migrations, models
import utility.utils


class Migration(migrations.Migration):

    dependencies = [
        ('ks_site', '0009_avatar_remove_sitesetting_avatar_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('image', models.ImageField(upload_to=utility.utils.upload_site_files_path)),
                ('alt', models.CharField(blank=True, max_length=200, null=True)),
                ('description', models.CharField(blank=True, max_length=400, null=True)),
            ],
        ),
    ]
