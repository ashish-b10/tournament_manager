from django.db import models
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
    min_age = models.IntegerField(default=0)
    max_age = models.IntegerField(default=99)
    min_weight = WeightField(default=decimal.Decimal('0.0'))
    max_weight = WeightField(default=decimal.Decimal('999.9'))
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
    lightweight = models.ForeignKey(Competitor, blank=True,
            related_name="lightweight")
    middleweight = models.ForeignKey(Competitor, blank=True,
            related_name="middleweight")
    heavyweight = models.ForeignKey(Competitor, blank=True,
            related_name="heavyweight")
    alternate1 = models.ForeignKey(Competitor, blank=True,
            related_name="alternate1")
    alternate2 = models.ForeignKey(Competitor, blank=True,
            related_name="alternate2")
    score = models.IntegerField(default=0)
    class Meta:
        unique_together = (("number", "division", "organization"),)
