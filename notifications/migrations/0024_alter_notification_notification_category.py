# Generated by Django 5.0.7 on 2024-09-10 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0023_alter_notification_notification_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_category',
            field=models.CharField(choices=[('new_grant', 'New Grant'), ('grant_application', 'Grant Application'), ('grant_review', 'Grant Review'), ('new_subgrantee', 'New Subgrantee'), ('grant_submission', 'Grant Submission'), ('status_report_due', 'Status Report Due'), ('status_report_submitted', 'Status Report Submitted'), ('status_report_reviewed', 'Status Report Reviewed'), ('disbursement_received', 'Disbursement Received'), ('request_review', 'Request Review'), ('financial_report', 'Financial Report'), ('requests', 'Requests')], max_length=30),
        ),
    ]
