# Generated by Django 5.0.7 on 2024-08-10 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grants_management', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='grant',
            name='is_open',
            field=models.BooleanField(default=True),
        ),
    ]
