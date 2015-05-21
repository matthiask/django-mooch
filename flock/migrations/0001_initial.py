# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import uuid
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('id', models.UUIDField(serialize=False, primary_key=True, editable=False, default=uuid.uuid4)),
                ('created_at', models.DateTimeField(verbose_name='created at', default=django.utils.timezone.now)),
                ('charged_at', models.DateTimeField(null=True, blank=True, verbose_name='charged at')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='amount')),
                ('full_name', models.CharField(max_length=200, verbose_name='full name')),
                ('email', models.EmailField(max_length=254, verbose_name='email')),
                ('postal_address', models.TextField(blank=True, verbose_name='postal address')),
                ('transaction', models.TextField(blank=True, verbose_name='transaction')),
            ],
            options={
                'verbose_name_plural': 'donations',
                'verbose_name': 'donation',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(verbose_name='created at', default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(verbose_name='is active', default=True)),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('funding_goal', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='funding goal')),
                ('default_amount', models.DecimalField(null=True, max_digits=10, blank=True, decimal_places=2, verbose_name='default amount')),
            ],
            options={
                'verbose_name_plural': 'projects',
                'verbose_name': 'project',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Reward',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('available_times', models.PositiveIntegerField(null=True, help_text='Leave empty if availability is unlimited.', blank=True, verbose_name='available')),
                ('donation_amount', models.DecimalField(decimal_places=2, help_text='The donation has to be at least this amount.', verbose_name='donation amount', max_digits=10)),
                ('project', models.ForeignKey(to='flock.Project', related_name='rewards', verbose_name='project', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'verbose_name_plural': 'rewards',
                'verbose_name': 'reward',
                'ordering': ('donation_amount',),
            },
        ),
        migrations.AddField(
            model_name='donation',
            name='project',
            field=models.ForeignKey(to='flock.Project', verbose_name='project', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='donation',
            name='selected_reward',
            field=models.ForeignKey(to='flock.Reward', blank=True, related_name='donations', null=True, verbose_name='selected reward', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
