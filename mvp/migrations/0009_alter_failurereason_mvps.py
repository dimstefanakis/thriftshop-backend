# Generated by Django 3.2.12 on 2022-04-28 01:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mvp', '0008_auto_20220428_0136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='failurereason',
            name='mvps',
            field=models.ManyToManyField(related_name='failure_reasons', to='mvp.Mvp'),
        ),
    ]
