from django.conf.urls import url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import tmdb.views as views

app_name = 'tmdb'

tournament_base = (r'^tournament/*'
            + r'/(?P<tournament_slug>[a-z0-9_-]+)/*')
tournament_school_base = (tournament_base
            + r'/school/*'
            + r'/(?P<school_slug>[a-z0-9_-]+)/*')
tournament_school_competitor_base = (tournament_school_base
            + r'/competitor/*'
            + r'/(?P<competitor_id>[0-9]+)/*')
tournament_division_base = (tournament_base
            + r'/division/*'
            + r'/(?P<division_slug>[a-z0-9_-]+)/*')
tournament_division_match_base = (tournament_division_base
            + r'/match/*'
            + r'/(?P<match_num>[0-9]+)/*')

season_base = (r'^season/*'
            + r'/(?P<season_slug>[a-z0-9_-]+)/*')

school_base = (r'^school/*'
            + r'/(?P<school_slug>[a-z0-9_-]+)/*')
school_season_base = (school_base
            + r'/season/*'
            + r'/(?P<season_slug>[a-z0-9_-]+)/*')

urlpatterns = [
    # season edit
    url(r'^seasons/*'
            + r'/add/*$',
            views.season_view.season_add, name='season_add'),
    url(season_base
            + r'/edit/*$',
            views.season_view.season_edit, name='season_edit'),
    url(season_base
            + r'/delete/*$',
            views.season_view.season_delete, name='season_delete'),

    # school edit
    url(r'^schools/*$', views.schools_view.schools, name='schools'),
    url(r'^schools/*'
            + r'/add/*$',
            views.schools_view.school_add, name='school_add'),
    url(school_base + '$', views.schools_view.school, name='school'),
    url(school_base
            + r'/edit/*$',
            views.schools_view.school_change, name='school_change'),
    url(school_base
            + r'/delete/*$',
            views.schools_view.school_delete, name='school_delete'),

    # school season registration edit
    url(school_season_base
            + r'/edit/*$',
            views.schools_view.school_season_change,
            name='school_season_change'),

    # tournament create/edit/delete
    url(r'^tournaments/*$', views.tournament_view.tournaments, name='tournaments'),
    url(r'^tournaments/*'
            + r'/add/*$',
            views.tournament_view.tournament_add, name='tournament_add'),
    url(tournament_base
            + r'/edit/*$',
            views.tournament_view.tournament_change, name='tournament_change'),
    url(tournament_base
            + r'/delete/*$',
            views.tournament_view.tournament_delete, name='tournament_delete'),
    url(tournament_base
            + r'/delete_teams/*$',
            views.tournament_view.tournament_delete_teams,
            name='tournament_delete_teams'),
    url(tournament_base
            + r'/json_data/*$',
            views.tournament_view.tournament_json, name='tournament_json'),

    # tournament import
    url(tournament_base
            + r'/import_schools/*$',
            views.tournament_view.tournament_import, name='tournament_import'),

    # tournament dashboard
    url(tournament_base + '$', views.tournament_view.tournament_dashboard,
            name='tournament_dashboard'),

    # tournament schools
    url(tournament_base
            + r'/schools/*$',
            views.tournament_view.tournament_schools, name='tournament_schools'),
    url(tournament_school_base
            + r'/*$',
            views.tournament_view.tournament_school, name='tournament_school'),
    url(tournament_school_base
            + r'/import_competitors/*$',
            views.tournament_view.tournament_school_import,
            name='tournament_school_import'),
    url(tournament_base
            + r'/import_competitors/*$',
            views.tournament_view.tournament_school_import,
            name='tournament_school_import'),

    # list of teams
    url(tournament_base
            + r'/teams/*$',
            views.team_registration_view.team_list, name='team_list'),
    url(tournament_division_base
            + r'/teams/*$',
            views.team_registration_view.team_list, name='team_list'),

    # team_registration create/edit/delete
    url(tournament_school_base
            + r'/teams/*'
            + r'/add/*$',
            views.team_registration_view.team_registration_add, name='team_registration_add'),
    url(tournament_school_base
            + r'/team/*'
            + r'/(?P<division_slug>[a-z0-9_-]+)/*'
            + r'/(?P<team_number>[0-9]+)'
            + r'/edit/*$',
            views.team_registration_view.team_registration_change, name='team_registration_change'),
    url(tournament_school_base
            + r'/team/*'
            + r'/(?P<division_slug>[a-z0-9_-]+)/*'
            + r'/(?P<team_number>[0-9]+)'
            + r'/delete/*$',
            views.team_registration_view.team_registration_delete, name='team_registration_delete'),

    # match creation from seedings
    url(tournament_division_base
            + r'/seedings/*$',
            views.division_view.division_seedings, name='division_seedings'),
    url(tournament_division_base
            + r'/points/*'
            + r'/(?P<team_slug>[a-z0-9_-]+)/*'
            + r'/edit/*$',
            views.division_view.division_points, name='division_points'),
    url(tournament_division_base
            + r'/seeding/*'
            + r'/(?P<team_slug>[a-z0-9_-]+)/*'
            + r'/edit/*$',
            views.division_view.division_seeding, name='division_seeding'),
    url(tournament_division_base
            + r'/create_matches/*$',
            views.division_view.create_tournament_division_matches,
            name='create_tournament_division_matches'),

    # add team to bracket
    url(tournament_division_base
            + r'/bracket/*'
            + r'/add_team/*$',
            views.bracket_view.add_team_to_bracket, name='add_team_to_bracket'),
    url(tournament_division_base
            + r'/bracket/*'
            + r'/remove_team/*$',
            views.bracket_view.remove_team_from_bracket,
            name='remove_team_from_bracket'),

    # list of team matches
    url(tournament_base
            + r'/matches/*$',
            views.team_match_view.matches, name='match_list'),
    url(tournament_division_match_base
            + r'/update_status/*$',
            views.team_match_view.update_teammatch_status, name='update_teammatch_status'),

    # match sheets
    url(tournament_division_base
            + r'/matches/*'
            + r'/(?P<match_number>[0-9]+)/*'
            + r'/match_sheet/*$',
            views.team_match_view.match_sheet, name='match_sheet'),
    url(tournament_division_base
            + r'/match_sheets/*$',
            views.team_match_view.match_sheet, name='match_sheet'),

    # bracket views
    url(tournament_division_base
            + r'/bracket/*$',
            views.bracket_view.bracket, name='bracket'),
    url(tournament_division_base
            + r'/bracket/*'
            + r'/svg/*$',
            views.bracket_view.bracket_printable, name='bracket_printable'),
    url(tournament_division_base
            + r'/bracket/*'
            + r'/pdf/*$',
            views.bracket_view.bracket_printable_pdf,
            name='bracket_printable_pdf'),

    # miscellaneous functionality
    url(r'^create_headtable_user/*$',
            views.settings_view.create_headtable_user, name='create_headtable_user'),
    url(r'^create_ringtable_user/*$',
            views.settings_view.create_ringtable_user, name='create_ringtable_user'),
    url(r'^registration_credentials/*$', views.settings_view.registration_credentials,
            name='registration_credentials'),
    url(r'^settings/*/$', views.settings_view.settings, name='settings'),
    url(r'^auth/*/', include('django.contrib.auth.urls')),
    url(r'^$', views.settings_view.index, name='index'),
]

urlpatterns += staticfiles_urlpatterns()
