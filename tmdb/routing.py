from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'ws/tournaments/(?P<tournament_slug>[a-z0-9_-]+)/sparring_team_match_updates/*', consumers.SparringTeamMatchConsumer),
]
