from django.test import TestCase
from tmdb.models import Organization, Competitor
from django.db.utils import IntegrityError
from decimal import Decimal

class CompetitorTestCase(TestCase):
    def setUp(self):
        self.org1 = Organization.objects.create(name="org1")
        self.org2 = Organization.objects.create(name="org2")
        self.competitor1 = Competitor.objects.create(name="competitor 1",
                sex="F", skill_level="WH", age=6, organization=self.org1,
                weight=Decimal(50.3))

    def test_str(self):
        self.assertEqual("competitor 1 (org1)", self.competitor1.__str__())

    def test_get(self):
        self.assertEqual("competitor 1",
                Competitor.objects.get(name="competitor 1").name)
        self.assertEqual("F",
                Competitor.objects.get(name="competitor 1").sex)
        self.assertEqual("WH",
                Competitor.objects.get(name="competitor 1").skill_level)
        self.assertEqual(6,
                Competitor.objects.get(name="competitor 1").age)
        self.assertEqual(self.org1,
                Competitor.objects.get(name="competitor 1").organization)
        self.assertEqual(Decimal("50.3"),
                Competitor.objects.get(name="competitor 1").weight)

    def test_different_name_same_org(self):
        try:
            competitor2_org1 = Competitor.objects.create(name="competitor 2",
                    sex="F", skill_level="WH", age=6, organization=self.org1,
                    weight=Decimal(50.3))
        except IntegrityError:
            self.fail("Competitors with different name and same organization "
                    + "should not raise IntegrityError")

    def test_same_name_different_org(self):
        try:
            competitor1_org2 = Competitor.objects.create(name="competitor 1",
                    sex="F", skill_level="WH", age=6, organization=self.org2,
                    weight=Decimal(50.3))
        except IntegrityError:
            self.fail("Competitors with same name and different organization "
                    + "should not raise IntegrityError")

    def test_same_name_same_org(self):
        try:
            competitor1_org1 = Competitor.objects.create(name="competitor 1",
                    sex="F", skill_level="WH", age=6, organization=self.org1,
                    weight=Decimal(50.3))
        except IntegrityError:
            pass
        else:
            self.fail("Competitors with same name and same organization "
                    + "should raise IntegrityError")

    # these seem to not be the intended behavior...
    #def test_invalid_sex(self):
    #    try:
    #        Competitor.objects.create(name="competitor 2", sex="F",
    #                skill_level="WH", age=6, organization=self.org1,
    #                weight=Decimal("50.3"))
    #    except IntegrityError:
    #        pass
    #    else:
    #        self.fail("Setting an invalid sex did not raise "
    #                + "IntegrityException.")
    #
    #def test_invalid_skill_level(self):
    #    try:
    #        Competitor.objects.create(name="competitor 2", sex="F",
    #                skill_level="WJ", age=6, organization=self.org1,
    #                weight=Decimal(50.3))
    #    except IntegrityError:
    #        pass
    #    except:
    #        import pdb ; pdb.set_trace()
    #    else:
    #        self.fail("Setting an invalid skill level did not raise "
    #                + "IntegrityException.")
