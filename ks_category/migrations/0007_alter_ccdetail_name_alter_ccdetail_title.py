# Generated by Django 4.2.4 on 2023-08-13 06:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ks_category', '0006_section'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ccdetail',
            name='name',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='ccdetail',
            name='title',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
