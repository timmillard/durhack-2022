# Generated by Django 4.1.4 on 2022-12-19 22:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pulsifi', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='status',
            field=models.CharField(choices=[('PR', 'In Progress'), ('RE', 'Rejected'), ('CN', 'Confirmed')], max_length=2, verbose_name='Status'),
        ),
    ]