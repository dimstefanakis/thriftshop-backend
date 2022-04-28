# Generated by Django 3.2.12 on 2022-04-28 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mvp', '0007_auto_20220428_0131'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cloudtype',
            name='mvp',
        ),
        migrations.RemoveField(
            model_name='failurereason',
            name='mvp',
        ),
        migrations.RemoveField(
            model_name='hosting',
            name='mvp',
        ),
        migrations.RemoveField(
            model_name='industry',
            name='mvp',
        ),
        migrations.RemoveField(
            model_name='platform',
            name='mvp',
        ),
        migrations.RemoveField(
            model_name='service',
            name='mvp',
        ),
        migrations.RemoveField(
            model_name='techstack',
            name='mvp',
        ),
        migrations.AddField(
            model_name='cloudtype',
            name='mvps',
            field=models.ManyToManyField(related_name='cloud_types', to='mvp.Mvp'),
        ),
        migrations.AddField(
            model_name='failurereason',
            name='mvps',
            field=models.ManyToManyField(related_name='failure_reason', to='mvp.Mvp'),
        ),
        migrations.AddField(
            model_name='hosting',
            name='mvps',
            field=models.ManyToManyField(related_name='hosting', to='mvp.Mvp'),
        ),
        migrations.AddField(
            model_name='industry',
            name='mvps',
            field=models.ManyToManyField(related_name='industries', to='mvp.Mvp'),
        ),
        migrations.AddField(
            model_name='platform',
            name='mvps',
            field=models.ManyToManyField(related_name='platforms', to='mvp.Mvp'),
        ),
        migrations.AddField(
            model_name='service',
            name='mvps',
            field=models.ManyToManyField(related_name='services', to='mvp.Mvp'),
        ),
        migrations.AddField(
            model_name='techstack',
            name='mvps',
            field=models.ManyToManyField(related_name='tech_stack', to='mvp.Mvp'),
        ),
    ]
