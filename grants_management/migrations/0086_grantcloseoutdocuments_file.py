# Generated by Django 5.0.7 on 2024-08-29 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grants_management', '0085_alter_grantcloseoutdocuments_document'),
    ]

    operations = [
        migrations.AddField(
            model_name='grantcloseoutdocuments',
            name='file',
            field=models.FileField(default=True, upload_to='closeout_documents/'),
            preserve_default=False,
        ),
    ]
