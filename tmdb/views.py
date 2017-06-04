from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.forms.models import modelformset_factory
from django.core.urlresolvers import reverse
from django.conf import settings as config
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import models as auth_models
from django.core.exceptions import PermissionDenied

from . import forms
from . import models

from collections import defaultdict
import re
import datetime

from .util.match_sheet import create_match_sheets
from .util.bracket_svg import SvgBracket

def permission_error_string(user, perm_type):
    return "Username `%s` does not have permission to %s." %(
            user.username, perm_type)

def can_import_school_registration(user):
    return user.has_perms([
        "tmdb.add_competitor",
        "tmdb.add_teamregistration",
        "tmdb.change_competitor",
        "tmdb.change_teamregistration",
        "tmdb.delete_competitor",
        "tmdb.delete_teamregistration",
    ])

@login_required
def settings(request):
    return render(request, 'tmdb/settings.html')

def index(request):
    return HttpResponseRedirect(reverse('tmdb:tournaments'))

def tournaments(request, tournament_slug=None):
    today = datetime.date.today()
    context = {
        'tournaments': models.Tournament.objects.order_by('-date')
    }
    return render(request, 'tmdb/tournaments.html', context)

@permission_required("tmdb.add_tournament")
def tournament_add(request):
    template_name = 'tmdb/tournament_add_change.html'
    context = {}
    if request.method == 'POST':
        add_form = forms.TournamentEditForm(request.POST)
        context['add_form'] = add_form
        if add_form.is_valid():
            add_form.save()
            return HttpResponseRedirect(reverse('tmdb:tournament_dashboard',
                    args=(add_form.instance.slug,)))
    else:
        today = datetime.date.today()
        add_form = forms.TournamentEditForm(initial={
                'date': today,
                'import_field': True,
        })
    context['add_form'] = add_form
    return render(request, template_name, context)

@permission_required("tmdb.change_tournament")
def tournament_change(request, tournament_slug):
    instance = get_object_or_404(models.Tournament, slug=tournament_slug)
    template_name = 'tmdb/tournament_add_change.html'
    context = {}
    if request.method == 'POST':
        change_form = forms.TournamentEditForm(request.POST, instance=instance)
        context['change_form'] = change_form
        if change_form.is_valid():
            tournament = change_form.save()
            return HttpResponseRedirect(reverse('tmdb:tournament_dashboard',
                    args=(change_form.instance.slug,)))
    else:
        change_form = forms.TournamentEditForm(instance=instance,
                initial={'import': False})
        import_form = forms.TournamentImportForm(instance=instance)
        context['import_form'] = import_form
    context['change_form'] = change_form
    return render(request, template_name, context)

@permission_required("tmdb.delete_tournament")
def tournament_delete(request, tournament_slug):
    instance = get_object_or_404(models.Tournament, slug=tournament_slug)
    template_name = 'tmdb/tournament_delete.html'
    context = {'tournament': instance}
    if request.method == 'POST':
        delete_form = forms.TournamentDeleteForm(request.POST,
                instance=instance)
        context['delete_form'] = delete_form
        if delete_form.is_valid():
            instance.delete()
            return HttpResponseRedirect(reverse('tmdb:index'))
    else:
        delete_form = forms.TournamentDeleteForm(instance=instance)
    context['delete_form'] = delete_form
    return render(request, 'tmdb/tournament_delete.html', context)

@permission_required("tmdb.change_tournament")
def tournament_import(request, tournament_slug):
    if request.method == "POST":
        instance = get_object_or_404(models.Tournament, slug=tournament_slug)
        instance.import_school_registrations()
    return HttpResponseRedirect(reverse('tmdb:index'))

