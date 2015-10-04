from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from .models import TeamMatch, Team
from .forms import MatchForm

def index(request):
    team_matches = TeamMatch.objects.all().order_by('number')
    context = {'team_matches' : team_matches}
    return render(request, 'tmdb/index.html', context)

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
    #return HttpResponse('Editing match number ' + match_num)
