# Generated by Django 5.0.3 on 2024-04-25 18:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vb', '0005_rename_related_fields'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contestentry',
            options={'verbose_name_plural': 'Contest entries'},
        ),
    ]