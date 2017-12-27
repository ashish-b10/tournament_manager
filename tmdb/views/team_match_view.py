import json

from django.shortcuts import redirect, render, get_object_or_404
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import models as auth_models
from django.contrib import messages

from tmdb import forms
from tmdb import models

from collections import defaultdict
import datetime

from tmdb.util.match_sheet import create_match_sheets
from tmdb.util.bracket_svg import SvgBracket

@permission_required("tmdb.change_teammatch")
def update_teammatch_status(request, tournament_slug, division_slug, match_num):
    tournament_division = get_object_or_404(models.TournamentDivision,
            tournament__slug=tournament_slug, division__slug=division_slug)
    team_match = get_object_or_404(models.TeamMatch,
            division=tournament_division, number=match_num)
    context = {
        'tournament': tournament_division.tournament,
        'tournament_division': tournament_division,
        'team_match': team_match,
    }
    if request.method == 'POST':
        team_match_form = forms.MatchForm(request.POST, instance=team_match)
        if team_match_form.is_valid():
            team_match_form.save()
            return HttpResponseRedirect(reverse("tmdb:match_list",
                    args=(tournament_slug,)))
    else:
        team_match_form = forms.MatchForm(instance=team_match)
        match_teams = []
        if team_match.blue_team is not None:
            match_teams.append(team_match.blue_team.pk)
        if team_match.red_team is not None:
            match_teams.append(team_match.red_team.pk)
        teams = models.TeamRegistration.objects.filter(pk__in=match_teams)
        team_match_form.fields['winning_team'].queryset = teams
    context['team_match_form'] = team_match_form
    return render(request, "tmdb/team_match_status_change.html", context)

def matches(request, tournament_slug):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    tournament_divisions = models.TournamentDivision.objects.filter(
            tournament__slug=tournament_slug)

    all_matches = []
    matches_by_division = []
    for division in tournament_divisions:
        team_matches = models.TeamMatch.objects.filter(
                division=division).order_by('number')
        matches_by_division.append((division, team_matches))
        all_matches += team_matches

    context = {
        'tournament': tournament,
        'tournament_divisions': tournament_divisions,
        'all_matches': all_matches,
        'matches_by_division': matches_by_division,
    }
    return render(request, 'tmdb/matches.html', context)

def _match_sheet_reponse(matches, filename):
    sheet = create_match_sheets(matches)

    response = HttpResponse(sheet, content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename=%s' %(filename,)
    return response

def match_sheet(request, tournament_slug, division_slug, match_number=None):
    tournament_division = get_object_or_404(models.TournamentDivision,
            tournament__slug=tournament_slug, division__slug=division_slug)
    filename = _match_sheet_filename(tournament_slug, division_slug,
            match_number)
    if match_number:
        matches = [models.TeamMatch.objects.get(division=tournament_division,
                number=match_number)]
    else:
        matches = models.TeamMatch.objects.filter(
                division=tournament_division).order_by('number')
    return _match_sheet_reponse(matches, filename)

def _match_sheet_filename(tournament_slug, division_slug, match_number=None):
    filename = "%s-%s" %(tournament_slug, division_slug)
    if match_number:
        filename += "-match_%s.pdf" %(match_number,)
    else:
        filename += "-matches.pdf"

    return filename

def match_sheet_by_pk(request):
    match = models.TeamMatch.objects.get(pk=request.GET['team_match_pk'])
    tournament_slug = match.division.tournament.slug
    division_slug = match.division.division.slug
    filename = _match_sheet_filename(tournament_slug, division_slug,
            match.number)
    return _match_sheet_reponse([match], filename)
