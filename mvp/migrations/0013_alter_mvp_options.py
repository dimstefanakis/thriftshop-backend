# Generated by Django 3.2.12 on 2022-05-21 00:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mvp', '0012_mvpsuggestion'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mvp',
            options={'ordering': ('-created_at',)},
        ),
    ]
