# Generated by Django 4.2.4 on 2023-10-28 20:57

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('ks_course', '0013_alter_coursecomment_create_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='create_date',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
    ]
