from django.contrib import admin

import tmdb.models as mdls
admin.site.register(mdls.BeltRank)
admin.site.register(mdls.Organization)
admin.site.register(mdls.Division)
admin.site.register(mdls.Competitor)
admin.site.register(mdls.Team)
admin.site.register(mdls.TeamMatch)
