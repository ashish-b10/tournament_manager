from django.test import TestCase
from tmdb.models import Organization, Competitor, SexField, BeltRank
from django.db.utils import IntegrityError
from decimal import Decimal

class CompetitorTestCase(TestCase):
    def setUp(self):
        BeltRank.create_tkd_belt_ranks()
        self.org1 = Organization.objects.create(name="org1")
        self.org2 = Organization.objects.create(name="org2")
        self.lightweight1 = Competitor.objects.create(
                name="sample lightweight1", sex=SexField.FEMALE_DB_VAL,
                skill_level=BeltRank.objects.get(belt_rank="WH"), age=20,
                organization=self.org1, weight=Decimal("117.0"))
        self.middleweight1 = Competitor.objects.create(
                name="sample middleweight1", sex=SexField.FEMALE_DB_VAL,
                skill_level=BeltRank.objects.get(belt_rank="WH"), age=20,
                organization=self.org1, weight=Decimal("137.0"))
        self.heavyweight1 = Competitor.objects.create(
                name="sample heavyweight1", sex=SexField.FEMALE_DB_VAL,
                skill_level=BeltRank.objects.get(belt_rank="WH"), age=20,
                organization=self.org1, weight=Decimal("157.0"))

    def test_str(self):
        self.assertEqual("sample lightweight1 (org1)",
                self.lightweight1.__str__())

    def test_get(self):
        light_competitor = Competitor.objects.get(name="sample lightweight1")
        self.assertEqual("sample lightweight1", light_competitor.name)
        self.assertEqual(SexField.FEMALE_DB_VAL, light_competitor.sex)
        self.assertEqual(BeltRank.objects.get(belt_rank="WH"),
                light_competitor.skill_level)
        self.assertEqual(20, light_competitor.age)
        self.assertEqual(self.org1, light_competitor.organization)
        self.assertEqual(Decimal("117.0"), light_competitor.weight)

    def test_is_lightweight(self):
        self.assertTrue(self.lightweight1.is_lightweight())
        self.assertFalse(self.middleweight1.is_lightweight())
        self.assertFalse(self.heavyweight1.is_lightweight())

    def test_is_middleweight(self):
        self.assertFalse(self.lightweight1.is_middleweight())
        self.assertTrue(self.middleweight1.is_middleweight())
        self.assertFalse(self.heavyweight1.is_middleweight())

    def test_is_heavyweight(self):
        self.assertFalse(self.lightweight1.is_heavyweight())
        self.assertFalse(self.middleweight1.is_heavyweight())
        self.assertTrue(self.heavyweight1.is_heavyweight())

    def test_different_name_same_org(self):
        try:
            lightweight2_org1 = Competitor.objects.create(
                    name="sample lightweight2", sex=SexField.FEMALE_DB_VAL,
                    skill_level=BeltRank.objects.get(belt_rank="WH"),
                    age=20, organization=self.org1, weight=Decimal("117.0"))
        except IntegrityError:
            self.fail("Competitors with different name and same organization "
                    + "should not raise IntegrityError")

    def test_same_name_different_org(self):
        try:
            lightweight1_org2 = Competitor.objects.create(name="sample lightweight1",
                    sex=SexField.FEMALE_DB_VAL,
                    skill_level=BeltRank.objects.get(belt_rank="WH"), age=20,
                    organization=self.org2, weight=Decimal("117.0"))
        except IntegrityError:
            self.fail("Competitors with same name and different organization "
                    + "should not raise IntegrityError")

    def test_same_name_same_org(self):
        try:
            lightweight1_org1 = Competitor.objects.create(name="sample lightweight1",
                    sex=SexField.FEMALE_DB_VAL,
                    skill_level=BeltRank.objects.get(belt_rank="WH"), age=20,
                    organization=self.org1, weight=Decimal("117.0"))
        except IntegrityError:
            pass
        else:
            self.fail("Competitors with same name and organization should "
                    + "raise IntegrityError")
