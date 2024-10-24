# Generated by Django 5.0.7 on 2024-10-15 05:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_alter_customuser_is_approved'),
    ]

    operations = [
        migrations.AddField(
            model_name='ldapuser',
            name='distinguished_name',
            field=models.CharField(default=True, max_length=255, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ldapuser',
            name='last_sync',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='ldapuser',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ldap_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
