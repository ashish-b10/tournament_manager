import json

from django.shortcuts import redirect, render, get_object_or_404
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import models as auth_models
from django.contrib import messages
from django import forms as django_forms

from tmdb import forms
from tmdb import models

from collections import defaultdict
import datetime

from tmdb.util.bracket_pdf import create_bracket_pdf
from tmdb.util.bracket_svg import SvgBracket

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

def bracket_printable_pdf(request, tournament_slug, division_slug):
    tournament_division = get_object_or_404(models.TournamentDivision,
            tournament__slug=tournament_slug, division__slug=division_slug)
    matches = models.TeamMatch.objects.filter(division=tournament_division)
    filename = "%s %s.pdf" %(str(tournament_division.tournament),
            str(tournament_division))
    filename = filename.lower().replace(' ', '_')
    bracket_pdf = create_bracket_pdf(matches)

    response = HttpResponse(bracket_pdf, content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename=%s' %(filename,)
    return response

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

@permission_required("tmdb.add_teammatch")
def add_team_to_bracket(request, tournament_slug, division_slug):
    tournament_division = get_object_or_404(models.TournamentDivision,
            tournament__slug=tournament_slug, division__slug=division_slug)
    context = {}

    if request.method == 'POST':
        form = forms.TeamRegistrationBracketSeedingForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("tmdb:bracket", args=(
                    tournament_division.tournament.slug,
                        tournament_division.division.slug,)))
        context = form.cleaned_data
    else:
        side = request.GET.get('side')
        round_number = request.GET.get('round_num')
        round_slot = request.GET.get('round_slot')

        tournament_division = get_object_or_404(models.TournamentDivision,
                tournament__slug=tournament_slug, division__slug=division_slug)
        existing_match = get_object_or_404(models.TeamMatch,
                division=tournament_division, round_num=round_number,
                round_slot=round_slot)

        if side == "upper":
            existing_team = existing_match.blue_team
        elif side == "lower":
            existing_team = existing_match.red_team
        else:
            raise ValueError("side was `%s`, must be `upper` or `lower`" %(side,))
        new_seed = 2**(int(round_number) + 2) - existing_team.seed + 1
        form = forms.TeamRegistrationBracketSeedingForm(initial={'seed': new_seed, 'existing_team': existing_team.id})
        context['existing_team'] = existing_team
        context['seed'] = new_seed

    form.fields['team_registration'].queryset = \
            models.TeamRegistration.get_teams_without_assigned_slot(
                    tournament_division)
    context['tournament_division'] = tournament_division
    context['tournament'] = tournament_division.tournament
    context['form'] = form
    return render(request, 'tmdb/modify_team_registration_seed.html', context)

@permission_required("tmdb.add_teammatch")
def remove_team_from_bracket(request, tournament_slug, division_slug):
    tournament_division = get_object_or_404(models.TournamentDivision,
            tournament__slug=tournament_slug, division__slug=division_slug)
    team_registration_pk = request.GET.get('team_registration')
    team_registration = get_object_or_404(models.TeamRegistration,
            pk=team_registration_pk)
    if request.method == 'POST':
        form = forms.TeamRegistrationSeedingForm(request.POST,
                instance=team_registration)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('tmdb:bracket',
                    args=(tournament_slug, division_slug,)))
    else:
        form = forms.TeamRegistrationSeedingForm(initial={'seed': None})
        form.fields['seed'].widget = django_forms.HiddenInput()
    context = {
        'form': form,
        'team_registration': team_registration,
        'tournament': tournament_division.tournament,
        'tournament_division': tournament_division,
    }
    return render(request, 'tmdb/division_seeding_delete.html', context)
