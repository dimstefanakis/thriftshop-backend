# Generated by Django 3.2.12 on 2022-04-22 01:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mvp', '0002_auto_20220421_2014'),
    ]

    operations = [
        migrations.CreateModel(
            name='TechStack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('mvp', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tech_stack', to='mvp.mvp')),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('mvp', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='services', to='mvp.mvp')),
            ],
        ),
        migrations.CreateModel(
            name='Platform',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('WEB', 'Web'), ('IOS', 'iOS'), ('AND', 'Android'), ('OTHR', 'Other')], default='OTHR', max_length=4)),
                ('mvp', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='platforms', to='mvp.mvp')),
            ],
        ),
        migrations.CreateModel(
            name='Industry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('mvp', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='industries', to='mvp.mvp')),
            ],
        ),
        migrations.CreateModel(
            name='Hosting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('mvp', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='hosting', to='mvp.mvp')),
            ],
        ),
        migrations.CreateModel(
            name='CloudType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('IAAS', 'Infrastructure as a Service'), ('PAAS', 'Platform as a Service'), ('SAAS', 'Software as a Service'), ('OTHR', 'Other')], default='SAAS', max_length=4)),
                ('mvp', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cloud_types', to='mvp.mvp')),
            ],
        ),
    ]
