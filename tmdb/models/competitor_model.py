"""
Competitor Model

Last Updated: 07-25-2017
"""

from django.db import models

from .fields_model import *
from .school_registration_model import *


class Competitor(models.Model):
    """ A person who may compete in a tournament. """
    name = models.CharField(max_length=127)
    sex = SexField()
    belt_rank = BeltRankField()
    weight = WeightField(null=True, blank=True)
    registration = models.ForeignKey(SchoolRegistration)

    def belt_rank_label(self):
        return BeltRankField.label(self.belt_rank)

    def sex_label(self):
        return SexField.label(self.sex)

    def __str__(self):
        return "%s (%s)" % (self.name, self.registration.school)

    class Meta:
        unique_together = (("name", "registration"),)