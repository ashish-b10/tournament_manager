# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal
import tmdb.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Competitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=63)),
                ('sex', models.CharField(max_length=1, choices=[('F', 'Female'), ('M', 'Male')])),
                ('skill_level', models.CharField(max_length=2, choices=[('WH', 'White'), ('YL', 'Yellow'), ('OR', 'Orange'), ('GN', 'Green'), ('BL', 'Blue'), ('PL', 'Purple'), ('BR', 'Brown'), ('RD', 'Red'), ('BK', 'Black'), ('1D', '1 Dan'), ('2D', '2 Dan'), ('3D', '3 Dan'), ('4D', '4 Dan'), ('5D', '5 Dan'), ('6D', '6 Dan'), ('7D', '7 Dan'), ('8D', '8 Dan'), ('9D', '9 Dan')])),
                ('age', models.IntegerField()),
                ('weight', tmdb.models.WeightField(decimal_places=1, max_digits=4)),
            ],
        ),
        migrations.CreateModel(
            name='Division',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('min_age', models.IntegerField(default=0)),
                ('max_age', models.IntegerField(default=99)),
                ('min_weight', tmdb.models.WeightField(default=Decimal('0.0'), decimal_places=1, max_digits=4)),
                ('max_weight', tmdb.models.WeightField(default=Decimal('999.9'), decimal_places=1, max_digits=4)),
                ('division_level', models.CharField(max_length=1, choices=[('A', 'A team'), ('B', 'B team'), ('C', 'C team')])),
                ('sex', models.CharField(max_length=1, choices=[('M', "Men's"), ('W', "Women's")])),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=31)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.IntegerField()),
                ('score', models.IntegerField(default=0)),
                ('alternate1', models.ForeignKey(related_name='alternate1', blank=True, to='tmdb.Competitor')),
                ('alternate2', models.ForeignKey(related_name='alternate2', blank=True, to='tmdb.Competitor')),
                ('division', models.ForeignKey(to='tmdb.Division')),
                ('heavyweight', models.ForeignKey(related_name='heavyweight', blank=True, to='tmdb.Competitor')),
                ('lightweight', models.ForeignKey(related_name='lightweight', blank=True, to='tmdb.Competitor')),
                ('middleweight', models.ForeignKey(related_name='middleweight', blank=True, to='tmdb.Competitor')),
                ('organization', models.ForeignKey(to='tmdb.Organization')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='division',
            unique_together=set([('division_level', 'sex', 'min_age', 'max_age', 'min_weight', 'max_weight')]),
        ),
        migrations.AddField(
            model_name='competitor',
            name='organization',
            field=models.ForeignKey(to='tmdb.Organization'),
        ),
        migrations.AlterUniqueTogether(
            name='team',
            unique_together=set([('number', 'division', 'organization')]),
        ),
        migrations.AlterUniqueTogether(
            name='competitor',
            unique_together=set([('name', 'organization')]),
        ),
    ]
