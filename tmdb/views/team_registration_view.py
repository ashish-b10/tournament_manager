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
    context = {
        'school': school,
        'team_registration': team_registration,
        'tournament': tournament,
        'tournament_division': tournament_division,
    }
    context['team_registration'] = team_registration
    if request.method == 'POST':
        delete_form = forms.TeamRegistrationDeleteForm(request.POST,
                instance=team_registration)
        if delete_form.is_valid():
            team_registration.delete()
            return HttpResponseRedirect(reverse("tmdb:tournament_school",
                    args=(tournament_slug, school_slug,)))
    else:
        delete_form = forms.TeamRegistrationDeleteForm(
                instance=team_registration)
    context['delete_form'] = delete_form
    return render(request, 'tmdb/team_registration_delete.html', context)

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
