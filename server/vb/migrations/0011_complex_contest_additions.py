# Generated by Django 5.0.3 on 2024-05-15 05:10

from django.db import migrations, models


def data_migrate_kind(apps, schema_editor):
    Contest = apps.get_model('vb', 'Contest')
    # We had to pick a default kind for each contest; we fix historical data here.
    for contest in Contest.objects.all():
        if contest.kind == "giveaway" and contest.in_n > 1:
            contest.kind = 'dice_roll'
            contest.save()


class Migration(migrations.Migration):

    dependencies = [
        ('vb', '0010_remove_ambiguous_email_sent_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='contest',
            name='kind',
            field=models.CharField(choices=[('giveaway', 'Giveaway'), ('dice_roll', 'Dice roll'), ('single_winner', 'Single winner'), ('no_prize', 'No prize')], default='giveaway', max_length=32),
        ),
        migrations.AddField(
            model_name='contest',
            name='prize',
            field=models.CharField(blank=True, default='gift card', help_text='A short description of the prize, if any.', max_length=255),
        ),
        migrations.AddField(
            model_name='contest',
            name='prize_long',
            field=models.CharField(blank=True, default='Amazon gift card', help_text='A long description of the prize, if any.', max_length=255),
        ),
        migrations.AddField(
            model_name='contest',
            name='workflow',
            field=models.CharField(choices=[('amazon', 'Amazon'), ('none', 'None')], default='amazon', max_length=32),
        ),
        migrations.AlterField(
            model_name='contest',
            name='amount',
            field=models.IntegerField(default=0, help_text='The amount of the prize.'),
        ),
        migrations.AlterField(
            model_name='contest',
            name='in_n',
            field=models.IntegerField(default=1, help_text='1 in_n students will win a prize.'),
        ),
        migrations.RunPython(data_migrate_kind),
    ]