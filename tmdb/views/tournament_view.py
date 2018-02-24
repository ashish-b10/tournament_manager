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

def tournaments(request, tournament_slug=None):
    today = datetime.date.today()
    context = {
        'tournaments': models.Tournament.objects.order_by('-date')
    }
    return render(request, 'tmdb/tournaments.html', context)


@permission_required("tmdb.add_tournament")
def tournament_add(request):
    template_name = 'tmdb/tournament_add_change.html'
    context = {}
    if request.method == 'POST':
        add_form = forms.TournamentEditForm(request.POST)
        context['add_form'] = add_form
        if add_form.is_valid():
            add_form.save()
            return HttpResponseRedirect(reverse('tmdb:tournament_dashboard',
                    args=(add_form.instance.slug,)))
    else:
        today = datetime.date.today()
        add_form = forms.TournamentEditForm(initial={
                'date': today,
                'import_field': True,
        })
    context['add_form'] = add_form
    return render(request, template_name, context)

@permission_required("tmdb.change_tournament")
def tournament_change(request, tournament_slug):
    instance = get_object_or_404(models.Tournament, slug=tournament_slug)
    template_name = 'tmdb/tournament_add_change.html'
    context = {}
    if request.method == 'POST':
        change_form = forms.TournamentEditForm(request.POST, instance=instance)
        context['change_form'] = change_form
        if change_form.is_valid():
            change_form.save()
            return HttpResponseRedirect(reverse('tmdb:tournament_dashboard',
                    args=(change_form.instance.slug,)))
    else:
        change_form = forms.TournamentEditForm(instance=instance,
                initial={'import': False})
        import_form = forms.TournamentImportForm(instance=instance)
        context['import_form'] = import_form
    context['change_form'] = change_form
    return render(request, template_name, context)

@permission_required("tmdb.delete_tournament")
def tournament_delete(request, tournament_slug):
    instance = get_object_or_404(models.Tournament, slug=tournament_slug)
    template_name = 'tmdb/tournament_delete.html'
    context = {'tournament': instance}
    if request.method == 'POST':
        delete_form = forms.TournamentDeleteForm(request.POST,
                instance=instance)
        context['delete_form'] = delete_form
        if delete_form.is_valid():
            instance.delete()
            return HttpResponseRedirect(reverse('tmdb:index'))
    else:
        delete_form = forms.TournamentDeleteForm(instance=instance)
    context['delete_form'] = delete_form
    return render(request, 'tmdb/tournament_delete.html', context)

@permission_required([
        "tmdb.add_school",
        "tmdb.add_schoolregistration",
])
def tournament_import(request, tournament_slug):
    if request.method != "POST":
        return HttpResponse("Invalid operation: %s on %s" %(request.method,
                request.get_full_path()), status=400)
    instance = get_object_or_404(models.Tournament, slug=tournament_slug)
    instance.import_school_registrations()
    return HttpResponseRedirect(reverse('tmdb:index'))

def tournament_dashboard(request, tournament_slug):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    tournament_divisions = models.TournamentDivision.objects.filter(
            tournament=tournament).order_by(
            'division__sex', 'division__skill_level')

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
    return render(request, 'tmdb/tournament_dashboard.html', context)

def model_to_json(query_set, fields):
    obj_json = serializers.serialize('json', query_set, fields=fields)
    return json.loads(obj_json)

json_fields = {
    'tournament': ('id', 'location', 'date',),
    'division': ('id', 'sex', 'skill_level',),
    'school': ('id', 'name',),
    'team': ('id', 'division', 'school', 'number',),
    'tournament_division': ('id', 'division', 'tournament',),
    'school_registration': ('id', 'school', 'tournament',),
    'competitor': ('id', 'registration', 'belt_rank', 'name', 'sex',),
    'team_registration': ('id', 'lightweight', 'middleweight', 'heavyweight',
                    'alternate1', 'alternate2', 'team', 'tournament_division',
                    'points', 'seed',),
    'team_match': ('id', 'blue_team', 'red_team', 'winning_team', 'division',
                    'in_holding', 'at_ring', 'number', 'ring_assignment_time',
                    'ring_number', 'round_num', 'round_slot', 'competing',),
}

