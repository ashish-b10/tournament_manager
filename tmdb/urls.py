from django.conf.urls import url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = [
    # tournament create/edit/delete
    url(r'^tournaments/*$', views.tournaments, name='tournaments'),
    url(r'^tournaments/*/add/*$',
            views.tournament_add, name='tournament_add'),
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/change/*$',
            views.tournament_change, name='tournament_change'),
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/delete/*$',
            views.tournament_delete, name='tournament_delete'),

    # competitor create/edit/delete
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/(?P<school_slug>[a-z0-9_-]+)/*'
            + r'/competitors/*/add/*$',
            views.competitor_add, name='competitor_add'),
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/(?P<school_slug>[a-z0-9_-]+)/*'
            + r'/competitors/*/(?P<competitor_id>[0-9]+)/*$',
            views.competitor_change, name='competitor_change'),
    url(r'^(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/(?P<school_slug>[a-z0-9_-]+)/*'
            + r'/delete_competitor/*/(?P<competitor_id>[0-9]+)',
            views.competitor_delete, name='delete_competitor'),

    # team_registration create/edit/delete
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/schools/*'
            + r'/(?P<school_slug>[a-z0-9_-]+)/*'
            + r'/teams/*'
            + r'/add/*',
            views.team_registration_add, name='team_registration_add'),
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/schools/*'
            + r'/(?P<school_slug>[a-z0-9_-]+)/*'
            + r'/teams/*'
            + r'/(?P<division_slug>[a-z0-9_-]+)/*'
            + r'/(?P<team_number>[0-9]+)'
            + r'/edit/*',
            views.team_registration_change, name='team_registration_change'),
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/schools/*'
            + r'/(?P<school_slug>[a-z0-9_-]+)/*'
            + r'/teams/*'
            + r'/(?P<division_slug>[a-z0-9_-]+)/*'
            + r'/(?P<team_number>[0-9]+)'
            + r'/delete/*',
            views.team_registration_delete, name='team_registration_delete'),

    url(r'^create_headtable_user/*$',
            views.create_headtable_user, name='create_headtable_user'),
    url(r'^create_ringtable_user/*$',
            views.create_ringtable_user, name='create_ringtable_user'),
    url(r'^add_match/*/(?P<match_id>[0-9]+)/*/upper/*$',
            views.add_upper_match, name='add_upper_match'),
    url(r'^add_match/*/(?P<match_id>[0-9]+)/*/lower/*$',
            views.add_lower_match, name='add_lower_match'),
    url(r'^registration_credentials/*$', views.registration_credentials,
            name='registration_credentials'),
    url(r'^settings/*/$', views.settings, name='settings'),
    url(r'^auth/*/', include('django.contrib.auth.urls')),
    url(r'^$', views.index, name='index'),

    url(r'^(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/(?P<division_slug>[a-z0-9_-]+)/*'
            + r'/(?P<match_number>[0-9]+)/*'
            + r'/match_sheet/*',
            views.match_sheet, name='match_sheet'),
    url(r'^(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/(?P<division_slug>[a-z0-9_-]+)/*'
            + r'/match_sheets/*',
            views.match_sheet, name='match_sheet'),
    url(r'^(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/(?P<division_slug>)[a-z0-9_-]+/*'
            + r'/seeding/*$',
            views.seeding, name='seeding'),
    url(r'^(?P<tournament_slug>[a-z0-9_-]+)/*/teams/*$',
            views.team_list, name='team_list'),
    url(r'^(?P<tournament_slug>[a-z0-9_-]+)/*'
            + '/teams/*/(?P<division_slug>[a-z0-9_-]+)/*$',
            views.team_list, name='team_list'),
    url(r'^(?P<tournament_slug>[a-z0-9_-]+)/*/matches/*$',
            views.match_list, name='match_list'),
    url(r'^(?P<tournament_slug>[a-z0-9_-]+)/*/matches/*/(?P<division_slug>[a-z0-9_-]+)/*$',
            views.match_list, name='match_list'),
    url(r'^(?P<tournament_slug>[a-z0-9_-]+)/*/team_points/*/(?P<division_slug>[a-z0-9_-]+)/*$',
            views.team_points, name='team_points'),
    url(r'^(?P<tournament_slug>[a-z0-9_-]+)/*/seedings/*/(?P<division_slug>[a-z0-9_-]+)/*$',
            views.seedings, name='seedings'),
    url(r'^(?P<tournament_slug>[a-z0-9_-]+)/*/brackets/*/(?P<division_slug>[a-z0-9_-]+)/*/printable/*$',
            views.bracket_printable, name='bracket_printable'),
    url(r'^(?P<tournament_slug>[a-z0-9_-]+)/*/brackets/*/(?P<division_slug>[a-z0-9_-]+)/*$',
            views.bracket, name='bracket'),
    url(r'^(?P<tournament_slug>[a-z0-9_-]+)/*/import/*$',
            views.tournament_import, name='tournament_import'),
    url(r'^(?P<tournament_slug>[a-z0-9_-]+)/*/schools/*$',
            views.tournament_schools, name='tournament_schools'),
    url(r'^(?P<tournament_slug>[a-z0-9_-]+)/*'
            + '/schools/*/(?P<school_slug>[a-z0-9_-]+)/*$',
            views.tournament_school, name='tournament_school'),
    url(r'^(?P<tournament_slug>[a-z0-9_-]+)/*/tournament_dashboard/*/rings/*$',
            views.rings, name='rings'),
    url(r'^(?P<tournament_slug>[a-z0-9_-]+)/*/$',
            views.tournament_dashboard, name='tournament_dashboard'),
]

urlpatterns += staticfiles_urlpatterns()
