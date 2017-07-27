"""
Competitor Model

Last Updated: 07-25-2017
"""

from django.db import models

import tmdb.models.fields_model as fields_model
import tmdb.models.school_registration_model as school_reg_model


class Competitor(models.Model):
    """ A person who may compete in a tournament. """
    name = models.CharField(max_length=127)
    sex = fields_model.SexField()
    belt_rank = fields_model.BeltRankField()
    weight = fields_model.WeightField(null=True, blank=True)
    registration = models.ForeignKey(school_reg_model.SchoolRegistration)

    def belt_rank_label(self):
        return fields_model.BeltRankField.label(self.belt_rank)

    def sex_label(self):
        return fields_model.SexField.label(self.sex)

    def __str__(self):
        return "%s (%s)" % (self.name, self.registration.school)

    class Meta:
        unique_together = (("name", "registration"),)