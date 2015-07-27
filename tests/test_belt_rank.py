from django.test import TestCase
from tmdb.models import BeltRank, Competitor, Sex
from django.core.exceptions import ValidationError

class BeltRankTestCase(TestCase):
    def test_create_tkd_belt_ranks(self):
        BeltRank.create_tkd_belt_ranks()
        if len(BeltRank.objects.all()) != len(BeltRank.BELT_RANKS):
            fail("There should be %d BeltRank instances"
                    %(BeltRank.BELT_RANKS.size()))
        for belt_rank_label in BeltRank.BELT_RANKS:
            belt_rank = BeltRank.objects.get(belt_rank=belt_rank_label[0])
            if belt_rank is None:
                fail("Invalid BeltRank found: %s" %(str(belt_rank)))

    def test_create_invalid_belt_rank(self):
        belt_rank_label = "AA"
        try:
            BeltRank.objects.create(belt_rank=belt_rank_label)
        except ValidationError:
            pass
        else:
            self.fail("Expected ValidationError creating invalid BeltRank: "
                    + belt_rank_label)
