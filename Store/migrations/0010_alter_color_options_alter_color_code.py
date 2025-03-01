# Generated by Django 5.0.4 on 2024-08-14 16:23

import Store.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0009_alter_stockitem_color'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='color',
            options={'verbose_name': 'Cor', 'verbose_name_plural': 'Cores'},
        ),
        migrations.AlterField(
            model_name='color',
            name='code',
            field=models.CharField(blank=True, max_length=7, null=True, validators=[Store.models.validate_hex_color], verbose_name='Código'),
        ),
    ]
