# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion

def migrate_competitors(apps, schema_editor):
    SparringTeamRegistration = apps.get_model(
            "tmdb", "SparringTeamRegistration")
    for sparring_team_reg in SparringTeamRegistration.objects.all():
        sparring_team_reg.has_lightweight = bool(sparring_team_reg.lightweight)
        sparring_team_reg.has_middleweight = bool(sparring_team_reg.middleweight)
        sparring_team_reg.has_heavyweight = bool(sparring_team_reg.heavyweight)
        sparring_team_reg.has_alternate1 = bool(sparring_team_reg.alternate1)
        sparring_team_reg.has_alternate2 = bool(sparring_team_reg.alternate2)
        sparring_team_reg.save()

class Migration(migrations.Migration):

    dependencies = [
        ('tmdb', '0019_create_weightclass_booleans'),
    ]

    operations = [
        migrations.RunPython(migrate_competitors)
    ]
