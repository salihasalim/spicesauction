# Generated by Django 5.1.5 on 2025-03-06 05:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_rename_stripe_payment_intent_order_stripe_payment_intent_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='stripe_payment_intent_id',
        ),
        migrations.AddField(
            model_name='order',
            name='total_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('COD', 'COD'), ('ONLINE', 'ONLINE')], default='COD', max_length=15),
        ),
    ]
