# Generated by Django 5.1.3 on 2025-02-13 11:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_alter_productreview_product'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cartorder',
            old_name='paid_statuus',
            new_name='paid_status',
        ),
    ]
