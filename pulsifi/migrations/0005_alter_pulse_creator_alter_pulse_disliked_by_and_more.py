# Generated by Django 4.1.5 on 2023-01-10 16:55

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import pulsifi.validators


class Migration(migrations.Migration):

    dependencies = [
        ('pulsifi', '0004_alter_report_assigned_staff'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pulse',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_%(class)s_set', to=settings.AUTH_USER_MODEL, verbose_name='Creator'),
        ),
        migrations.AlterField(
            model_name='pulse',
            name='disliked_by',
            field=models.ManyToManyField(blank=True, related_name='disliked_%(class)s_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='pulse',
            name='liked_by',
            field=models.ManyToManyField(blank=True, related_name='liked_%(class)s_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='pulse',
            name='visible',
            field=models.BooleanField(default=True, verbose_name='Visible'),
        ),
        migrations.AlterField(
            model_name='reply',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_%(class)s_set', to=settings.AUTH_USER_MODEL, verbose_name='Creator'),
        ),
        migrations.AlterField(
            model_name='reply',
            name='disliked_by',
            field=models.ManyToManyField(blank=True, related_name='disliked_%(class)s_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='reply',
            name='liked_by',
            field=models.ManyToManyField(blank=True, related_name='liked_%(class)s_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='reply',
            name='visible',
            field=models.BooleanField(default=True, verbose_name='Visible'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'unique': 'A user with that username already exists.'}, max_length=30, unique=True, validators=[django.core.validators.RegexValidator('^[\\w.-]+\\Z', 'Enter a valid username. This value may contain only letters, digits and ./_ characters.'), pulsifi.validators.ReservedNameValidator, pulsifi.validators.ConfusableStringValidator], verbose_name='username'),
        ),
    ]
