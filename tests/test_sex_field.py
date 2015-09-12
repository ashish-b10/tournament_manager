from django.test import TestCase
from tmdb.models import SexField
from django.core.exceptions import ValidationError

class SexTestCase(TestCase):

    def test_female_sex_valid(self):
        sf = SexField()
        sf.to_python("F")

    def test_male_sex_valid(self):
        sf = SexField()
        sf.to_python("M")

    def test_create_invalid_sex(self):
        invalid_sex_label = "A"
        sf = SexField()
        try:
            sf.to_python(invalid_sex_label)
        except ValidationError:
            pass
        else:
            self.fail("Expected ValidationError creating invalid Sex: "
                    + invalid_sex_label)
