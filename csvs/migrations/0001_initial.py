# Generated by Django 3.1.5 on 2021-01-10 17:46

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Csv',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.FileField(upload_to='csvs', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['csv'])])),
                ('uploaded', models.DateTimeField(auto_now=True)),
                ('activated', models.BooleanField(default=False)),
            ],
        ),
    ]
