from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.forms.models import modelformset_factory
from django.core.urlresolvers import reverse

from . import forms
from . import models

from collections import defaultdict
import re
import datetime

def index(request, tournament_slug=None):
    if request.method == 'POST':
        instance = get_object_or_404(models.Tournament, slug=tournament_slug)
        delete_form = forms.TournamentDeleteForm()
        context['delete_form'] = delete_form
    else:
        today = datetime.date.today()
        edit_form = forms.TournamentEditForm(initial={'date': today})
        context = {
            'edit_form': edit_form,
            'tournaments': models.Tournament.objects.order_by('-date')
        }
    return render(request, 'tmdb/index.html', context)

def settings(request):
    return render(request, 'tmdb/settings.html')

def tournament_create(request):
    if request.method == 'POST':
        edit_form = forms.TournamentEditForm(request.POST)
        if edit_form.is_valid():
            edit_form.save()
            return HttpResponseRedirect(reverse('tmdb:index'))
    else:
        today = datetime.date.today()
        edit_form = forms.TournamentEditForm(initial={'date': today})
    context = {'edit_form': edit_form}
    return render(request, 'tmdb/tournament_edit.html', context)

def tournament_edit(request, tournament_slug):
    instance = get_object_or_404(models.Tournament, slug=tournament_slug)
    context = {}
    if request.method == 'POST':
        edit_form = forms.TournamentEditForm(request.POST, instance=instance)
        if edit_form.is_valid():
            tournament = edit_form.save()
            return HttpResponseRedirect(reverse('tmdb:index'))
    else:
        edit_form = forms.TournamentEditForm(instance=instance)
        import_form = forms.TournamentImportForm(instance=instance)
        context['import_form'] = import_form
        delete_form = forms.TournamentDeleteForm(instance=instance)
        context['delete_form'] = delete_form
    context['edit_form'] = edit_form
    return render(request, 'tmdb/tournament_edit.html', context)

def tournament_delete(request, tournament_slug):
    instance = get_object_or_404(models.Tournament, slug=tournament_slug)
    if request.method == 'POST':
        delete_form = forms.TournamentDeleteForm(request.POST,
                instance=instance)
        if delete_form.is_valid():
            instance.delete()
            return HttpResponseRedirect(reverse('tmdb:index'))
    else:
        delete_form = forms.TournamentDeleteForm(instance=instance)
    context = {'delete_form': delete_form, 'tournament': instance}
    return render(request, 'tmdb/tournament_delete.html', context)

def tournament_import(request, tournament_slug):
    instance = models.Tournament.objects.filter(slug=tournament_slug).first()
    if request.method == "POST":
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

    # Add all to the context.
    context = {
        'tournament': tournament,
        'tournament_divisions': tournament_divisions,
        'matches_by_ring':sorted(matches_by_ring.items()),
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
    team_registrations = models.TeamRegistration.objects.filter(
            tournament_division__tournament=tournament,
            team__school=school).order_by(
                    'tournament_division__division', 'team__number')
    context = {
        'school_registration': school_registration,
        'competitors': competitors,
        'team_registrations': team_registrations,
    }
    return render(request, 'tmdb/tournament_school_competitors.html', context)

def tournament_schools(request, tournament_slug):
    context = {}
    if request.method == "POST":
        tournament_slug = request.POST['tournament_slug']
        tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
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
    else:
        tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
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
    context['tournament'] = tournament
    context['all_schools_imported'] = all_schools_imported
    context['import_all_form'] = forms.SchoolRegistrationImportForm(
            initial={
                'reimport': False,
                'school_registrations': ','.join(map(str, school_pks))
            })
    return render(request, 'tmdb/tournament_schools.html', context)

def match_list(request, tournament_slug, division_slug=None):
    if request.method == 'POST':
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
            team_match.form.fields['winning_team'].queryset = \
                    models.TeamRegistration.objects.filter(pk__in=match_teams)
        matches.append((division, team_matches))
    context = {
        'team_matches' : matches,
        'tournament': tournament,
    }
    return render(request, 'tmdb/match_list.html', context)

def team_list(request, tournament_slug, division_slug=None):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    tournament_divisions = models.TournamentDivision.objects.filter(
            tournament__slug=tournament_slug)
    if division_slug is not None:
        tournament_divisions = tournament_divisions.filter(
                division__slug=division_slug)

    division_teams = []
    for tournament_division in tournament_divisions:
        teams = models.TeamRegistration.objects.filter(
                tournament_division=tournament_division).order_by(
                        'school').order_by('team__number')
        division_teams.append((tournament_division, teams))

    context = {
        'division_teams' : division_teams,
        'tournament': tournament,
    }
    return render(request, 'tmdb/team_list.html', context)

seeds_re = re.compile('(?P<team_reg_id>[0-9]+)-seed$')
def seedings(request, tournament_slug, division_slug):
    if request.method == 'POST':
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
        tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
        tournament_division = get_object_or_404(models.TournamentDivision,
                tournament=tournament, division__slug=division_slug)
        teams = models.TeamRegistration.objects.filter(
                tournament_division=tournament_division).order_by(
                        'team__school__name', 'team__number')
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

points_re = re.compile('(?P<team_reg_id>[0-9]+)-points$')
def team_points(request, tournament_slug, division_slug):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    tournament_division = get_object_or_404(models.TournamentDivision,
            tournament=tournament, division__slug=division_slug)
    if request.method == "POST":
        for post_field in request.POST:
            re_match = points_re.match(post_field)
            if not re_match: continue
            team_reg_id = int(re_match.group('team_reg_id'))
            points_form = forms.TeamPointsForm(request.POST,
                    prefix=str(team_reg_id),
                    instance=models.TeamRegistration.objects.get(
                            pk=team_reg_id))
            points_form.save()

        teams = models.TeamRegistration.get_teams_with_assigned_slots(
                tournament_division)
        for team in teams:
            team.save()

        return HttpResponseRedirect(reverse('tmdb:seedings', args=(
                tournament_slug, division_slug)))
    else:
        teams = models.TeamRegistration.objects.filter(
                tournament_division=tournament_division).order_by('team__number').order_by('team__school')
        points_forms = []
        for team in teams:
            points_form = forms.TeamPointsForm(
                    prefix=str(team.id), instance=team)
            points_form.name = str(team)
            points_forms.append(points_form)

    context = {
            'tournament': tournament,
            'points_forms': points_forms,
            'tournament_division': tournament_division,
            }
    return render(request, 'tmdb/points.html', context)

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
    setting_key = models.ConfigurationSetting.REGISTRATION_CREDENTIALS
    existing_value = models.ConfigurationSetting.objects.filter(
            key=setting_key).first()
    if request.method == 'POST':
        form = forms.ConfigurationSetting(request.POST,
                instance=existing_value)
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
    context = {
            "setting_name": "Registration Import Credentials",
            "form": form
    }
    return render(request, 'tmdb/configuration_setting.html', context)

def bracket(request, tournament_slug, division_slug):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    tournament_division = get_object_or_404(models.TournamentDivision,
            tournament=tournament, division__slug=division_slug)
    bracket_columns = []
    matches = {}
    num_rounds = 0
    for match in models.TeamMatch.objects.filter(division=tournament_division):
        matches[(match.round_num, match.round_slot)] = match
        num_rounds = max(num_rounds, match.round_num)
    bracket_column_height = str(100 * 2**num_rounds) + "px"
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
    context = {
            'tournament_division': tournament_division,
            'tournament': tournament,
            'bracket_columns': bracket_columns,
            'bracket_column_height': bracket_column_height,
    }
    return render(request, 'tmdb/brackets.html', context)
