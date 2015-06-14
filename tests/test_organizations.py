from django.test import TestCase
from tmdb.models import Organization
from django.db.utils import IntegrityError

class OrganizationTestCase(TestCase):
    def setUp(self):
        self.org1 = Organization.objects.create(name="org1")
        self.org2 = Organization.objects.create(name="org2")
        self.org3 = Organization.objects.create(name="org3")

    def test_get(self):
        self.assertEqual("org1", Organization.objects.get(name="org1").name)
        self.assertEqual("org2", Organization.objects.get(name="org2").name)
        self.assertEqual("org3", Organization.objects.get(name="org3").name)

    def test_create_duplicate_org(self):
        try:
            org1 = Organization.objects.create(name="org1")
        except IntegrityError:
            pass
        else:
            self.fail("Creating a duplicate organization did not raise "
                    + "IntegrityException.")
