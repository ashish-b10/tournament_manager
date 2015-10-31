# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tmdb.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BeltRank',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('belt_rank', models.CharField(unique=True, choices=[('WH', 'White'), ('YL', 'Yellow'), ('OR', 'Orange'), ('GN', 'Green'), ('BL', 'Blue'), ('PL', 'Purple'), ('BR', 'Brown'), ('RD', 'Red'), ('BK', 'Black'), ('1D', '1 Dan'), ('2D', '2 Dan'), ('3D', '3 Dan'), ('4D', '4 Dan'), ('5D', '5 Dan'), ('6D', '6 Dan'), ('7D', '7 Dan'), ('8D', '8 Dan'), ('9D', '9 Dan')], max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Competitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=63)),
                ('sex', tmdb.models.SexField(max_length=1)),
                ('age', models.IntegerField()),
                ('weight', tmdb.models.WeightField(decimal_places=1, max_digits=4)),
            ],
        ),
        migrations.CreateModel(
            name='Division',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=31)),
                ('min_age', models.IntegerField(blank=True, null=True)),
                ('max_age', models.IntegerField(blank=True, null=True)),
                ('min_weight', tmdb.models.WeightField(blank=True, decimal_places=1, max_digits=4, null=True)),
                ('max_weight', tmdb.models.WeightField(blank=True, decimal_places=1, max_digits=4, null=True)),
                ('sex', tmdb.models.SexField(max_length=1)),
                ('belt_ranks', models.ManyToManyField(to='tmdb.BeltRank')),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=31)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('number', models.IntegerField()),
                ('score', models.IntegerField(default=0)),
                ('alternate1', models.ForeignKey(to='tmdb.Competitor', related_name='alternate1', null=True, blank=True)),
                ('alternate2', models.ForeignKey(to='tmdb.Competitor', related_name='alternate2', null=True, blank=True)),
                ('division', models.ForeignKey(to='tmdb.Division')),
                ('heavyweight', models.ForeignKey(to='tmdb.Competitor', related_name='heavyweight', null=True, blank=True)),
                ('lightweight', models.ForeignKey(to='tmdb.Competitor', related_name='lightweight', null=True, blank=True)),
                ('middleweight', models.ForeignKey(to='tmdb.Competitor', related_name='middleweight', null=True, blank=True)),
                ('organization', models.ForeignKey(to='tmdb.Organization')),
            ],
        ),
        migrations.CreateModel(
            name='TeamMatch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('number', models.PositiveIntegerField(unique=True)),
                ('parent_side', models.IntegerField()),
                ('root_match', models.BooleanField()),
                ('ring_number', models.PositiveIntegerField(blank=True, null=True)),
                ('ring_assignment_time', models.DateTimeField(blank=True, null=True)),
                ('blue_team', models.ForeignKey(to='tmdb.Team', related_name='blue_team', null=True, blank=True)),
                ('division', models.ForeignKey(to='tmdb.Division')),
                ('parent', models.ForeignKey(to='tmdb.TeamMatch', null=True, blank=True)),
                ('red_team', models.ForeignKey(to='tmdb.Team', related_name='red_team', null=True, blank=True)),
                ('winning_team', models.ForeignKey(to='tmdb.Team', related_name='winning_team', null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='competitor',
            name='organization',
            field=models.ForeignKey(to='tmdb.Organization'),
        ),
        migrations.AddField(
            model_name='competitor',
            name='skill_level',
            field=models.ForeignKey(to='tmdb.BeltRank'),
        ),
        migrations.AlterUniqueTogether(
            name='teammatch',
            unique_together=set([('parent', 'parent_side')]),
        ),
        migrations.AlterUniqueTogether(
            name='team',
            unique_together=set([('number', 'division', 'organization')]),
        ),
        migrations.AlterUniqueTogether(
            name='division',
            unique_together=set([('sex', 'min_age', 'max_age', 'min_weight', 'max_weight')]),
        ),
        migrations.AlterUniqueTogether(
            name='competitor',
            unique_together=set([('name', 'organization')]),
        ),
    ]
