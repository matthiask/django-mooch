# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('flock', '0004_project_default_amount'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reward',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('available_times', models.PositiveIntegerField(null=True, help_text='Leave empty if availability is unlimited.', blank=True, verbose_name='available')),
                ('donation_amount', models.DecimalField(max_digits=10, help_text='The donation has to be at least this amount.', decimal_places=2, verbose_name='donation amount')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rewards', to='flock.Project', verbose_name='project')),
            ],
        ),
        migrations.AlterField(
            model_name='donation',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='flock.Project', verbose_name='project'),
        ),
        migrations.AddField(
            model_name='donation',
            name='selected_reward',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='donations', to='flock.Reward', null=True, blank=True, verbose_name='selected reward'),
        ),
    ]