def tournament_dashboard(request, tournament_slug, division_slug=None):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    tournament_divisions = models.TournamentDivision.objects.filter(
            tournament=tournament)

    if division_slug is not None:
        tournament_divisions = tournament_divisions.filter(
                division__slug=division_slug)

    matches = []
    for division in tournament_divisions:
        team_matches = models.TeamMatch.objects.filter(
                division=division).order_by('number')
        for team_match in team_matches:
            team_match.form = forms.MatchForm(instance=team_match)
            match_teams = []
            if team_match.blue_team is not None:
                match_teams.append(team_match.blue_team.pk)
            if team_match.red_team is not None:
                match_teams.append(team_match.red_team.pk)
            team_match.form.fields['winning_team'].queryset = \
                    models.TeamRegistration.objects.filter(pk__in=match_teams)
        matches.append((division, team_matches))

    # Information about the matches by ring.
    matches_by_ring = defaultdict(list)
    for match in models.TeamMatch.objects.filter(ring_number__isnull=False,
            division__tournament=tournament).order_by('ring_assignment_time'):
        matches_by_ring[str(match.ring_number)].append(match)

    context = {
        'tournament': tournament,
        'tournament_divisions': tournament_divisions,
        'matches_by_ring': sorted(matches_by_ring.items()),
        'team_matches': matches
    }
    return render(request, 'tmdb/tournament_dashboard.html', context)

def tournament_school(request, tournament_slug, school_slug):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    school = get_object_or_404(models.School, slug=school_slug)
    school_registration = get_object_or_404(models.SchoolRegistration,
            tournament=tournament, school=school)
    competitors = models.Competitor.objects.filter(
            registration=school_registration).order_by('name')
    team_registrations = models.TeamRegistration.order_queryset(
            models.TeamRegistration.objects.filter(
                    tournament_division__tournament=tournament,
                    team__school=school))
    context = {
        'tournament': tournament,
        'school_registration': school_registration,
        'competitors': competitors,
        'team_registrations': team_registrations,
    }
    return render(request, 'tmdb/tournament_school_competitors.html', context)

def build_tournament_schools(request, tournament, context=None, status=None):
    if context is None:
        context = {}
    context['tournament'] = tournament
    template_name = 'tmdb/tournament_schools.html'
    school_registrations = models.SchoolRegistration.objects.filter(
        tournament=tournament).order_by('school__name')
    school_pks = []
    all_schools_imported = True
    for school_reg in school_registrations:
        initial = {'school_registrations': school_reg.pk, 'reimport': True}
        school_reg.import_form = forms.SchoolRegistrationImportForm(
                initial=initial)
        school_pks.append(school_reg.pk)
        all_schools_imported = all_schools_imported and school_reg.imported
    context['school_registrations'] = school_registrations
    context['all_schools_imported'] = all_schools_imported
    context['import_all_form'] = forms.SchoolRegistrationImportForm(
            initial={
                'reimport': False,
                'school_registrations': ','.join(map(str, school_pks))
            })
    return render(request, 'tmdb/tournament_schools.html', context)

def tournament_schools(request, tournament_slug):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    context = {}
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' %(
                    reverse('tmdb:login'), request.path,))
        if not can_import_school_registration(request.user):
            context['err_msg'] = permission_error_string(request.user,
                    "import school registration")
            return build_tournament_schools(request, tournament, context,
                    status=403)
        form = forms.SchoolRegistrationImportForm(request.POST)
        if form.is_valid():
            school_reg_pks = list(map(int,
                    form.cleaned_data['school_registrations'].split(',')))
            school_regs = models.SchoolRegistration.objects.filter(
                    pk__in=school_reg_pks)
            for school_reg in school_regs:
                if school_reg.imported and not form.cleaned_data['reimport']:
                    continue
                if school_reg.imported and form.cleaned_data['reimport']:
                    school_reg.drop_competitors_and_teams()
                school_reg.import_competitors_and_teams()
            return HttpResponseRedirect(reverse('tmdb:tournament_schools',
                    args=(tournament.slug,)))
        context['error_form'] = form

    return build_tournament_schools(request, tournament, context)

