# Generated by Django 5.0.7 on 2024-09-26 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grants_management', '0123_alter_grantapplication_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='grantapplication',
            name='updated',
            field=models.BooleanField(default=False),
        ),
    ]
