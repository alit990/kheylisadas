# Generated by Django 4.2.4 on 2023-10-02 09:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('ks_subscription', '0015_alter_payment_create_date_alter_payment_payment_date_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ks_course', '0009_alter_course_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='price',
            field=models.IntegerField(default=2000000),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='TransactionCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=False)),
                ('in_process', models.BooleanField(default=False)),
                ('status', models.CharField(max_length=20)),
                ('gift_day', models.IntegerField(default=0)),
                ('info', models.CharField(blank=True, max_length=100, null=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ks_course.course')),
                ('payment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ks_subscription.payment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
