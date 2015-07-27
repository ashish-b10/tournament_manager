from django.test import TestCase
from tmdb.models import Competitor, Sex, BeltRank, Organization
from django.core.exceptions import ValidationError

class SexTestCase(TestCase):
    def test_create_sexes(self):
        Sex.create_sexes()
        if len(Sex.objects.all()) != len(Sex.SEXES):
            self.fail("There should be %d Sex instances" %(len(Sex.SEXES)))
        self.assertIsNotNone(Sex.FEMALE_SEX, "Static member Sex.FEMALE is set")
        self.assertIsNotNone(Sex.MALE_SEX, "Static member Sex.MALE is set")
        self.assertEqual(Sex.FEMALE_SEX.sex, "F", "Sex.FEMALE sex is 'F'")
        self.assertEqual(Sex.MALE_SEX.sex, "M", "Sex.MALE sex is 'M'")

    def test_str(self):
        Sex.create_sexes()
        self.assertEqual("Female", str(Sex.FEMALE_SEX))
        self.assertEqual("Male", str(Sex.MALE_SEX))

    def test_create_invalid_sex(self):
        invalid_sex_label = "A"
        try:
            Sex.objects.create(sex=invalid_sex_label)
        except ValidationError:
            pass
        else:
            self.fail("Expected ValidationError creating invalid Sex: "
                    + invalid_sex_label)

    def test_create_competitor(self):
        Sex.create_sexes()
        BeltRank.create_tkd_belt_ranks()
        org = Organization.objects.create(name="org1")
        competitor = Competitor.objects.create(name="sample competitor",
                sex=Sex.FEMALE_SEX,
                skill_level=BeltRank.objects.get(belt_rank="WH"),
                age=20, organization=org, weight=120)
        self.assertTrue(competitor in
                Competitor.objects.filter(sex=Sex.FEMALE_SEX),
                "Newly created Competitor belongs to Sex group")
