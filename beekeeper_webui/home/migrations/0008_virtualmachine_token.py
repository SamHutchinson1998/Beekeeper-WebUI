# Generated by Django 3.0.1 on 2020-02-26 23:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_virtualmachine_cell_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='virtualmachine',
            name='token',
            field=models.CharField(default='2cs8_ro50-fdl4StmneO3g', max_length=22),
        ),
    ]
