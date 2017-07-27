"""
Tournament division model

Last Updated: 07-25-2017
"""

# Django imports
from django.db import models
# Model imports
from .fields_model import *

class TournamentDivision(models.Model):
    tournament = models.ForeignKey('Tournament')
    division = models.ForeignKey('Division')

    class Meta:
        unique_together = (('tournament', 'division'),)

    def __str__(self):
        return "%s" %(self.division)

    def __repr__(self):
        return "%s (%s)" %(self.division, self.tournament)

class TournamentDivisionBeltRanks(models.Model):
    belt_rank = BeltRankField()
    tournament_division = models.ForeignKey('TournamentDivision')
