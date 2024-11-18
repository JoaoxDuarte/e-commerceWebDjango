# Generated by Django 5.0.4 on 2024-08-14 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0007_banner_alter_address_options_alter_customer_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=60, null=True, verbose_name='Nome')),
                ('code', models.CharField(blank=True, max_length=7, null=True, verbose_name='Código')),
            ],
        ),
    ]
