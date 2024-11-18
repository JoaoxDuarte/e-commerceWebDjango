# Generated by Django 5.1 on 2024-08-15 22:04

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0018_alter_customer_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='phone',
            field=models.CharField(blank=True, max_length=15, null=True, validators=[django.core.validators.RegexValidator(message='Número de telefone inválido. Por favor, use um dos formatos permitidos: +55 (XX) XXXX-XXXX, +55 (XX) XXXXX-XXXX, (XX) XXXX-XXXX, (XX) XXXXX-XXXX, XX XXXX-XXXX, XX XXXXX-XXXX, XX XXXXXXXXXX ou XX XXXXXXXXX', regex='^(?:\\+55\\s)?(?:\\(\\d{2}\\)\\s|\\d{2}\\s)?(?:\\d{4,5}-\\d{4}|\\d{4,5}\\s\\d{4}|\\d{10,11}|\\d{2}\\s\\d{8,9})$')], verbose_name='Telefone'),
        ),
    ]