def match_list(request, tournament_slug, division_slug=None):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' %(
                    reverse('tmdb:login'), request.path,))
        if not request.user.has_perm('tmdb.change_teammatch'):
            return HttpResponseForbidden(permission_error_string(request.user,
                    "change matches"))
        match = models.TeamMatch.objects.get(pk=request.POST['team_match_id'])
        form = forms.MatchForm(request.POST, instance=match)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.path)

    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    tournament_divisions = models.TournamentDivision.objects.filter(
            tournament__slug=tournament_slug)
    if division_slug is not None:
        tournament_divisions = tournament_divisions.filter(
                division__slug=division_slug)

    matches = []
    for division in tournament_divisions:
        team_matches = models.TeamMatch.objects.filter(
                division=division).order_by('number')
        for team_match in team_matches:
            team_match.form = forms.MatchForm(instance=team_match)
            match_teams = []
            if team_match.blue_team is not None:
                match_teams.append(team_match.blue_team.pk)
            if team_match.red_team is not None:
                match_teams.append(team_match.red_team.pk)
            team_match.form.fields['winning_team'].queryset =  \
                    models.TeamRegistration.objects.filter(pk__in=match_teams)
        matches.append((division, team_matches))
    context = {
        'team_matches' : matches,
        'tournament': tournament,
    }
    return render(request, 'tmdb/match_list.html', context)

@permission_required("tmdb.delete_teamregistration")
def team_registration_delete(request, tournament_slug, school_slug,
        division_slug, team_number):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    school = get_object_or_404(models.School, slug=school_slug)
    division = get_object_or_404(models.Division, slug=division_slug)
    tournament_division = get_object_or_404(models.TournamentDivision,
            tournament=tournament, division=division)
    team = get_object_or_404(models.Team, school=school, division=division,
            number=team_number)
    team_registration = get_object_or_404(models.TeamRegistration,
            tournament_division=tournament_division, team=team)
    context = {}
    context['team'] = team_registration
    if request.method == 'POST':
        delete_form = forms.TeamRegistrationDeleteForm(request.POST,
                instance=team_registration)
        context['delete_form'] = delete_form
        if delete_form.is_valid():
            team_registration.delete()
            return HttpResponseRedirect(reverse("tmdb:tournament_school",
                    args=(tournament_slug, school_slug,)))

@permission_required("tmdb.change_teamregistration")
def team_registration_change(request, tournament_slug, school_slug,
        division_slug, team_number):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    school = get_object_or_404(models.School, slug=school_slug)
    school_registration = get_object_or_404(models.SchoolRegistration,
            tournament=tournament, school=school)
    division = get_object_or_404(models.Division, slug=division_slug)
    tournament_division = get_object_or_404(models.TournamentDivision,
            tournament=tournament, division=division)
    team = get_object_or_404(models.Team, school=school, division=division,
            number=team_number)
    instance = get_object_or_404(models.TeamRegistration,
            tournament_division=tournament_division, team=team)
    template_name = 'tmdb/team_registration_add_change.html'
    context = {}
    context['school'] = school
    context['school_registration'] = school_registration
    context['tournament'] = tournament
    context['instance'] = instance
    used_competitors = []
    if request.method == 'POST':
        edit_form = forms.TeamRegistrationForm(school_registration,
                request.POST, instance=instance)
        context['edit_form'] = edit_form
        if edit_form.is_valid():
            edit_form.save()
            return HttpResponseRedirect(reverse("tmdb:tournament_school", args=(tournament_slug, school_slug,)))
    else:
        edit_form = forms.TeamRegistrationForm(school_registration,
                instance=instance, initial={'tournament': tournament.pk})
        context['edit_form'] = edit_form

    return render(request, template_name, context)

@permission_required("tmdb.add_teamregistration")
def team_registration_add(request, tournament_slug, school_slug):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    school_registration = models.SchoolRegistration.objects.get(
            school__slug=school_slug, tournament=tournament)
    context = {}
    context['school_registration'] = school_registration
    context['tournament'] = tournament
    template_name = 'tmdb/team_registration_add_change.html'
    if request.method == 'POST':
        add_form = forms.TeamRegistrationForm(school_registration,
                request.POST)
        context['add_form'] = add_form
        if add_form.is_valid():
            add_form.save()
            return HttpResponseRedirect(reverse("tmdb:tournament_school", args=(tournament_slug,school_slug,)))
    else:
        add_form = forms.TeamRegistrationForm(school_registration,
                initial={'tournament': tournament.pk})
        context['add_form'] = add_form

    return render(request, template_name, context)

