# Generated by Django 5.0 on 2024-06-02 09:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phdc_app', '0026_remove_postgraduatestudent_messaging_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='deadline',
            name='student_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='phdc_app.postgraduatestudent'),
        ),
    ]