def tournament_json(request, tournament_slug):
    msg = []
    tournament = models.Tournament.objects.get(slug=tournament_slug)
    msg.extend(model_to_json(
            [tournament],
            json_fields['tournament']))
    msg.extend(model_to_json(
            models.Division.objects.all(),
            json_fields['division']))
    msg.extend(model_to_json(
            models.School.objects.all(),
            json_fields['school']))
    msg.extend(model_to_json(
            models.Team.objects.all(),
            json_fields['team']))
    msg.extend(model_to_json(
            models.TournamentDivision.objects.filter(tournament=tournament),
            json_fields['tournament_division']))
    msg.extend(model_to_json(
            models.SchoolRegistration.objects.filter(tournament=tournament),
            json_fields['school_registration']))
    msg.extend(model_to_json(
            models.Competitor.objects.filter(
                    registration__tournament=tournament),
            json_fields['competitor']))
    msg.extend(model_to_json(
            models.TeamRegistration.objects.filter(
                    tournament_division__tournament=tournament),
            json_fields['team_registration']))
    msg.extend(model_to_json(
            models.TeamMatch.objects.filter(division__tournament=tournament),
            json_fields['team_match']))

    msg_json = json.dumps(msg)
    return HttpResponse(msg_json, content_type="application/json")

@login_required
def tournament_school(request, tournament_slug, school_slug):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    school = get_object_or_404(models.School, slug=school_slug)
    school_registration = get_object_or_404(models.SchoolRegistration,
            tournament=tournament, school=school)
    competitors = models.Competitor.objects.filter(
            registration=school_registration).order_by('name')
    team_registrations = models.TeamRegistration.order_queryset(
            models.TeamRegistration.objects.filter(
                    tournament_division__tournament=tournament,
                    team__school=school))
    context = {
        'tournament': tournament,
        'school_registration': school_registration,
        'competitors': competitors,
        'team_registrations': team_registrations,
    }
    return render(request, 'tmdb/tournament_school_competitors.html', context)

@permission_required([
        "tmdb.add_competitor",
        "tmdb.add_teamregistration",
        "tmdb.change_competitor",
        "tmdb.change_schoolregistration",
        "tmdb.change_teamregistration",
        "tmdb.delete_competitor",
        "tmdb.delete_teamregistration",
])
def tournament_school_import(request, tournament_slug, school_slug=None):
    if request.method != "POST":
        return HttpResponse("Invalid operation: %s on %s" %(request.method,
                request.get_full_path()), status=400)
    if school_slug is None:
        school_regs = models.SchoolRegistration.objects.filter(
                tournament__slug=tournament_slug)
    else:
        school_reg = get_object_or_404(models.SchoolRegistration,
                tournament__slug = tournament_slug, school__slug=school_slug)
        school_regs = [school_reg]
    reimport = False
    if request.POST.get('reimport') == "true":
        reimport = True
    err_msgs = []
    already_imported_schools = []
    for school_reg in school_regs:
        if school_reg.imported and not reimport:
            already_imported_schools.append(school_reg.school.name)
            continue
        try:
            school_reg.import_competitors_and_teams(reimport=reimport)
        except models.SchoolValidationError as e:
            err_msg = "Error importing %s: %s" %(school_reg.school.name,
                    str(e))
            err_msgs.append(err_msg)
    for err_msg in err_msgs:
        messages.error(request, err_msg, extra_tags="alert alert-danger")
    if already_imported_schools:
        msg = "The following schools were not re-imported: %s" %(
                ", ".join(already_imported_schools))
        messages.warning(request, msg, extra_tags="alert alert-warning")
    return HttpResponseRedirect(reverse('tmdb:tournament_schools',
            args=(tournament_slug,)))

def attach_school_registration_import_errors(school_registrations):
    school_registrations_by_id = {sr.pk:sr for sr in school_registrations}
    import_errors = models.SchoolRegistrationError.objects.filter(
        school_registration__in=[sr.pk for sr in school_registrations]
    )
    for import_error in import_errors:
        school_registration = school_registrations_by_id[
                import_error.school_registration.pk]
        try:
            school_registration.import_errors.append(import_error)
        except AttributeError:
            school_registration.import_errors = [import_error]

@login_required
def tournament_schools(request, tournament_slug):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    school_registrations = models.SchoolRegistration.objects.filter(
        tournament=tournament).order_by('school__name')
    attach_school_registration_import_errors(school_registrations)
    context = {
        'tournament': tournament,
        'all_schools_imported': all(s.imported for s in school_registrations),
        'school_registrations': school_registrations,
    }
    return render(request, 'tmdb/tournament_schools.html', context)

def rings(request, tournament_slug):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    matches_by_ring = defaultdict(list)
    for match in models.TeamMatch.objects.filter(ring_number__isnull=False,
            division__tournament=tournament).order_by('-ring_assignment_time'):
        matches_by_ring[str(match.ring_number)].append(match)
    context = {
        'matches_by_ring' : sorted(matches_by_ring.items()),
        'tournament': tournament
    }
    return render(request, 'tmdb/rings.html', context)