def team_list(request, tournament_slug, division_slug=None):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    tournament_divisions = models.TournamentDivision.objects.filter(
            tournament__slug=tournament_slug)
    if division_slug is not None:
        division = get_object_or_404(models.Division, slug=division_slug)
        tournament_divisions = tournament_divisions.filter(division=division)

    division_teams = []
    for tournament_division in tournament_divisions:
        teams = models.TeamRegistration.order_queryset(
                models.TeamRegistration.objects.filter(
                        tournament_division=tournament_division))
        division_teams.append((tournament_division, teams))

    context = {
        'division_teams' : division_teams,
        'tournament': tournament,
    }
    return render(request, 'tmdb/team_list.html', context)

seeds_re = re.compile('(?P<team_reg_id>[0-9]+)-seed$')
def seedings(request, tournament_slug, division_slug):
    tournament_division = get_object_or_404(models.TournamentDivision,
            tournament__slug=tournament_slug, division__slug=division_slug)
    tournament = tournament_division.tournament
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' %(
                    reverse('tmdb:login'), request.path,))
        if not request.user.has_perm('tmdb.change_teamregistration'):
            return HttpResponseForbidden(permission_error_string(request.user,
                "change team seedings"))
        seed_forms = []
        tournament_division_pk = request.POST["tournament_division_pk"]
        tournament_division = get_object_or_404(models.TournamentDivision,
                pk=tournament_division_pk)
        for post_field in request.POST:
            re_match = seeds_re.match(post_field)
            if not re_match: continue
            team_reg_id = re_match.group('team_reg_id')
            seed_form = forms.SeedingForm(request.POST, prefix=str(team_reg_id),
                    instance=models.TeamRegistration.objects.get(
                            pk=int(team_reg_id)))
            seed_forms.append(seed_form)

        if all(map(forms.SeedingForm.is_valid, seed_forms)):

            tournament_division = forms.SeedingForm.all_seeds_valid(seed_forms)

            for team in forms.SeedingForm.modified_teams(seed_forms):
                team = models.TeamRegistration.objects.get(pk=team.pk)
                team.seed = None
                team.save()

            for form in seed_forms:
                form.save()
            models.TeamMatch.create_matches_from_slots(tournament_division)
            return HttpResponseRedirect(reverse('tmdb:tournament_dashboard',
                    args=(tournament_division.tournament.slug,)))

    else:
        teams = models.TeamRegistration.order_queryset(
                models.TeamRegistration.objects.filter(
                        tournament_division=tournament_division))
        seed_forms = []
        teams = list(teams)
        for team in teams:
            seed_form = forms.SeedingForm(prefix=str(team.id), instance=team)
            seed_form.name = str(team)
            seed_forms.append(seed_form)

    context = {
            'seed_forms': seed_forms,
            'tournament_division': tournament_division,
            'tournament': tournament,
            }
    return render(request, 'tmdb/seedings.html', context)

def build_team_points(request, tournament_division, context=None, status=None):
    if context is None:
        context = {}
    template_name = 'tmdb/points.html'
    tournament = tournament_division.tournament
    teams = models.TeamRegistration.order_queryset(
            models.TeamRegistration.objects.filter(
                tournament_division=tournament_division))
    tournament_divisions = models.TournamentDivision.objects.filter(
            tournament=tournament)
    points_forms = []
    for team in teams:
        points_form = forms.TeamPointsForm(
                prefix=str(team.id), instance=team)
        points_form.name = str(team)
        points_forms.append(points_form)

    context['tournament'] = tournament
    context['points_forms'] = points_forms
    context['tournament_divisions'] = tournament_divisions
    context['tournament_division'] = tournament_division
    return render(request, template_name, context, status)

