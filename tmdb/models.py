from django.db import models
from django.core.exceptions import ValidationError
import decimal

class WeightField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs['max_digits'] = 4
        kwargs['decimal_places'] = 1
        super(WeightField, self).__init__(*args, **kwargs)

class Organization(models.Model):
    name = models.CharField(max_length=31, unique=True)

    def __str__(self):
        return self.name

class Division(models.Model):
    SKILL_LEVELS = (
        ('A', 'A team'),
        ('B', 'B team'),
        ('C', 'C team'),
    )
    SEXES = (
        ('M', "Men's"),
        ('W', "Women's"),
    )
    min_age = models.IntegerField(null=True)
    max_age = models.IntegerField(null=True)
    min_weight = WeightField(null=True)
    max_weight = WeightField(null=True)
    skill_level = models.CharField(max_length=1, choices = SKILL_LEVELS)
    sex = models.CharField(max_length=1, choices = SEXES)
    class Meta:
        unique_together = (("skill_level", "sex", "min_age", "max_age",
                "min_weight", "max_weight"),)

    def __str__(self):
        return " ".join([self.sex, self.division])

class Competitor(models.Model):
    SEXES = (
        ('F', 'Female'),
        ('M', 'Male'),
    )
    BELT_RANKS = (
        ('WH', 'White'),
        ('YL', 'Yellow'),
        ('OR', 'Orange'),
        ('GN', 'Green'),
        ('BL', 'Blue'),
        ('PL', 'Purple'),
        ('BR', 'Brown'),
        ('RD', 'Red'),
        ('BK', 'Black'),
        ('1D', '1 Dan'),
        ('2D', '2 Dan'),
        ('3D', '3 Dan'),
        ('4D', '4 Dan'),
        ('5D', '5 Dan'),
        ('6D', '6 Dan'),
        ('7D', '7 Dan'),
        ('8D', '8 Dan'),
        ('9D', '9 Dan'),
    )
    """ Cutoff weights for each weight class in pounds inclusive. """
    WEIGHT_CUTOFFS = {
        'F' : {
            'light': (decimal.Decimal('0'), decimal.Decimal('117.0')),
            'middle': (decimal.Decimal('117.1'), decimal.Decimal('137.0')),
            'heavy': (decimal.Decimal('137.1'), decimal.Decimal('999.9')),
        },
        'M' : {
            'light': (decimal.Decimal('0'), decimal.Decimal('145.0')),
            'middle': (decimal.Decimal('145.1'), decimal.Decimal('172.0')),
            'heavy': (decimal.Decimal('172.1'), decimal.Decimal('999.9')),
        },
    }
    name = models.CharField(max_length=63)
    sex = models.CharField(max_length=1, choices=SEXES)
    skill_level = models.CharField(max_length=2, choices=BELT_RANKS)
    age = models.IntegerField()
    organization = models.ForeignKey(Organization)
    weight = WeightField()
    class Meta:
        unique_together = (("name", "organization"),)

    @staticmethod
    def _is_between_cutoffs(weight, sex, weightclass):
        cutoffs = Competitor.WEIGHT_CUTOFFS[sex][weightclass]
        return weight >= cutoffs[0] and weight <= cutoffs[1]

    def is_lightweight(self):
        return self._is_between_cutoffs(self.weight, self.sex, 'light')

    def is_middleweight(self):
        return self._is_between_cutoffs(self.weight, self.sex, 'middle')

    def is_heavyweight(self):
        return self._is_between_cutoffs(self.weight, self.sex, 'heavy')

    def __str__(self):
        return "%s (%s)" % (self.name, self.organization)

class Team(models.Model):
    number = models.IntegerField()
    division = models.ForeignKey(Division)
    organization = models.ForeignKey(Organization)
    lightweight = models.ForeignKey(Competitor, null=True,
            related_name="lightweight")
    middleweight = models.ForeignKey(Competitor, null=True,
            related_name="middleweight")
    heavyweight = models.ForeignKey(Competitor, null=True,
            related_name="heavyweight")
    alternate1 = models.ForeignKey(Competitor, null=True,
            related_name="alternate1")
    alternate2 = models.ForeignKey(Competitor, null=True,
            related_name="alternate2")
    score = models.IntegerField(default=0)
    class Meta:
        unique_together = (("number", "division", "organization"),)

    def _valid_member_organization(self, member):
        if member is None: return True
        return self.organization == member.organization

    def _validate_member_organizations(self):
        if not self._valid_member_organization(self.lightweight):
            raise ValidationError(("Lightweight [%s] is not from same" +
                    " organization as [%s]") %(self.lightweight, self))
        if not self._valid_member_organization(self.middleweight):
            raise ValidationError(("Middleweight [%s] is not from same" +
                    " organization as [%s]") %(self.lightweight, self))
        if not self._valid_member_organization(self.heavyweight):
            raise ValidationError(("Heavyweight [%s] is not from same" +
                    " organization as [%s]") %(self.lightweight, self))
        if not self._valid_member_organization(self.alternate1):
            raise ValidationError(("Alternate1 [%s] is not from same" +
                    " organization as [%s]") %(self.lightweight, self))
        if not self._valid_member_organization(self.alternate2):
            raise ValidationError(("Alternate2 [%s] is not from same" +
                    " organization as [%s]") %(self.lightweight, self))

    def _validate_lightweight_eligibility(self):
        if self.lightweight is None: return

        if not self.lightweight.is_lightweight():
            raise ValidationError(("Competitor %s has invalid weight for"
                    + " lightweight spot [%d lbs]")
                    %(self.lightweight, self.lightweight.weight))

    def _validate_middleweight_eligibility(self):
        if self.middleweight is None: return

        if self.middleweight.is_heavyweight():
            raise ValidationError(("Competitor %s has invalid weight for"
                    + " middleweight spot [%d lbs]")
                    %(self.middleweight, self.middleweight.weight))

    def _validate_heavyweight_eligibility(self):
        if self.heavyweight is None: return

        if self.heavyweight.is_lightweight():
            raise ValidationError(("Competitor %s has invalid weight for"
                    + " heavyweight spot [%d lbs]")
                    %(self.heavyweight, self.heavyweight.weight))

    def validate_team_members(self):
        self._validate_member_organizations()
        self._validate_lightweight_eligibility()
        self._validate_middleweight_eligibility()
        self._validate_heavyweight_eligibility()

    def save(self, *args, **kwargs):
        self.validate_team_members()
        super().save(*args, **kwargs)
