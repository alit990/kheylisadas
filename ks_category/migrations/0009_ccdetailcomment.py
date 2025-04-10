# Generated by Django 4.2.4 on 2023-08-24 13:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ks_category', '0008_rename_active_category_is_active_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CCDetailComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('text', models.TextField()),
                ('is_allowed', models.BooleanField(default=False)),
                ('ccdetail', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ks_category.ccdetail')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ks_category.ccdetailcomment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
