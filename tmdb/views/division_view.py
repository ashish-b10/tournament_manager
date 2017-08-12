"""
Division View

Last Updated: 07-09-2017
"""

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

def division_seedings(request, tournament_slug, division_slug):
    tournament_division = get_object_or_404(models.TournamentDivision,
            tournament__slug=tournament_slug, division__slug=division_slug)
    team_registrations = models.TeamRegistration.objects.filter(
            tournament_division=tournament_division).order_by(
            'team__school__name', 'team__number')
    unimported_schools = models.SchoolRegistration.objects.filter(
            tournament=tournament_division.tournament, imported=False)
    context = {
        'tournament': tournament_division.tournament,
        'tournament_division': tournament_division,
        'team_registrations': team_registrations,
        'unimported_schools': unimported_schools,
    }
    return render(request, 'tmdb/tournament_division_seedings.html', context)

@permission_required('tmdb.change_teamregistration')
def division_seeding(request, tournament_slug, division_slug, team_slug):
    team_registration = get_object_or_404(models.TeamRegistration,
            tournament_division__tournament__slug=tournament_slug,
            tournament_division__division__slug=division_slug,
            team__slug=team_slug)
    tournament_division = team_registration.tournament_division
    if request.method == 'POST':
        edit_form = forms.TeamRegistrationPointsSeedingForm(request.POST,
                instance=team_registration)
        if edit_form.is_valid():
            edit_form.save()
            return HttpResponseRedirect(reverse('tmdb:division_seedings',
                    args=(tournament_slug, division_slug,)))
    else:
        edit_form = forms.TeamRegistrationPointsSeedingForm(
                instance=team_registration,
                initial={'recompute_seedings': True})
    context = {
        'edit_form': edit_form,
        'tournament': tournament_division.tournament,
        'tournament_division': tournament_division,
    }
    return render(request, 'tmdb/division_seeding_change.html', context)

@permission_required(["tmdb.add_teammatch", "tmdb.delete_teammatch"])
def create_tournament_division_matches(request, tournament_slug, division_slug):
    if request.method != "POST":
        return HttpResponse("Invalid operation: %s on %s" %(request.method,
                request.get_full_path()), status=400)
    tournament_division = get_object_or_404(models.TournamentDivision,
            tournament__slug=tournament_slug, division__slug=division_slug)
    models.TeamMatch.create_matches_from_slots(tournament_division)
    return HttpResponseRedirect(reverse('tmdb:tournament_dashboard',
            args=(tournament_slug,)))
