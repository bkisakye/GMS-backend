# Generated by Django 5.0.7 on 2024-08-26 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grants_management', '0063_financialreport'),
    ]

    operations = [
        migrations.AddField(
            model_name='grant',
            name='reporting_time',
            field=models.CharField(choices=[('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('biannually', 'Biannually'), ('annually', 'Annually'), ('other', 'Other')], default=True, max_length=20),
            preserve_default=False,
        ),
    ]
