# Generated by Django 5.0 on 2024-06-02 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phdc_app', '0027_deadline_student_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='email',
            name='last_sent',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]