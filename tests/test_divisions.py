from django.test import TestCase
from tmdb.models import Organization, Competitor
from django.db.utils import IntegrityError
from decimal import Decimal
import itertools as it

def DivisionTestCase(TestCase):
    def setUp(self):
        for (skill_level, sex) in it.product(Division.SKILL_LEVELS,
                Division.SEXES):
            Division.objects.create(skill_level=skill_level, sex=sex)

    def test_create_duplicate_division(self):
        div1 = Division.objects.first()
        try:
            Division.objects.create(skill_level=div1.skill_level, sex=div1.sex)
        except IntegrityError:
            pass
        else:
            self.fail("Division with same skill_level and sex should raise "
                    + "IntegrityError")
