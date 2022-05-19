# Generated by Django 3.2.12 on 2022-05-05 01:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membershipplan',
            name='interval',
            field=models.CharField(choices=[('one_month', 'One month'), ('six_months', 'Six months'), ('one_year', 'One year')], default='one_month', max_length=20),
        ),
    ]