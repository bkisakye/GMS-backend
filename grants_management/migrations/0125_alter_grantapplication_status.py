# Generated by Django 5.0.7 on 2024-09-26 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grants_management', '0124_grantapplication_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grantapplication',
            name='status',
            field=models.CharField(choices=[('under_review', 'Under Review'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('negotiate', 'Negotiate')], default='under_review', max_length=100),
        ),
    ]
