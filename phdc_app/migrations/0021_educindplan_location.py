# Generated by Django 5.0 on 2024-06-01 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phdc_app', '0020_remove_educindplan_is_approved_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='educindplan',
            name='location',
            field=models.CharField(choices=[('Відділ аспірантури', 'Відділ аспірантури'), ('Аспірант', 'Аспірант'), ('Приймальня', 'Приймальня'), ('31 корпус', '31 корпус')], default='Аспірант', max_length=25),
        ),
    ]
