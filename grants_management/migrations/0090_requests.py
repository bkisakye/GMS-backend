# Generated by Django 5.0.7 on 2024-08-30 08:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grants_management', '0089_grantcloseout_grantcloseoutdocuments_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Requests',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request', models.CharField(choices=[('grant_account', 'Grant Account'), ('budget_total', 'Budget Total'), ('budget_total_modification', 'Budget Total Modification'), ('disbursement', 'Disbursement'), ('closeout', 'Closeout'), ('modification', 'Modification'), ('document', 'Document'), ('review', 'Review')], max_length=50)),
                ('grant_closeout', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='grants_management.grantcloseout')),
            ],
        ),
    ]
