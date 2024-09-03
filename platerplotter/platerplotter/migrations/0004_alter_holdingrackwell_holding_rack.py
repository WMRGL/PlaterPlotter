# Generated by Django 4.2.9 on 2024-02-09 11:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('platerplotter', '0003_holdingrack_checked_by_holdingrack_discard_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='holdingrackwell',
            name='holding_rack',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='wells', to='platerplotter.holdingrack'),
        ),
    ]