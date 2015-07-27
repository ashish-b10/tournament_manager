from django.contrib import admin

from .models import Sex, BeltRank, Organization, Division, Competitor, Team
admin.site.register(Sex)
admin.site.register(BeltRank)
admin.site.register(Organization)
admin.site.register(Division)
admin.site.register(Competitor)
admin.site.register(Team)