points_re = re.compile('(?P<team_reg_id>[0-9]+)-points$')
def team_points(request, tournament_slug, division_slug):
    tournament_division = get_object_or_404(models.TournamentDivision,
            tournament__slug=tournament_slug, division__slug=division_slug)
    if not request.method == "POST":
        return build_team_points(request, tournament_division)

    if not request.user.is_authenticated:
        return redirect('%s?next=%s' %(
                reverse('tmdb:login'), request.path,))
    if not request.user.has_perm('tmdb.change_teamregistration'):
        context = {'err_msg': permission_error_string(request.user,
                "change team registration")}
        return build_team_points(request, tournament_division, context,
                status=403)
    for post_field in request.POST:
        re_match = points_re.match(post_field)
        if not re_match: continue
        team_reg_id = int(re_match.group('team_reg_id'))
        points_form = forms.TeamPointsForm(request.POST,
                prefix=str(team_reg_id),
                instance=models.TeamRegistration.objects.get(
                        pk=team_reg_id))
        points_form.save()

    models.TeamRegistration.objects.filter(
            tournament_division=tournament_division).update(seed=None)
    teams = models.TeamRegistration.get_teams_with_assigned_slots(
            tournament_division)
    for team in teams:
        team.save()

    return HttpResponseRedirect(reverse('tmdb:seedings', args=(
            tournament_slug, division_slug)))

def rings(request, tournament_slug):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    matches_by_ring = defaultdict(list)
    for match in models.TeamMatch.objects.filter(ring_number__isnull=False,
            division__tournament=tournament).order_by('-ring_assignment_time'):
        matches_by_ring[str(match.ring_number)].append(match)
    context = {
        'matches_by_ring' : sorted(matches_by_ring.items()),
        'tournament': tournament
    }
    return render(request, 'tmdb/rings.html', context)

def registration_credentials(request):
    template_name = 'tmdb/configuration_setting.html'
    context = {"setting_name": "Registration Import Credentials"}
    setting_key = models.ConfigurationSetting.REGISTRATION_CREDENTIALS
    existing_value = models.ConfigurationSetting.objects.filter(
            key=setting_key).first()
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' %(
                    reverse('tmdb:login'), request.path,))
        form = forms.ConfigurationSetting(request.POST,
                instance=existing_value)
        context['form'] = form
        if not request.user.has_perm('tmdb.change_configurationsetting'):
            context['err_msg'] = permission_error_string(request.user,
                    "change settings")
            return render(request, template_name, context, status=403)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('tmdb:index'))
    else:
        if existing_value is not None:
            value = existing_value.value
        else:
            value = None
        form = forms.ConfigurationSetting(initial={'key': setting_key,
                'value': value})
        context['form'] = form
    return render(request, 'tmdb/configuration_setting.html', context)

def blue_team_text(team_match):
    if team_match.blue_team is None:
        return None
    return team_match.blue_team.bracket_str()

def red_team_text(team_match):
    if team_match.red_team is None:
        return None
    return team_match.red_team.bracket_str()

def bracket_printable(request, tournament_slug, division_slug):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    tournament_division = get_object_or_404(models.TournamentDivision,
            tournament=tournament, division__slug=division_slug)
    matches, num_rounds = models.TeamMatch.get_matches_by_round(
            tournament_division)
    bracket_columns = []
    for round_num in reversed(range(num_rounds + 1)):
        round_num_matches = 2**round_num
        bracket_column = [None] * round_num_matches
        bracket_columns.append(bracket_column)
        for round_slot in range(round_num_matches):
            key = (round_num, round_slot)
            if key not in matches:
                continue
            bracket_column[round_slot] = matches[key]
    bracket = SvgBracket.create(bracket_columns,
            blue_team_text=blue_team_text, red_team_text=red_team_text)
    response = '<html><body>%s</body></html>' %(bracket.tostring(
            encoding="unicode"),)
    return HttpResponse(response, content_type="image/svg+xml")

