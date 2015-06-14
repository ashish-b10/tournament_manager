# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tmdb', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='division',
            old_name='division_level',
            new_name='skill_level',
        ),
        migrations.AlterUniqueTogether(
            name='division',
            unique_together=set([('skill_level', 'sex', 'min_age', 'max_age', 'min_weight', 'max_weight')]),
        ),
    ]
