# Generated by Django 5.0.7 on 2024-08-21 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grants_management', '0050_remove_grantapplicationdocument_document'),
    ]

    operations = [
        migrations.AddField(
            model_name='grantapplication',
            name='signed',
            field=models.BooleanField(default=False),
        ),
    ]