def bracket(request, tournament_slug, division_slug):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    tournament_division = get_object_or_404(models.TournamentDivision,
            tournament=tournament, division__slug=division_slug)
    bracket_columns = []
    matches, num_rounds = models.TeamMatch.get_matches_by_round(
            tournament_division)
    bracket_column_height = str(64 * 2**num_rounds) + "px"
    for round_num in reversed(range(num_rounds + 1)):
        round_num_matches = 2**round_num
        bracket_column = [None] * round_num_matches
        bracket_columns.append(bracket_column)
        for round_slot in range(round_num_matches):
            key = (round_num, round_slot)
            cell_type = []
            if key not in matches:
                match = models.TeamMatch()
                cell_type.append("bracket_cell_without_match")
            else:
                match = matches[key]
                cell_type.append("bracket_cell_with_match")
            if round_slot % 2:
                cell_type.append("lower_child_cell")
            else:
                cell_type.append("upper_child_cell")
            bracket_column[round_slot] = match
            match.cell_type = " ".join(cell_type)
            match.height = str(100 / (round_num_matches)) + "%"
    if (0, 0) in matches:
        matches[(0, 0)].cell_type = "bracket_cell_with_match" \
                + " bracket_finals_cell"
    unassigned_teams = models.TeamRegistration.get_teams_without_assigned_slot(
            tournament_division)

    context = {
            'tournament_division': tournament_division,
            'tournament': tournament,
            'bracket_columns': bracket_columns,
            'bracket_column_height': bracket_column_height,
            'unassigned_teams': unassigned_teams,
            'lowest_bye_seed': get_lowest_bye_seed(tournament_division),
    }
    return render(request, 'tmdb/brackets.html', context)

def get_lowest_bye_seed(tournament_division):
    team_registrations = models.TeamRegistration.objects.filter(
            tournament_division=tournament_division)
    team_matches = models.TeamMatch.objects.filter(
            division=tournament_division).order_by('-round_num')
    if not team_matches:
        return 1
    max_round_num = team_matches[0].round_num
    seeds = {tr.seed for tr in team_registrations if tr.seed}
    max_seed = max(seeds)
    for team_match in team_matches:
        if team_match.round_num != max_round_num:
            break
        if team_match.blue_team:
            seeds.remove(team_match.blue_team.seed)
        if team_match.red_team:
            seeds.remove(team_match.red_team.seed)
    if not seeds:
        return max_seed
    return max(seeds)

def seeding(request, tournament_slug, division_slug, seed=None):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' %(
                    reverse('tmdb:login'), request.path,))
        if not request.user.has_perm('tmdb.change_teamregistration'):
            return HttpResponseForbidden(permission_error_string(request.user,
                    "change team seeding"))
        form = forms.TeamRegistrationSeedingForm(request.POST)
        if form.is_valid():
            team_registration = models.TeamRegistration.objects.get(
                    pk=request.POST['team_registration'])
            team_registration.seed = int(request.POST['seed'])
            team_registration.save()
            tournament_division = team_registration.tournament_division
            models.TeamMatch.create_matches_from_slots(tournament_division)
            return HttpResponseRedirect(reverse("tmdb:bracket", args=(
                    tournament_division.tournament.slug,
                    tournament_division.division.slug,)))
    else:
        tournament_division = get_object_or_404(models.TournamentDivision,
                tournament__slug=tournament_slug, division__slug=division_slug)
        form = forms.TeamRegistrationSeedingForm(initial={'seed': seed})
        form.fields['team_registration'].queryset = \
                models.TeamRegistration.get_teams_without_assigned_slot(
                        tournament_division)
        form.fields['seed'].widget.attrs['readonly'] = True
    context = {
            'tournament_division': tournament_division,
            'tournament': tournament_division.tournament,
            'form': form,
    }
    return render(request, 'tmdb/modify_team_registration_seed.html', context)

@permission_required("tmdb.add_competitor")
def competitor_add(request, tournament_slug, school_slug):
    template_name = 'tmdb/competitor_add_change.html'
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    school = get_object_or_404(models.School, slug=school_slug)
    school_registration = get_object_or_404(models.SchoolRegistration,
            tournament=tournament, school=school)
    competitors = models.Competitor.objects.filter(registration=school_registration)
    context = {}
    context['tournament'] = tournament
    context['school'] = school
    context['school_registration'] = school_registration
    context['competitors'] = competitors
    if request.method == 'POST':
        add_form = forms.SchoolCompetitorForm(request.POST)
        context['add_form'] = add_form
        if add_form.is_valid():
            add_form.save()
            return HttpResponseRedirect(reverse("tmdb:tournament_school",
                    args=(tournament_slug, school_slug,)))
    else:
        add_form = forms.SchoolCompetitorForm(
                initial={'registration': school_registration})
        context['add_form'] = add_form
    return render(request, template_name, context)

