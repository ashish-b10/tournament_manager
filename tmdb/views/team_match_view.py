import json

from django.shortcuts import redirect, render, get_object_or_404
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
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
    tournament_division = get_object_or_404(models.TournamentSparringDivision,
            tournament__slug=tournament_slug, division__slug=division_slug)
    team_match = get_object_or_404(models.SparringTeamMatch,
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
        teams = models.SparringTeamRegistration.objects.filter(
                pk__in=match_teams)
        team_match_form.fields['winning_team'].queryset = teams
    context['team_match_form'] = team_match_form
    return render(request, "tmdb/team_match_status_change.html", context)

def matches(request, tournament_slug):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    context = {
        'tournament': tournament,
    }
    return render(request, 'tmdb/matches.html', context)

def match_sheet(request, tournament_slug, division_slug, match_number=None):
    tournament_division = get_object_or_404(models.TournamentSparringDivision,
            tournament__slug=tournament_slug, division__slug=division_slug)
    filename = _match_sheet_filename(tournament_slug, division_slug,
            match_number)
    if match_number:
        matches = [models.SparringTeamMatch.objects.get(
                division=tournament_division, number=match_number)]
    else:
        matches = models.SparringTeamMatch.objects.filter(
                division=tournament_division).order_by('number')
    sheet = create_match_sheets(matches)

    response = HttpResponse(sheet, content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename=%s' %(filename,)
    return response

def _match_sheet_filename(tournament_slug, division_slug, match_number=None):
    filename = "%s-%s" %(tournament_slug, division_slug)
    if match_number:
        filename += "-match_%s.pdf" %(match_number,)
    else:
        filename += "-matches.pdf"

    return filename
