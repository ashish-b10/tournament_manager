from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = [
    url(r'^registration_credentials/*$', views.registration_credentials,
            name='registration_credentials'),
    url(r'^match/(?P<match_num>[0-9]+)/*$', views.match, name='match'),
    url(r'^rings/*$', views.rings, name='rings'),
    url(r'^teams/(?P<division_id>[0-9]+)/*$', views.team_list,
            name='team_list'),
    url(r'^teams/*$', views.team_list,
            name='team_list'),
    url(r'^matches/(?P<division_id>[0-9]+)/*$', views.match_list,
            name='match_list'),
    url(r'^matches/*$', views.match_list, name='match_list'),
    url(r'^seedings/(?P<division_id>[0-9]+)/*$', views.seedings,
            name='seedings'),
    url(r'^new_tournament/*$', views.tournament_create,
            name='tournament_create'),
    url(r'^(?P<tournament_slug>[a-z0-9_-]+)/*/edit/*$',
            views.tournament_edit, name='tournament_edit'),
    url(r'^(?P<tournament_slug>[a-z0-9_-]+)/*/import/*$',
            views.tournament_import, name='tournament_import'),
    url(r'^(?P<tournament_slug>[a-z0-9_-]+)/*/schools/*$',
            views.tournament_schools, name='tournament_schools'),
    url(r'^divisions/*$', views.division_list, name='divisions'),
    url(r'^settings/*$', views.settings, name='settings'),
    url(r'^$', views.index, name='index'),
]

urlpatterns += staticfiles_urlpatterns()
