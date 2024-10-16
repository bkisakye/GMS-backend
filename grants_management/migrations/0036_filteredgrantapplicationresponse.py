# Generated by Django 5.0.7 on 2024-08-20 05:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grants_management', '0035_remove_grant_district_grant_district'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FilteredGrantApplicationResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.CharField(blank=True, max_length=500, null=True)),
                ('choices', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='filtered_responses', to='grants_management.grantapplication')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='grants_management.defaultapplicationquestion')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='filtered_responses', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
