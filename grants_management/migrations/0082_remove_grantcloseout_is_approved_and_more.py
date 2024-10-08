# Generated by Django 5.0.7 on 2024-08-28 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grants_management', '0081_remove_grantcloseoutreview_closeout_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grantcloseout',
            name='is_approved',
        ),
        migrations.AddField(
            model_name='grantcloseout',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20),
        ),
    ]
