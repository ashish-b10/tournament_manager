import json

from django.shortcuts import redirect, render, get_object_or_404
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import models as auth_models
from django.contrib import messages
from django import forms as django_forms

from tmdb import models

from collections import defaultdict
import datetime

from tmdb.util.match_sheet import create_match_sheets
from tmdb.util.bracket_svg import SvgBracket

class SparringTeamRegistrationDeleteForm(django_forms.ModelForm):
    class Meta:
        model = models.SparringTeamRegistration
        fields = []

class SparringTeamRegistrationForm(django_forms.ModelForm):
    def __init__(self, school_tournament_registration, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.school_tournament_registration = school_tournament_registration
        self.school = school_tournament_registration.school_season_registration.school

    def validate_num_competitors(self, validation_errors):
        if self.cleaned_data['lightweight'] or \
                self.cleaned_data['middleweight'] or \
                self.cleaned_data['heavyweight']:
            return
        validation_errors.append(django_forms.ValidationError(
                "Team must have a lightweight, middleweight or heavyweight"
        ))

class SparringTeamRegistrationAddForm(SparringTeamRegistrationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['team'].widget = django_forms.HiddenInput()
        self.fields['team'].required = False

        self.fields['school'] = django_forms.IntegerField()
        self.fields['school'].initial = self.school.pk
        self.fields['school'].widget = django_forms.HiddenInput()

        self.fields['number'] = django_forms.IntegerField()
        self.fields['number'].widget = django_forms.Select(choices=(
                [(i, i) for i in range(1,11)]))
        self.order_fields([
                'tournament_division',
                'team',
                'school',
                'number',
                'lightweight',
                'middleweight',
                'heavyweight',
                'alternate1',
                'alternate2',
        ])
        self.fields['tournament_division'].queryset = models.TournamentSparringDivision.objects.filter(
                tournament=self.school_tournament_registration.tournament)

    def clean_school(self):
        return models.School.objects.get(pk=self.cleaned_data['school'])

    def clean_and_validate_team(self, validation_errors):
        sparring_team, created = models.SparringTeam.objects.get_or_create(
                school=self.cleaned_data['school'],
                division=self.cleaned_data['tournament_division'].division,
                number=self.cleaned_data['number']
        )
        self.cleaned_data['team'] = sparring_team
        if not models.SparringTeamRegistration.objects.filter(
                team=self.cleaned_data['team'],
                tournament_division=self.cleaned_data['tournament_division']):
            return
        validation_errors.append(
                "There is already a %s team registered for this tournament" %(
                        self.cleaned_data['team']))

    def clean(self):
        validation_errors = []
        self.validate_num_competitors(validation_errors)
        self.clean_and_validate_team(validation_errors)
        if validation_errors:
            raise django_forms.ValidationError(validation_errors)

    class Meta:
        model = models.SparringTeamRegistration
        exclude = ['seed', 'points']

class SparringTeamRegistrationChangeForm(SparringTeamRegistrationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tournament_division'].widget = django_forms.HiddenInput()

        self.fields['team'] = django_forms.IntegerField()
        self.fields['team'].initial = self.instance.pk
        self.fields['team'].widget = django_forms.HiddenInput()

    def clean(self):
        validation_errors = []
        self.validate_num_competitors(validation_errors)
        if validation_errors:
            raise django_forms.ValidationError(validation_errors)

    class Meta:
        model = models.SparringTeamRegistration
        exclude = ['seed', 'points', 'team']

@permission_required("tmdb.delete_sparringteamregistration")
def team_registration_delete(request, tournament_slug, school_slug,
        division_slug, team_number):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    school = get_object_or_404(models.School, slug=school_slug)
    division = get_object_or_404(models.SparringDivision, slug=division_slug)
    tournament_division = get_object_or_404(models.TournamentSparringDivision,
            tournament=tournament, division=division)
    team = get_object_or_404(models.SparringTeam,
            school=school, division=division, number=team_number)
    team_registration = get_object_or_404(models.SparringTeamRegistration,
            tournament_division=tournament_division, team=team)
    context = {
        'school': school,
        'team_registration': team_registration,
        'tournament': tournament,
        'tournament_division': tournament_division,
    }
    context['team_registration'] = team_registration
    if request.method == 'POST':
        delete_form = SparringTeamRegistrationDeleteForm(request.POST,
                instance=team_registration)
        if delete_form.is_valid():
            team_registration.delete()
            return HttpResponseRedirect(reverse("tmdb:tournament_school",
                    args=(tournament_slug, school_slug,)))
    else:
        delete_form = SparringTeamRegistrationDeleteForm(
                instance=team_registration)
    context['delete_form'] = delete_form
    return render(request, 'tmdb/team_registration_delete.html', context)

@permission_required("tmdb.change_sparringteamregistration")
def team_registration_change(request, tournament_slug, school_slug,
        division_slug, team_number):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    school = get_object_or_404(models.School, slug=school_slug)
    school_registration = get_object_or_404(models.SchoolTournamentRegistration,
            tournament=tournament, school_season_registration__school=school)
    division = get_object_or_404(models.SparringDivision, slug=division_slug)
    tournament_division = get_object_or_404(models.TournamentSparringDivision,
            tournament=tournament, division=division)
    team = get_object_or_404(models.SparringTeam, school=school,
            division=division, number=team_number)
    instance = get_object_or_404(models.SparringTeamRegistration,
            tournament_division=tournament_division, team=team)
    template_name = 'tmdb/team_registration_add_change.html'
    context = {}
    context['school'] = school
    context['school_registration'] = school_registration
    context['tournament'] = tournament
    context['instance'] = instance
    used_competitors = []
    if request.method == 'POST':
        edit_form = SparringTeamRegistrationChangeForm(school_registration,
                request.POST, instance=instance)
        if edit_form.is_valid():
            edit_form.save()
            return HttpResponseRedirect(reverse("tmdb:tournament_school", args=(tournament_slug, school_slug,)))
    else:
        edit_form = SparringTeamRegistrationChangeForm(school_registration,
                instance=instance, initial={'tournament': tournament.pk})
    context['edit_form'] = edit_form
    return render(request, template_name, context)

@permission_required("tmdb.add_sparringteamregistration")
def team_registration_add(request, tournament_slug, school_slug):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    school_registration = models.SchoolTournamentRegistration.objects.get(
            school_season_registration__school__slug=school_slug,
            tournament=tournament)
    context = {}
    context['school_registration'] = school_registration
    context['tournament'] = tournament
    template_name = 'tmdb/team_registration_add_change.html'
    if request.method == 'POST':
        add_form = SparringTeamRegistrationAddForm(school_registration,
                request.POST)
        if add_form.is_valid():
            add_form.save()
            return HttpResponseRedirect(reverse("tmdb:tournament_school", args=(tournament_slug,school_slug,)))
    else:
        add_form = SparringTeamRegistrationAddForm(school_registration,
                initial={'tournament': tournament.pk})
    context['add_form'] = add_form
    return render(request, template_name, context)

def team_list(request, tournament_slug, division_slug=None):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    tournament_divisions = models.TournamentSparringDivision.objects.filter(
            tournament__slug=tournament_slug)
    if division_slug is not None:
        division = get_object_or_404(models.SparringDivision,
                slug=division_slug)
        tournament_divisions = tournament_divisions.filter(division=division)

    division_teams = []
    for tournament_division in tournament_divisions:
        teams = models.SparringTeamRegistration.order_queryset(
                models.SparringTeamRegistration.objects.filter(
                        tournament_division=tournament_division))
        division_teams.append((tournament_division, teams))

    context = {
        'division_teams' : division_teams,
        'tournament': tournament,
    }
    return render(request, 'tmdb/team_list.html', context)
