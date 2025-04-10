# Generated by Django 4.2.4 on 2023-08-13 06:00

from django.db import migrations, models
import django.db.models.deletion
import utility.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=150, null=True)),
                ('name', models.CharField(blank=True, max_length=150, null=True)),
                ('active', models.BooleanField(default=False)),
                ('icon', models.CharField(default='A', max_length=10)),
                ('thumb', models.ImageField(blank=True, null=True, upload_to=utility.utils.upload_course_image_path)),
                ('image', models.ImageField(blank=True, null=True, upload_to=utility.utils.upload_course_image_path)),
                ('description', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SectionCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('name', models.CharField(max_length=150)),
                ('active', models.BooleanField(default=False)),
                ('description', models.TextField(blank=True, null=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ks_course.course')),
            ],
        ),
    ]
