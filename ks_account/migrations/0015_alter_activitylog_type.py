# Generated by Django 4.2.4 on 2023-11-30 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ks_account', '0014_alter_activitylog_create_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activitylog',
            name='type',
            field=models.IntegerField(choices=[(1, 'ورود موفق'), (2, 'ورود ناموفق - تصویر امنیتی اشتباه'), (3, 'ورود ناموفق - کلمه عبور اشتباه'), (4, 'ارسال پیامک فعالسازی'), (5, 'ارسال پیامک بازیابی رمز عبور'), (6, 'ثبت نام موفق')]),
        ),
    ]
