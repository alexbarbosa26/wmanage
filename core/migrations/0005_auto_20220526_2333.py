# Generated by Django 3.1.5 on 2022-05-27 02:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20220526_1713'),
    ]

    operations = [
        migrations.AlterField(
            model_name='desdobramento',
            name='desdobra_se',
            field=models.IntegerField(verbose_name='Desdobra-se em'),
        ),
    ]
