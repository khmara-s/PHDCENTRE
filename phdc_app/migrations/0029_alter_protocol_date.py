# Generated by Django 5.0 on 2024-06-02 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phdc_app', '0028_email_last_sent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='protocol',
            name='date',
            field=models.DateField(verbose_name='Дата'),
        ),
    ]