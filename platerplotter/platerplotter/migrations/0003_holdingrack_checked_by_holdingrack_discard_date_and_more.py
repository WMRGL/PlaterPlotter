# Generated by Django 4.2.9 on 2024-02-07 11:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('platerplotter', '0002_holdingrack_discarded'),
    ]

    operations = [
        migrations.AddField(
            model_name='holdingrack',
            name='checked_by',
            field=models.CharField(blank=True, null=True, max_length=120),
        ),
        migrations.AddField(
            model_name='holdingrack',
            name='discard_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='holdingrack',
            name='discarded_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]