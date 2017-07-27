"""
Division Model

Last Updated: 07-25-2017
"""

# Django imports
from django.db import models
from django.template.defaultfilters import slugify
# Model imports
import tmdb.models.fields_model as fields_model


class Division(models.Model):
    sex = fields_model.SexField()
    skill_level = fields_model.DivisionLevelField()
    slug = models.SlugField(unique=True)
    tournaments = models.ManyToManyField('Tournament', through='TournamentDivision')

    class Meta:
        unique_together = (("sex", "skill_level"),)

    def save(self, *args, **kwargs):
        self.slug = self.slugify()
        super(Division, self).save(*args, **kwargs)

    def slugify(self):
        return slugify(str(self))

    def __str__(self):
        if self.sex == fields_model.SexField.FEMALE: sex_name = "Women's"
        if self.sex == fields_model.SexField.MALE: sex_name = "Men's"
        return sex_name + " " + self.skill_level

    def match_number_start_val(self):
        if self.skill_level == fields_model.DivisionLevelField.A_TEAM_VAL:
            start_val = 100
        elif self.skill_level == fields_model.DivisionLevelField.B_TEAM_VAL:
            start_val = 300
        elif self.skill_level == fields_model.DivisionLevelField.C_TEAM_VAL:
            start_val = 500
        return start_val + (100 if self.sex == fields_model.SexField.FEMALE else 0) + 1