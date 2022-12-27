# Generated by Django 4.1.4 on 2022-12-22 00:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pulsifi', '0004_report_assigned_staff_alter_report_reporter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='status',
            field=models.CharField(choices=[('PR', 'In Progress'), ('RE', 'Rejected'), ('CN', 'Confirmed')], default='PR', max_length=2, verbose_name='Status'),
        ),
    ]