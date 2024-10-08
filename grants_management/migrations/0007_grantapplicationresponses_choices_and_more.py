# Generated by Django 5.0.7 on 2024-08-12 01:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grants_management', '0006_defaultapplicationquestion_number_of_rows_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='grantapplicationresponses',
            name='choices',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='defaultapplicationquestion',
            name='question_type',
            field=models.CharField(choices=[('text', 'Text'), ('number', 'Number'), ('date', 'Date'), ('checkbox', 'Checkbox'), ('radio', 'Radio'), ('table', 'Table')], max_length=10),
        ),
    ]