@permission_required("tmdb.change_competitor")
def competitor_change(request, tournament_slug, school_slug, competitor_id):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    school = get_object_or_404(models.School, slug=school_slug)
    school_registration = get_object_or_404(models.SchoolRegistration,
            tournament=tournament, school=school)
    instance = models.Competitor.objects.get(pk = competitor_id)
    template_name = 'tmdb/competitor_add_change.html'
    context = {}
    context['tournament'] = tournament
    context['school'] = school
    context['school_registration'] = school_registration
    context['competitor'] = instance
    context['name'] = instance.name
    if request.method == 'POST':
        change_form = forms.SchoolCompetitorForm(request.POST,
                instance=instance)
        context['change_form'] = change_form
        if change_form.is_valid():
            competitor = change_form.save()
            return HttpResponseRedirect(reverse('tmdb:tournament_school', args = (tournament_slug, school_slug)))
    else:
        change_form = forms.SchoolCompetitorForm(instance = instance)
        change_form.registration = school_registration
        context['change_form'] = change_form
    return render(request, template_name, context)

@permission_required("tmdb.delete_competitor")
def competitor_delete(request, tournament_slug, school_slug, competitor_id):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    school = get_object_or_404(models.School, slug=school_slug)
    school_registration = get_object_or_404(models.SchoolRegistration,
            tournament=tournament, school=school)
    instance = models.Competitor.objects.get(pk = competitor_id)
    template_name = 'tmdb/delete_competitor.html'
    context = {}
    context['tournament'] = tournament
    context['school'] = school
    context['school_registration'] = school_registration
    context['competitor'] = instance
    if request.method == 'POST':
        delete_form = forms.SchoolCompetitorDeleteForm(request.POST,
                instance=instance)
        context['delete_form'] = delete_form
        if delete_form.is_valid():
            instance.delete()
            return HttpResponseRedirect(reverse("tmdb:tournament_school",
                    args=(tournament_slug, school_slug,)))
    else:
        delete_form = forms.SchoolCompetitorDeleteForm(instance = instance)
    context['delete_form'] = delete_form
    return render(request, template_name, context)

def add_upper_match(request, match_id):
    return add_match(request, match_id, side='upper')

def add_lower_match(request, match_id):
    return add_match(request, match_id, side='lower')

def add_match(request, match_id, side):
    next_round_match = models.TeamMatch.objects.get(pk=match_id)
    if side == 'upper':
        existing_team = next_round_match.blue_team
    else:
        existing_team = next_round_match.red_team
    new_seed = 2**(next_round_match.round_num + 2) - existing_team.seed + 1
    tournament_division = next_round_match.division
    tournament_slug = tournament_division.tournament.slug
    division_slug = tournament_division.division.slug
    return seeding(request, tournament_slug, division_slug, new_seed)

#def add_match(request, match_id, side):
#    if side != 'upper' and side != 'lower':
#        raise IllegalArgumentError("side must be 'upper' or 'lower'")
#    next_round_match = models.TeamMatch.objects.get(pk=match_id)
#    round_slot = next_round_match.round_slot * 2
#    if side == 'lower':
#        round_slot+= 1
#
#    previous_round_matches = next_round_match.get_previous_round_matches()
#    for match_index,match in enumerate(previous_round_matches):
#        if match is None:
#            match = models.TeamMatch()
#            previous_round_matches[match_index] = match
#            match.cell_type = "bracket_cell_without_match"
#        else:
#            match.cell_type = "bracket_cell_with_match"
#        match.height = "50%"
#
#    editing_match = previous_round_matches[0 if side == 'upper' else 1]
#    if editing_match is None:
#        editing_match = models.TeamMatch()
#    editing_match.division = next_round_match.division
#
#    unassigned_teams = models.TeamRegistration.get_teams_without_assigned_slot(
#            tournament_division)
#    if next_round_match.blue_team:
#        editing_match.blue_team = next_round_match.blue_team
#        editing_match.red_team = unassigned_teams
#    elif next_round_match.red_team:
#        editing_match.red_team = next_round_match.red_team
#        next_round_match.blue_team = unassigned_teams
#    else:
#        raise NotImplementedError()
#
#    editing_match.blue_team = models.TeamRegistration.objects.first()
#    editing_match.red_team = models.TeamRegistration.objects.first()
#    editing_match.cell_type = "bracket_cell_with_match"
#
#    previous_round_matches[0].cell_type += " upper_child_cell"
#    previous_round_matches[1].cell_type += " lower_child_cell"
#
#    bracket_column_height = str(100 * 2**2) + "px"
#
#    next_round_match.cell_type = "bracket_cell_with_match bracket_finals_cell"
#    next_round_match.height = "100%"
#
#    if request.method == "POST":
#         if not request.user.is_authenticated:
#             return redirect('%s?next=%s' %(
#                     reverse('tmdb:login'), request.path,))
#         raise Exception("permission_check")
#        raise NotImplementedError()
#
#    bracket_columns = [previous_round_matches, [next_round_match]]
#
#    context = {
#            'tournament_division': next_round_match.division,
#            'tournament': next_round_match.division.tournament,
#            'bracket_columns': bracket_columns,
#            'bracket_column_height': bracket_column_height,
#    }
#    return render(request, 'tmdb/bracket_match_edit.html', context)

