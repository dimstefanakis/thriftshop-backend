# Generated by Django 3.2.12 on 2022-04-18 02:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_userprofile_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='twitter_avatar',
            field=models.URLField(blank=True, default='', max_length=400),
        ),
    ]
