# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tmdb.models


class Migration(migrations.Migration):

    dependencies = [
        ('tmdb', '0002_auto_20150614_1644'),
    ]

    operations = [
        migrations.AlterField(
            model_name='division',
            name='max_age',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='division',
            name='max_weight',
            field=tmdb.models.WeightField(null=True, decimal_places=1, max_digits=4),
        ),
        migrations.AlterField(
            model_name='division',
            name='min_age',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='division',
            name='min_weight',
            field=tmdb.models.WeightField(null=True, decimal_places=1, max_digits=4),
        ),
        migrations.AlterField(
            model_name='team',
            name='alternate1',
            field=models.ForeignKey(null=True, to='tmdb.Competitor', related_name='alternate1'),
        ),
        migrations.AlterField(
            model_name='team',
            name='alternate2',
            field=models.ForeignKey(null=True, to='tmdb.Competitor', related_name='alternate2'),
        ),
        migrations.AlterField(
            model_name='team',
            name='heavyweight',
            field=models.ForeignKey(null=True, to='tmdb.Competitor', related_name='heavyweight'),
        ),
        migrations.AlterField(
            model_name='team',
            name='lightweight',
            field=models.ForeignKey(null=True, to='tmdb.Competitor', related_name='lightweight'),
        ),
        migrations.AlterField(
            model_name='team',
            name='middleweight',
            field=models.ForeignKey(null=True, to='tmdb.Competitor', related_name='middleweight'),
        ),
    ]
