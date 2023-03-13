# Generated by Django 4.1.5 on 2023-01-12 14:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import pulsifi.models.utils


class Migration(migrations.Migration):

    dependencies = [
        ('pulsifi', '0005_alter_pulse_creator_alter_pulse_disliked_by_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='assigned_staff',
        ),
        migrations.AddField(
            model_name='report',
            name='assigned_staff_member',
            field=models.ForeignKey(default=pulsifi.models.utils.get_random_moderator_id, limit_choices_to={'groups__name': 'Moderators'}, on_delete=django.db.models.deletion.CASCADE, related_name='staff_assigned_report_set', to=settings.AUTH_USER_MODEL, verbose_name='Assigned Staff Member'),
        ),
        migrations.AlterField(
            model_name='report',
            name='reporter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submitted_report_set', to=settings.AUTH_USER_MODEL, verbose_name='Reporter'),
        ),
    ]
