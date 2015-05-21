# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('id', models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, serialize=False)),
                ('created_at', models.DateTimeField(verbose_name='created at', default=django.utils.timezone.now)),
                ('charged_at', models.DateTimeField(verbose_name='charged at', null=True, blank=True)),
                ('amount', models.DecimalField(verbose_name='amount', decimal_places=2, max_digits=10)),
                ('full_name', models.CharField(verbose_name='full name', max_length=200)),
                ('email', models.EmailField(verbose_name='email', max_length=254)),
                ('postal_address', models.TextField(verbose_name='postal address', blank=True)),
            ],
            options={
                'verbose_name': 'donation',
                'verbose_name_plural': 'donations',
            },
        ),
    ]
