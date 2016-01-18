from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.forms.models import modelformset_factory
from django.core.urlresolvers import reverse

from . import forms
from . import models

from collections import defaultdict
import re
import datetime

def division_list(request):
    divisions = models.Division.objects.all()
    context = {'divisions' : divisions}
    return render(request, 'tmdb/division.html', context)

def index(request):
    context = {'tournaments' : models.Tournament.objects.order_by('-date')}
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
        instance.import_tournament_organizations()
    return HttpResponseRedirect(reverse('tmdb:index'))

def tournament_dashboard(request, tournament_slug):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug) 
    organizations = models.TournamentOrganization.objects.filter(
            tournament=tournament).order_by('organization__name')
    for org in organizations:
        org.import_form = forms.TournamentOrganizationImportForm(instance=org)
    divisions = models.Division.objects.all()
    context = {
        'tournament': tournament,
        'organizations': organizations,
        'divisions': divisions,
    }
    return render(request, 'tmdb/tournament_dashboard.html', context)

def tournament_school(request, tournament_slug, school_slug):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    organization = get_object_or_404(models.Organization, slug=school_slug)
    tournament_organization = get_object_or_404(models.TournamentOrganization,
            tournament=tournament, organization=organization)
    competitors = models.Competitor.objects.filter(
            registration=tournament_organization).order_by('name')
    team_registrations = models.TeamRegistration.objects.filter(
            tournament_division__tournament=tournament,
            team__school=organization).order_by(
                    'tournament_division__division', 'team__number')
    context = {
        'tournament_organization': tournament_organization,
        'competitors': competitors,
        'team_registrations': team_registrations,
    }
    return render(request, 'tmdb/tournament_school_competitors.html', context)

def tournament_schools(request, tournament_slug):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    organizations = models.TournamentOrganization.objects.filter(
            tournament=tournament).order_by('organization__name')
    for org in organizations:
        org.import_form = forms.TournamentOrganizationImportForm(instance=org)
    context = {
        'tournament': tournament,
        'organizations': organizations,
    }
    return render(request, 'tmdb/tournament_schools.html', context)

def tournament_schools_import(request, tournament_slug, school_slug):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    organization = get_object_or_404(models.Organization, slug=school_slug)
    tournament_organization = get_object_or_404(models.TournamentOrganization,
            tournament=tournament, organization=organization)
    if request.method == "POST":
        form = forms.TournamentOrganizationImportForm(request.POST)
        if form.is_valid():
            tournament_organization.import_competitors_and_teams()
    return HttpResponseRedirect(reverse('tmdb:tournament_schools',
            args=(tournament.slug,)))

def match_list(request, division_id=None):
    if division_id is None:
        divisions = models.Division.objects.all()
    else:
        divisions=[models.Division.objects.get(pk=division_id)]

    matches = []
    for division in divisions:
        team_matches = models.TeamMatch.objects.filter(
                division=division).order_by('number')
        matches.append((division, team_matches))
    context = {'team_matches' : matches}
    return render(request, 'tmdb/match_list.html', context)

def team_list(request, division_id=None):
    if division_id is None:
        divisions = models.Division.objects.all()
    else:
        divisions=[models.Division.objects.get(pk=division_id)]

    division_teams = []
    for division in divisions:
        teams = models.Team.objects.filter(
                division=division).order_by('organization').order_by('number')
        division_teams.append((division, teams))

    context = { 'division_teams' : division_teams }
    return render(request, 'tmdb/team_list.html', context)

seedings_form_re = re.compile('(?P<team_id>[0-9]+)-seed$')
def seedings(request, division_id):
    if request.method == 'POST':
        seed_forms = []
        for post_field in request.POST:
            re_match = seedings_form_re.match(post_field)
            if not re_match: continue
            team_id = re_match.group('team_id')
            seed_form = forms.SeedingForm(request.POST, prefix=str(team_id),
                    instance=models.Team.objects.get(pk=int(team_id)))
            seed_forms.append(seed_form)

        if all(map(forms.SeedingForm.is_valid, seed_forms)):

            division = forms.SeedingForm.all_seeds_valid(seed_forms)

            for team in forms.SeedingForm.modified_teams(seed_forms):
                team = models.Team.objects.get(pk=team.pk)
                team.seed = None
                team.save()

            for form in seed_forms:
                form.save()
            models.TeamMatch.create_matches_from_seeds(division)
            return HttpResponseRedirect('/tmdb/matches/' + division_id)

    else:
        seed_forms = []
        for team in models.Team.objects.filter(division=division_id):
            seed_form = forms.SeedingForm(prefix=str(team.id), instance=team)
            seed_form.name = str(team)
            seed_forms.append(seed_form)

    division_name = str(models.Division.objects.get(pk=division_id))

    context = {'division': division_id, 'seed_forms': seed_forms,
            'division_name': division_name}
    return render(request, 'tmdb/seedings.html', context)

def match(request, match_num):
    match = models.TeamMatch.objects.get(number=match_num)
    if request.method == 'POST':
        form = forms.MatchForm(request.POST, instance=match)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/tmdb/matches/'
                    + str(match.division.pk))
    else:
        form = forms.MatchForm(instance=match)
        match_teams = []
        if match.blue_team is not None:
            match_teams.append(match.blue_team.pk)
        if match.red_team is not None:
            match_teams.append(match.red_team.pk)
        form.fields['winning_team'].queryset = models.Team.objects.filter(
                pk__in=match_teams)

    return render(request, 'tmdb/match_edit.html', {'form': form.as_p(),
            'match_num': match_num})

def rings(request):
    if 'all_matches' not in request.GET: all_matches=False
    else:
        try:
            all_matches = int(request.GET['all_matches']) > 0
        except ValueError:
            all_matches = False
    matches_by_ring = defaultdict(list)
    for match in models.TeamMatch.objects.filter(ring_number__isnull=False):
        if all_matches or match.winning_team is None:
            matches_by_ring[str(match.ring_number)].append(match)
    context = {'matches_by_ring' : sorted(matches_by_ring.items())}
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
