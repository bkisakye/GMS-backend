# Generated by Django 5.0.7 on 2024-10-01 07:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grants_management', '0125_alter_grantapplication_status'),
        ('notifications', '0026_notification_review_recommendation'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='uploads',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='grants_management.grantapplicationreviewdocument'),
        ),
    ]