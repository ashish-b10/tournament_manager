from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from .models import TeamMatch, Team, Division
from .forms import MatchForm

from collections import defaultdict

def index(request):
    divisions = Division.objects.all()
    context = {'divisions' : divisions}
    return render(request, 'tmdb/index.html', context)

def division(request, division_id=None):
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
    return render(request, 'tmdb/division.html', context)

def match(request, match_num):
    match = TeamMatch.objects.get(number=match_num)
    if request.method == 'POST':
        form = MatchForm(request.POST, instance=match)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/tmdb')
    else:
        form = MatchForm(instance=match)
        form.fields['winning_team'].queryset = Team.objects.filter(
                pk__in=[match.blue_team.pk, match.red_team.pk])

    return render(request, 'tmdb/match_edit.html', {'form': form,
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
