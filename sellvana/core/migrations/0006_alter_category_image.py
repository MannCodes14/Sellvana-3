# Generated by Django 5.1.3 on 2025-01-11 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_category_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='image',
            field=models.ImageField(blank=True, default='category.jpg', null=True, upload_to='media/category'),
        ),
    ]
