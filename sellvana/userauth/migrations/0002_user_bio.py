# Generated by Django 5.1.3 on 2024-11-25 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='bio',
            field=models.CharField(default=1, max_length=200),
            preserve_default=False,
        ),
    ]
