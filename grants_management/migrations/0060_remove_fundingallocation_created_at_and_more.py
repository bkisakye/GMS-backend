# Generated by Django 5.0.7 on 2024-08-25 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grants_management', '0059_remove_fundingallocation_source_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fundingallocation',
            name='created_at',
        ),
        migrations.AlterField(
            model_name='fundingallocation',
            name='allocation_date',
            field=models.DateField(auto_now_add=True),
        ),
    ]
