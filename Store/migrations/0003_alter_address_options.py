# Generated by Django 5.0.4 on 2024-08-12 21:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0002_rename_orderitems_orderitem'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'verbose_name': 'Address', 'verbose_name_plural': 'Addresses'},
        ),
    ]