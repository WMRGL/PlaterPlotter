# Generated by Django 4.2.9 on 2024-02-15 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('platerplotter', '0006_holdingrackwell_assigned_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='sample',
            name='non_issue_comment',
            field=models.TextField(blank=True, null=True),
        ),
    ]
