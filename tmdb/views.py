from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.forms.models import modelformset_factory

from .models import TeamMatch, Team, Division
from .forms import MatchForm, SeedingForm

from collections import defaultdict
import re

def index(request):
    divisions = Division.objects.all()
    context = {'divisions' : divisions}
    return render(request, 'tmdb/index.html', context)

def match_list(request, division_id=None):
    if division_id is None:
        divisions = Division.objects.all()
    else:
        divisions=[Division.objects.get(pk=division_id)]

    matches = []
    for division in divisions:
        team_matches = TeamMatch.objects.filter(
                division=division).order_by('number')
        matches.append((division, team_matches))
    context = {'team_matches' : matches}
    return render(request, 'tmdb/match_list.html', context)

def team_list(request, division_id=None):
    if division_id is None:
        divisions = Division.objects.all()
    else:
        divisions=[Division.objects.get(pk=division_id)]

    division_teams = []
    for division in divisions:
        teams = Team.objects.filter(
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
            seed_form = SeedingForm(request.POST, prefix=str(team_id),
                    instance=Team.objects.get(pk=int(team_id)))
            seed_forms.append(seed_form)

        if all(map(SeedingForm.is_valid, seed_forms)):

            division = SeedingForm.all_seeds_valid(seed_forms)

            for team in SeedingForm.modified_teams(seed_forms):
                team = Team.objects.get(pk=team.pk)
                team.seed = None
                team.save()

            for form in seed_forms:
                form.save()
            TeamMatch.create_matches_from_seeds(division)
            return HttpResponseRedirect('/tmdb/matches/' + division_id)

    else:
        seed_forms = []
        for team in Team.objects.filter(division=division_id):
            seed_form = SeedingForm(prefix=str(team.id), instance=team)
            seed_form.name = str(team)
            seed_forms.append(seed_form)

    division_name = str(Division.objects.get(pk=division_id))

    context = {'division': division_id, 'seed_forms': seed_forms,
            'division_name': division_name}
    return render(request, 'tmdb/seedings.html', context)

def match(request, match_num):
    match = TeamMatch.objects.get(number=match_num)
    if request.method == 'POST':
        form = MatchForm(request.POST, instance=match)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/tmdb/matches/'
                    + str(match.division.pk))
    else:
        form = MatchForm(instance=match)
        form.fields['winning_team'].queryset = Team.objects.filter(
                pk__in=[match.blue_team.pk, match.red_team.pk])

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
    for match in TeamMatch.objects.filter(ring_number__isnull=False):
        if all_matches or match.winning_team is None:
            matches_by_ring[str(match.ring_number)].append(match)
    context = {'matches_by_ring' : sorted(matches_by_ring.items())}
    return render(request, 'tmdb/rings.html', context)
