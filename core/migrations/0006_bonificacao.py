# Generated by Django 3.1.5 on 2022-06-04 01:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0005_auto_20220526_2333'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bonificacao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField()),
                ('a_cada', models.IntegerField()),
                ('recebo_bonus_de', models.IntegerField()),
                ('custo_atribuido', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Custo Atribuído')),
                ('data_instante', models.DateTimeField(auto_now_add=True)),
                ('ativo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.ativo')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]