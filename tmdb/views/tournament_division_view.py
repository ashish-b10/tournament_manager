from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseRedirect

from tmdb import forms, models

@permission_required("tmdb.change_tournamentdivision")
def lock_team_registration(request, tournament_slug, division_slug):
    tournament_division = get_object_or_404(models.TournamentDivision,
            tournament__slug=tournament_slug, division__slug=division_slug)
    if request.method == 'POST':
        form = forms.TournamentDivisionLockUnlockForm(request.POST,
                instance = tournament_division)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("tmdb:tournament_dashboard",
                    args=(tournament_slug,)))
    else:
        form = forms.TournamentDivisionLockUnlockForm(
                instance=tournament_division,
                initial={'locked_from_new_teams': True})
    context = {
        'tournament_division': tournament_division,
        'tournament': tournament_division.tournament,
        'form': form,
    }
    return render(request,
            'tmdb/tournament_division/lock_team_registration.html', context)

@permission_required("tmdb.change_tournamentdivision")
def unlock_team_registration(request, tournament_slug, division_slug):
    tournament_division = get_object_or_404(models.TournamentDivision,
            tournament__slug=tournament_slug, division__slug=division_slug)
    if request.method == 'POST':
        form = forms.TournamentDivisionLockUnlockForm(request.POST,
                instance = tournament_division)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("tmdb:tournament_dashboard",
                    args=(tournament_slug,)))
    else:
        form = forms.TournamentDivisionLockUnlockForm(
                instance=tournament_division,
                initial={'locked_from_new_teams': False})
    context = {
        'tournament_division': tournament_division,
        'tournament': tournament_division.tournament,
        'form': form,
    }
    return render(request,
            'tmdb/tournament_division/unlock_team_registration.html', context)
