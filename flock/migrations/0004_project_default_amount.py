# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flock', '0003_auto_20150513_1016'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='default_amount',
            field=models.DecimalField(verbose_name='default amount', decimal_places=2, max_digits=10, blank=True, null=True),
        ),
    ]
