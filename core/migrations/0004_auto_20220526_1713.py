# Generated by Django 3.1.5 on 2022-05-26 20:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_desdobramento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='desdobramento',
            name='ativo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.ativo'),
        ),
    ]
