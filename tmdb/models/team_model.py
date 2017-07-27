"""
Team Model

Last Updated: 07-25-2017
"""

# Django imports
from django.db import models


class Team(models.Model):
    school = models.ForeignKey('School')
    division = models.ForeignKey('Division')
    number = models.SmallIntegerField()
    slug = models.SlugField(unique=True)
    registrations = models.ManyToManyField('TournamentDivision',
            through="TeamRegistration")

    def save(self, *args, **kwargs):
        self.slug = self.slugify()
        super(Team, self).save(*args, **kwargs)

    def slugify(self):
        return self.school.slug + '-' + self.division.slug + str(self.number)

    class Meta:
        unique_together = (('school', 'division', 'number',),)

    def __str__(self):
        return "%s %s%d" %(str(self.school), str(self.division), self.number,)