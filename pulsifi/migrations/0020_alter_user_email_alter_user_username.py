# Generated by Django 4.1.7 on 2023-03-10 15:59

import django.core.validators
from django.db import migrations, models

import pulsifi.validators


class Migration(migrations.Migration):

    dependencies = [
        ('pulsifi', '0019_alter_pulse__date_time_created_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(error_messages={'unique': 'That Email Address is already in use by another user.'}, max_length=254, unique=True, validators=[pulsifi.validators.HTML5EmailValidator(), pulsifi.validators.FreeEmailValidator(), pulsifi.validators.ConfusableEmailValidator(), pulsifi.validators.PreexistingEmailTLDValidator(), pulsifi.validators.ExampleEmailValidator()], verbose_name='Email Address'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'unique': 'A user with that username already exists.'}, max_length=30, unique=True, validators=[django.core.validators.RegexValidator('^[\\w.-]+\\Z', 'Enter a valid username. This value may contain only letters, digits and ./_ characters.'), pulsifi.validators.ReservedNameValidator(), pulsifi.validators.ConfusableStringValidator()], verbose_name='Username'),
        ),
    ]
