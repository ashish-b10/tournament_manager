"""
School Model

Last Updated: 07-25-2017
"""

from django.db import models
from django.template.defaultfilters import slugify
from itertools import product

class School(models.Model):
    name = models.CharField(max_length=127, unique=True)
    tournaments = models.ManyToManyField('Tournament',
            through='SchoolRegistration')
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = self.slugify()
        new_school = not self.id

        super(School, self).save(*args, **kwargs)

        if new_school:
            self.create_teams()

    def create_teams(self):
        sex_labels = SexField.SEX_LABELS
        skill_labels = DivisionLevelField.DIVISION_LEVEL_LABELS
        for sex, skill_level in product(sex_labels, skill_labels):
            division = Division.objects.filter(sex=sex,
                    skill_level=skill_level).first()
            if division is None:
                division = Division(sex=sex, skill_level=skill_level)
                division.clean()
                division.save()
            self.create_division_teams(division)

    def create_division_teams(self, division):
        for team_num in range(1,11):
            team = Team(school=self, division=division, number=team_num)
            team.clean()
            team.save()

    def slugify(self):
        return slugify(self.name)

    def __str__(self):
        return self.name