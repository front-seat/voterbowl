# Generated by Django 5.0.3 on 2024-05-15 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vb', '0011_complex_contest_additions'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='percent_voted_2020',
            field=models.IntegerField(blank=True, default=0, help_text='If known, the percentage of students who voted in 2020 (like 70).'),
        ),
    ]
