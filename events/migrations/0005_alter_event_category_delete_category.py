# Generated by Django 5.1.5 on 2025-04-27 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_remove_event_capacity_remove_event_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='category',
            field=models.CharField(choices=[('club', 'Club'), ('academic', 'Academic'), ('social', 'Social'), ('cultural', 'Cultural'), ('athletic', 'Athletic'), ('workshop', 'Workshop')], default='main', max_length=10),
        ),
        migrations.DeleteModel(
            name='Category',
        ),
    ]
