# Generated by Django 5.0 on 2024-05-23 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phdc_app', '0009_dissertation_is_approved'),
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=50)),
                ('status', models.CharField(max_length=50)),
                ('subject', models.CharField(max_length=50)),
                ('message', models.CharField(max_length=1000)),
            ],
        ),
    ]
