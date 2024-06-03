# Generated by Django 5.0 on 2024-05-22 23:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phdc_app', '0005_remove_seminar_date_end_remove_seminar_date_start_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='deadlinesubmission',
            name='is_approved',
            field=models.CharField(choices=[('Очікується перевірка', 'Очікується перевірка'), ('Затверджено', 'Затверджено'), ('Не затверджено', 'Не затверджено')], default='Очікується перевірка', max_length=25),
        ),
    ]
