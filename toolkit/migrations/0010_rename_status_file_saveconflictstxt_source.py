# Generated by Django 4.2.1 on 2024-08-04 17:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('toolkit', '0009_rename_destination_saveconfigfiles_source'),
    ]

    operations = [
        migrations.RenameField(
            model_name='saveconflictstxt',
            old_name='status_file',
            new_name='source',
        ),
    ]