def match_sheet(request, tournament_slug, division_slug, match_number=None):
    tournament_division = get_object_or_404(models.TournamentDivision,
            tournament__slug=tournament_slug, division__slug=division_slug)
    filename = "%s-%s" %(tournament_slug, division_slug)
    if match_number:
        matches = [models.TeamMatch.objects.get(division=tournament_division,
                number=match_number)]
        filename += "-match_%s.pdf" %(match_number,)
    else:
        matches = models.TeamMatch.objects.filter(
                division=tournament_division).order_by('number')
        filename += "-matches.pdf"
    sheet = create_match_sheets(matches)

    response = HttpResponse(sheet, content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename=%s' %(filename,)
    return response

def create_headtable_user(request):
    template_name = 'tmdb/add_user.html'
    context = {}
    context['form_action'] = reverse('tmdb:create_headtable_user')
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' %(
                    reverse('tmdb:login'), request.path,))
        form = forms.UserForm(request.POST)
        context['form'] = form
        if not request.user.has_perm('auth.add_user'):
            context['err_msg'] = permission_error_string(request.user,
                    "create users")
            return render(request, template_name, context, status=403)
        if form.is_valid():
            user = auth_models.User.objects.create_user(**form.cleaned_data)
            user.groups.set([get_headtable_permission_group()])
            return HttpResponseRedirect(reverse('tmdb:settings'))
    else:
        form = forms.UserForm()

    context['form'] = form
    return render(request, 'tmdb/add_user.html', context)

def create_ringtable_user(request):
    template_name = 'tmdb/add_user.html'
    context = {}
    context['form_action'] = reverse('tmdb:create_ringtable_user')
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' %(
                    reverse('tmdb:login'), request.path,))
        form = forms.UserForm(request.POST)
        context['form'] = form
        if not request.user.has_perm('auth.add_user'):
            context['err_msg'] = permission_error_string(request.user,
                    "create users")
            return render(request, template_name, context, status=403)
        if form.is_valid():
            user = auth_models.User.objects.create_user(**form.cleaned_data)
            user.groups.set([get_ringtable_permission_group()])
            return HttpResponseRedirect(reverse('tmdb:settings'))
    else:
        form = forms.UserForm()

    context['form'] = form
    return render(request, 'tmdb/add_user.html', context)

def get_ringtable_permission_group():
    group = auth_models.Group.objects.filter(name = "Ring Table").first()
    if not group:
        group = create_ringtable_permission_group()
    return group

def create_ringtable_permission_group():
    group = auth_models.Group.objects.create(name="Ring Table")
    group.permissions.set([auth_models.Permission.objects.get(
            name='Can change team match')])
    return group

def get_headtable_permission_group():
    group = auth_models.Group.objects.filter(name = "Head Table").first()
    if not group:
        group = create_headtable_permission_group()
    return group

def create_headtable_permission_group():
    group = auth_models.Group.objects.create(name="Head Table")
    group.permissions.set(auth_models.Permission.objects.filter(
            content_type__in=auth_models.ContentType.objects.filter(
                    app_label="tmdb")))
    group.permissions.add(auth_models.Permission.objects.get(
            name="Can add user"))
    return group
