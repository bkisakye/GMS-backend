# Generated by Django 5.0.7 on 2024-09-11 05:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grants_management', '0110_alter_requests_request_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='extensions',
            name='reason',
            field=models.TextField(blank=True, null=True),
        ),
    ]
