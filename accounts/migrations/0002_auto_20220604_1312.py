# Generated by Django 3.2.12 on 2022-06-04 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='github_url',
            field=models.URLField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='website_url',
            field=models.URLField(blank=True, default='', null=True),
        ),
    ]