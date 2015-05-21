# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flock', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='donation',
            options={'verbose_name': 'donation', 'verbose_name_plural': 'donations', 'ordering': ('-created_at',)},
        ),
        migrations.AddField(
            model_name='donation',
            name='transaction',
            field=models.TextField(verbose_name='transaction', blank=True),
        ),
    ]
