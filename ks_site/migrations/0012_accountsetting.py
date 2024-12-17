# Generated by Django 4.2.4 on 2023-12-15 11:34

from django.db import migrations, models
import utility.utils


class Migration(migrations.Migration):

    dependencies = [
        ('ks_site', '0011_reference_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('mobile_activation_text', models.TextField()),
                ('register_username_text', models.TextField()),
                ('logo_ks', models.ImageField(upload_to=utility.utils.upload_site_files_path)),
                ('icon_ks', models.ImageField(upload_to=utility.utils.upload_site_files_path)),
                ('is_main_setting', models.BooleanField()),
            ],
        ),
    ]
