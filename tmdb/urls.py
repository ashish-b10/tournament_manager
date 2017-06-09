from django.conf.urls import url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = [
    # tournament create/edit/delete
    url(r'^tournaments/*$', views.tournaments, name='tournaments'),
    url(r'^tournaments/*'
            + r'/add/*$',
            views.tournament_add, name='tournament_add'),
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/edit/*$',
            views.tournament_change, name='tournament_change'),
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/delete/*$',
            views.tournament_delete, name='tournament_delete'),

    # competitor create/edit/delete
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/schools/*'
            + r'/(?P<school_slug>[a-z0-9_-]+)/*'
            + r'/competitors/*'
            + r'/add/*$',
            views.competitor_add, name='competitor_add'),
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/schools/*'
            + r'/(?P<school_slug>[a-z0-9_-]+)/*'
            + r'/competitor/*'
            + r'/(?P<competitor_id>[0-9]+)/*'
            + r'/edit/*$',
            views.competitor_change, name='competitor_change'),
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/schools/*'
            + r'/(?P<school_slug>[a-z0-9_-]+)/*'
            + r'/competitor/*'
            + r'/(?P<competitor_id>[0-9]+)/*'
            + r'/delete/*$',
            views.competitor_delete, name='delete_competitor'),

    # team_registration create/edit/delete
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/schools/*'
            + r'/(?P<school_slug>[a-z0-9_-]+)/*'
            + r'/teams/*'
            + r'/add/*$',
            views.team_registration_add, name='team_registration_add'),
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/schools/*'
            + r'/(?P<school_slug>[a-z0-9_-]+)/*'
            + r'/team/*'
            + r'/(?P<division_slug>[a-z0-9_-]+)/*'
            + r'/(?P<team_number>[0-9]+)'
            + r'/edit/*$',
            views.team_registration_change, name='team_registration_change'),
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/schools/*'
            + r'/(?P<school_slug>[a-z0-9_-]+)/*'
            + r'/team/*'
            + r'/(?P<division_slug>[a-z0-9_-]+)/*'
            + r'/(?P<team_number>[0-9]+)'
            + r'/delete/*$',
            views.team_registration_delete, name='team_registration_delete'),

    # tournament import
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/import_schools/*$',
            views.tournament_import, name='tournament_import'),

    # tournament schools
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/schools/*$',
            views.tournament_schools, name='tournament_schools'),
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/schools/*'
            + r'/(?P<school_slug>[a-z0-9_-]+)/*'
            + r'/import_competitors/*$',
            views.tournament_school_import, name='tournament_school_import'),
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/import_competitors/*$',
            views.tournament_school_import, name='tournament_school_import'),

    # match creation from seedings
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/divisions/*'
            + r'/(?P<division_slug>[a-z0-9_-]+)/*'
            + r'/seedings/*$',
            views.division_seedings, name='division_seedings'),
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/divisions/*'
            + r'/(?P<division_slug>[a-z0-9_-]+)/*'
            + r'/seeding/*'
            + r'/(?P<team_slug>[a-z0-9_-]+)/*'
            + r'/edit/*$',
            views.division_seeding, name='division_seeding'),
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/divisions/*'
            + r'/(?P<division_slug>[a-z0-9_-]+)/*'
            + r'/create_matches/*$',
            views.create_tournament_division_matches,
            name='create_tournament_division_matches'),

    # add team to bracket
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/divisions/*'
            + r'/(?P<division_slug>[a-z0-9_-]+)/*'
            + r'/bracket/*'
            + r'/add_team/*$',
            views.add_team_to_bracket, name='add_team_to_bracket'),

    # list of team matches
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/matches/*$',
            views.match_list, name='match_list'),
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/divisions/*'
            + r'/(?P<division_slug>[a-z0-9_-]+)/*'
            + r'/matches/*$',
            views.match_list, name='match_list'),
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/divisions/*'
            + r'/(?P<division_slug>[a-z0-9_-]+)/*'
            + r'/matches/*'
            + r'/(?P<match_num>[0-9]+)/*'
            + r'/update_status/*$',
            views.update_teammatch_status, name='update_teammatch_status'),

    url(r'^create_headtable_user/*$',
            views.create_headtable_user, name='create_headtable_user'),
    url(r'^create_ringtable_user/*$',
            views.create_ringtable_user, name='create_ringtable_user'),
    url(r'^registration_credentials/*$', views.registration_credentials,
            name='registration_credentials'),
    url(r'^settings/*/$', views.settings, name='settings'),
    url(r'^auth/*/', include('django.contrib.auth.urls')),
    url(r'^$', views.index, name='index'),

    # match sheets
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/divisions/*'
            + r'/(?P<division_slug>[a-z0-9_-]+)/*'
            + r'/matches/*'
            + r'/(?P<match_number>[0-9]+)/*'
            + r'/match_sheet/*$',
            views.match_sheet, name='match_sheet'),
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/divisions/*'
            + r'/(?P<division_slug>[a-z0-9_-]+)/*'
            + r'/match_sheets/*$',
            views.match_sheet, name='match_sheet'),

    # list of teams
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/teams/*$',
            views.team_list, name='team_list'),
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/divisions/*'
            + r'/(?P<division_slug>[a-z0-9_-]+)/*'
            + r'/teams/*$',
            views.team_list, name='team_list'),

    # bracket views
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/divisions/*'
            + r'/(?P<division_slug>[a-z0-9_-]+)/*'
            + r'/bracket/*$',
            views.bracket, name='bracket'),
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/divisions/*'
            + r'/(?P<division_slug>[a-z0-9_-]+)/*'
            + r'/bracket/*'
            + r'/printed/*$',
            views.bracket_printable, name='bracket_printable'),

    # tournament school
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/schools/*'
            + r'/(?P<school_slug>[a-z0-9_-]+)/*$',
            views.tournament_school, name='tournament_school'),

    # tournament dashboard
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/dashboard/*$',
            views.tournament_dashboard, name='tournament_dashboard'),
    url(r'^tournaments/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*'
            + r'/dashboard/*'
            + r'/rings/*$',
            views.rings, name='rings'),
]

urlpatterns += staticfiles_urlpatterns()
