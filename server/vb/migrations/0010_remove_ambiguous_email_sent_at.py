# Generated by Django 5.0.3 on 2024-05-09 16:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vb', '0009_add_explicit_roll_field'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contestentry',
            name='email_sent_at',
        ),
    ]
