# Generated by Django 5.1 on 2024-10-24 21:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0020_category_slug_type_pslug_alter_address_postal_code'),
    ]

    operations = [
        migrations.RenameField(
            model_name='type',
            old_name='pslug',
            new_name='slug',
        ),
    ]
