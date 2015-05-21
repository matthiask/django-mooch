# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('flock', '0002_auto_20150512_2313'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(verbose_name='created at', default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(verbose_name='is active', default=True)),
                ('title', models.CharField(verbose_name='title', max_length=200)),
                ('funding_goal', models.DecimalField(verbose_name='funding goal', max_digits=10, decimal_places=2)),
            ],
            options={
                'verbose_name': 'project',
                'verbose_name_plural': 'projects',
                'ordering': ('-created_at',),
            },
        ),
        migrations.AddField(
            model_name='donation',
            name='project',
            field=models.ForeignKey(default=1, to='flock.Project', verbose_name='project'),
            preserve_default=False,
        ),
    ]
