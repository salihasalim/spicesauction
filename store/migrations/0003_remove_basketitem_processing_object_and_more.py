# Generated by Django 5.1.6 on 2025-02-26 07:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_rename_owner_basket_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='basketitem',
            name='processing_object',
        ),
        migrations.RemoveField(
            model_name='spice',
            name='processing_objects',
        ),
    ]
