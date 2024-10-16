# Generated by Django 5.0.7 on 2024-08-30 08:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grants_management', '0088_remove_grantcloseoutdocuments_closeout_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GrantCloseOut',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('initiated_date', models.DateTimeField(auto_now_add=True)),
                ('reason', models.CharField(choices=[('completed', 'Completed'), ('terminated', 'Terminated'), ('suspended', 'Suspended')], max_length=20)),
                ('lessons_learnt', models.TextField(blank=True, null=True)),
                ('best_practices', models.TextField(blank=True, null=True)),
                ('achievements', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('approved_date', models.DateTimeField(blank=True, null=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_closeouts', to=settings.AUTH_USER_MODEL)),
                ('completed_kpis', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='grants_management.progressreport')),
                ('grant_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='close_outs', to='grants_management.grantaccount')),
                ('initiated_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='initiated_closeouts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GrantCloseOutDocuments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.JSONField(default=dict)),
                ('file', models.FileField(upload_to='closeout_documents/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('closeout', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='grants_management.grantcloseout')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='closeout_documents', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GrantCloseOutReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], max_length=20)),
                ('comments', models.TextField(blank=True, null=True)),
                ('closeout', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='grants_management.grantcloseout')),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Modifications',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requested_date', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('reviewed_date', models.DateTimeField(blank=True, null=True)),
                ('comments', models.TextField(blank=True, null=True)),
                ('grant_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modifications', to='grants_management.grantaccount')),
                ('requested_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requested_modifications', to=settings.AUTH_USER_MODEL)),
                ('reviewed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_modifications', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
