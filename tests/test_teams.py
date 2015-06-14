from django.test import TestCase
from tmdb.models import Organization, Competitor
from django.db.utils import IntegrityError
from decimal import Decimal

class TeamTestCase(TestCase):
    def setUp(self):
        self.org1 = Organization.objects.create(name="org1")
        self.lightweight1 = Competitor.objects.create(
                name="sample lightweight1", sex="F", skill_level="WH", age=20,
                organization=self.org1, weight=Decimal("117.0"))
        self.middleweight1 = Competitor.objects.create(
                name="sample middleweight1", sex="F", skill_level="WH", age=20,
                organization=self.org1, weight=Decimal("137.0"))
        self.heavyweight1 = Competitor.objects.create(
                name="sample heavyweight1", sex="F", skill_level="WH", age=20,
                organization=self.org1, weight=Decimal("157.0"))


