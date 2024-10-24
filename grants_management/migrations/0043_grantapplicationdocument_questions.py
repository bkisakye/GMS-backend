# Generated by Django 5.0.7 on 2024-08-21 08:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grants_management', '0042_alter_grantapplicationreview_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='grantapplicationdocument',
            name='questions',
            field=models.ForeignKey(default=True, on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='grants_management.filteredgrantapplicationresponse'),
            preserve_default=False,
        ),
    ]
