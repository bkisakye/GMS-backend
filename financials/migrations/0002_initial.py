# Generated by Django 5.0.7 on 2024-08-07 18:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('financials', '0001_initial'),
        ('subgrantees', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='financialinformation',
            name='subgrantee_profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subgrantees.subgranteeprofile'),
        ),
    ]
