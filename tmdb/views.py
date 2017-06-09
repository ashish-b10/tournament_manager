from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import models as auth_models
from django.contrib import messages

from . import forms
from . import models

from collections import defaultdict
import datetime

from .util.match_sheet import create_match_sheets
from .util.bracket_svg import SvgBracket

def permission_error_string(user, perm_type):
    return "Username `%s` does not have permission to %s." %(
            user.username, perm_type)

def can_import_school_registration(user):
    return user.has_perms([
        "tmdb.add_competitor",
        "tmdb.add_teamregistration",
        "tmdb.change_competitor",
        "tmdb.change_teamregistration",
        "tmdb.delete_competitor",
        "tmdb.delete_teamregistration",
    ])

@permission_required("tmdb.change_configurationsetting")
def settings(request):
    return render(request, 'tmdb/settings.html')

def index(request):
    return HttpResponseRedirect(reverse('tmdb:tournaments'))

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

@permission_required("tmdb.change_tournament")
def tournament_import(request, tournament_slug):
    if request.method == "POST":
        instance = get_object_or_404(models.Tournament, slug=tournament_slug)
        instance.import_school_registrations()
    return HttpResponseRedirect(reverse('tmdb:index'))

def tournament_dashboard(request, tournament_slug, division_slug=None):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    tournament_divisions = models.TournamentDivision.objects.filter(
            tournament=tournament)

    if division_slug is not None:
        tournament_divisions = tournament_divisions.filter(
                division__slug=division_slug)

    matches = []
    for division in tournament_divisions:
        team_matches = models.TeamMatch.objects.filter(
                division=division).order_by('number')
        for team_match in team_matches:
            team_match.form = forms.MatchForm(instance=team_match)
            match_teams = []
            if team_match.blue_team is not None:
                match_teams.append(team_match.blue_team.pk)
            if team_match.red_team is not None:
                match_teams.append(team_match.red_team.pk)
            team_match.form.fields['winning_team'].queryset = \
                    models.TeamRegistration.objects.filter(pk__in=match_teams)
        matches.append((division, team_matches))

    # Information about the matches by ring.
    matches_by_ring = defaultdict(list)
    for match in models.TeamMatch.objects.filter(ring_number__isnull=False,
            division__tournament=tournament).order_by('ring_assignment_time'):
        matches_by_ring[str(match.ring_number)].append(match)

    context = {
        'tournament': tournament,
        'tournament_divisions': tournament_divisions,
        'matches_by_ring': sorted(matches_by_ring.items()),
        'team_matches': matches
    }
    return render(request, 'tmdb/tournament_dashboard.html', context)

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

@permission_required("tmdb.change_schoolregistration")
def tournament_school_import(request, tournament_slug, school_slug=None):
    context = {}
    if request.method == "POST":
        if school_slug is None:
            school_regs = models.SchoolRegistration.objects.filter(
                    tournament__slug=tournament_slug)
        else:
            school_reg = get_object_or_404(models.SchoolRegistration,
                    tournament__slug = tournament_slug,
                    school__slug=school_slug)
            school_regs = [school_reg]
        reimport = False
        if 'reimport' in request.POST and request.POST['reimport'] == "true":
            reimport = True
        err_msgs = []
        already_imported_schools = []
        for school_reg in school_regs:
            if school_reg.imported and not reimport:
                already_imported_schools.append(school_reg.school.name)
                continue
            try:
                school_reg.import_competitors_and_teams(reimport=reimport)
            except Exception as e:
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
    return HttpResponse("Invalid operation: %s on %s" %(request.method,
            request.get_full_path()), status=400)

def tournament_schools(request, tournament_slug):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    school_registrations = models.SchoolRegistration.objects.filter(
        tournament=tournament).order_by('school__name')
    context = {
        'tournament': tournament,
        'school_registrations': school_registrations
    }
    return render(request, 'tmdb/tournament_schools.html', context)

@permission_required("tmdb.change_teammatch")
def update_teammatch_status(request, tournament_slug, division_slug, match_num):
    tournament_division = get_object_or_404(models.TournamentDivision,
            tournament__slug=tournament_slug, division__slug=division_slug)
    team_match = get_object_or_404(models.TeamMatch,
            division=tournament_division, number=match_num)
    context = {
        'tournament': tournament_division.tournament,
        'tournament_division': tournament_division,
        'team_match': team_match,
    }
    if request.method == 'POST':
        team_match_form = forms.MatchForm(request.POST, instance=team_match)
        context['team_match_form'] = team_match_form
        if team_match_form.is_valid():
            team_match_form.save()
            return HttpResponseRedirect(reverse("tmdb:match_list",
                    args=(tournament_slug, division_slug,)))
    else:
        team_match_form = forms.MatchForm(instance=team_match)
        context['team_match_form'] = team_match_form
        match_teams = []
        if team_match.blue_team is not None:
            match_teams.append(team_match.blue_team.pk)
        if team_match.red_team is not None:
            match_teams.append(team_match.red_team.pk)
        teams = models.TeamRegistration.objects.filter(pk__in=match_teams)
        team_match_form.fields['winning_team'].queryset = teams
    return render(request, "tmdb/team_match_status_change.html", context)

def match_list(request, tournament_slug, division_slug=None):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    tournament_divisions = models.TournamentDivision.objects.filter(
            tournament__slug=tournament_slug)
    if division_slug is not None:
        tournament_divisions = tournament_divisions.filter(
                division__slug=division_slug)

    matches = []
    for division in tournament_divisions:
        team_matches = models.TeamMatch.objects.filter(
                division=division).order_by('number')
        matches.append((division, team_matches,))
    context = {
        'team_matches' : matches,
        'tournament': tournament,
    }
    return render(request, 'tmdb/match_list.html', context)

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
        context['delete_form'] = delete_form
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
        context['edit_form'] = edit_form
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
        context['add_form'] = add_form
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

def division_seedings(request, tournament_slug, division_slug):
    tournament_division = get_object_or_404(models.TournamentDivision,
            tournament__slug=tournament_slug, division__slug=division_slug)
    team_registrations = models.TeamRegistration.objects.filter(
            tournament_division=tournament_division).order_by(
            'team__school__name', 'team__number')
    context = {
        'tournament': tournament_division.tournament,
        'tournament_division': tournament_division,
        'team_registrations': team_registrations,
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

@permission_required("tmdb.add_teammatch", "tmdb.delete_teammatch")
def create_tournament_division_matches(request, tournament_slug, division_slug):
    if request.method != "POST":
        return HttpResponse("Invalid operation: %s on %s" %(request.method,
                request.get_full_path()), status=400)
    tournament_division = get_object_or_404(models.TournamentDivision,
            tournament__slug=tournament_slug, division__slug=division_slug)
    models.TeamMatch.create_matches_from_slots(tournament_division)
    return HttpResponseRedirect(reverse('tmdb:tournament_dashboard',
            args=(tournament_slug,)))

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

def registration_credentials(request):
    template_name = 'tmdb/configuration_setting.html'
    context = {"setting_name": "Registration Import Credentials"}
    setting_key = models.ConfigurationSetting.REGISTRATION_CREDENTIALS
    existing_value = models.ConfigurationSetting.objects.filter(
            key=setting_key).first()
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' %(
                    reverse('tmdb:login'), request.path,))
        form = forms.ConfigurationSetting(request.POST,
                instance=existing_value)
        context['form'] = form
        if not request.user.has_perm('tmdb.change_configurationsetting'):
            context['err_msg'] = permission_error_string(request.user,
                    "change settings")
            return render(request, template_name, context, status=403)
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
        context['form'] = form
    return render(request, 'tmdb/configuration_setting.html', context)

def blue_team_text(team_match):
    if team_match.blue_team is None:
        return None
    return team_match.blue_team.bracket_str()

def red_team_text(team_match):
    if team_match.red_team is None:
        return None
    return team_match.red_team.bracket_str()

def bracket_printable(request, tournament_slug, division_slug):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    tournament_division = get_object_or_404(models.TournamentDivision,
            tournament=tournament, division__slug=division_slug)
    matches, num_rounds = models.TeamMatch.get_matches_by_round(
            tournament_division)
    bracket_columns = []
    for round_num in reversed(range(num_rounds + 1)):
        round_num_matches = 2**round_num
        bracket_column = [None] * round_num_matches
        bracket_columns.append(bracket_column)
        for round_slot in range(round_num_matches):
            key = (round_num, round_slot)
            if key not in matches:
                continue
            bracket_column[round_slot] = matches[key]
    bracket = SvgBracket.create(bracket_columns,
            blue_team_text=blue_team_text, red_team_text=red_team_text)
    response = '<html><body>%s</body></html>' %(bracket.tostring(
            encoding="unicode"),)
    return HttpResponse(response, content_type="image/svg+xml")

def bracket(request, tournament_slug, division_slug):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    tournament_division = get_object_or_404(models.TournamentDivision,
            tournament=tournament, division__slug=division_slug)
    bracket_columns = []
    matches, num_rounds = models.TeamMatch.get_matches_by_round(
            tournament_division)
    bracket_column_height = str(64 * 2**num_rounds) + "px"
    for round_num in reversed(range(num_rounds + 1)):
        round_num_matches = 2**round_num
        bracket_column = [None] * round_num_matches
        bracket_columns.append(bracket_column)
        for round_slot in range(round_num_matches):
            key = (round_num, round_slot)
            cell_type = []
            if key not in matches:
                match = models.TeamMatch()
                cell_type.append("bracket_cell_without_match")
            else:
                match = matches[key]
                cell_type.append("bracket_cell_with_match")
            if round_slot % 2:
                cell_type.append("lower_child_cell")
            else:
                cell_type.append("upper_child_cell")
            bracket_column[round_slot] = match
            match.cell_type = " ".join(cell_type)
            match.height = str(100 / (round_num_matches)) + "%"
    if (0, 0) in matches:
        matches[(0, 0)].cell_type = "bracket_cell_with_match" \
                + " bracket_finals_cell"
    unassigned_teams = models.TeamRegistration.get_teams_without_assigned_slot(
            tournament_division)

    context = {
            'tournament_division': tournament_division,
            'tournament': tournament,
            'bracket_columns': bracket_columns,
            'bracket_column_height': bracket_column_height,
            'unassigned_teams': unassigned_teams,
            'lowest_bye_seed': get_lowest_bye_seed(tournament_division),
    }
    return render(request, 'tmdb/brackets.html', context)

def get_lowest_bye_seed(tournament_division):
    team_registrations = models.TeamRegistration.objects.filter(
            tournament_division=tournament_division)
    team_matches = models.TeamMatch.objects.filter(
            division=tournament_division).order_by('-round_num')
    if not team_matches:
        return 1
    max_round_num = team_matches[0].round_num
    seeds = {tr.seed for tr in team_registrations if tr.seed}
    max_seed = max(seeds)
    for team_match in team_matches:
        if team_match.round_num != max_round_num:
            break
        if team_match.blue_team:
            seeds.remove(team_match.blue_team.seed)
        if team_match.red_team:
            seeds.remove(team_match.red_team.seed)
    if not seeds:
        return max_seed
    return max(seeds)

@permission_required("tmdb.add_competitor")
def competitor_add(request, tournament_slug, school_slug):
    template_name = 'tmdb/competitor_add_change.html'
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    school = get_object_or_404(models.School, slug=school_slug)
    school_registration = get_object_or_404(models.SchoolRegistration,
            tournament=tournament, school=school)
    competitors = models.Competitor.objects.filter(registration=school_registration)
    context = {}
    context['tournament'] = tournament
    context['school'] = school
    context['school_registration'] = school_registration
    context['competitors'] = competitors
    if request.method == 'POST':
        add_form = forms.SchoolCompetitorForm(request.POST)
        context['add_form'] = add_form
        if add_form.is_valid():
            add_form.save()
            return HttpResponseRedirect(reverse("tmdb:tournament_school",
                    args=(tournament_slug, school_slug,)))
    else:
        add_form = forms.SchoolCompetitorForm(
                initial={'registration': school_registration})
        context['add_form'] = add_form
    return render(request, template_name, context)

@permission_required("tmdb.change_competitor")
def competitor_change(request, tournament_slug, school_slug, competitor_id):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    school = get_object_or_404(models.School, slug=school_slug)
    school_registration = get_object_or_404(models.SchoolRegistration,
            tournament=tournament, school=school)
    instance = models.Competitor.objects.get(pk = competitor_id)
    template_name = 'tmdb/competitor_add_change.html'
    context = {}
    context['tournament'] = tournament
    context['school'] = school
    context['school_registration'] = school_registration
    context['competitor'] = instance
    context['name'] = instance.name
    if request.method == 'POST':
        change_form = forms.SchoolCompetitorForm(request.POST,
                instance=instance)
        context['change_form'] = change_form
        if change_form.is_valid():
            competitor = change_form.save()
            return HttpResponseRedirect(reverse('tmdb:tournament_school', args = (tournament_slug, school_slug)))
    else:
        change_form = forms.SchoolCompetitorForm(instance = instance)
        change_form.registration = school_registration
        context['change_form'] = change_form
    return render(request, template_name, context)

@permission_required("tmdb.delete_competitor")
def competitor_delete(request, tournament_slug, school_slug, competitor_id):
    tournament = get_object_or_404(models.Tournament, slug=tournament_slug)
    school = get_object_or_404(models.School, slug=school_slug)
    school_registration = get_object_or_404(models.SchoolRegistration,
            tournament=tournament, school=school)
    instance = models.Competitor.objects.get(pk = competitor_id)
    template_name = 'tmdb/delete_competitor.html'
    context = {}
    context['tournament'] = tournament
    context['school'] = school
    context['school_registration'] = school_registration
    context['competitor'] = instance
    if request.method == 'POST':
        delete_form = forms.SchoolCompetitorDeleteForm(request.POST,
                instance=instance)
        context['delete_form'] = delete_form
        if delete_form.is_valid():
            instance.delete()
            return HttpResponseRedirect(reverse("tmdb:tournament_school",
                    args=(tournament_slug, school_slug,)))
    else:
        delete_form = forms.SchoolCompetitorDeleteForm(instance = instance)
    context['delete_form'] = delete_form
    return render(request, template_name, context)

@permission_required("tmdb.add_teammatch")
def add_team_to_bracket(request, tournament_slug, division_slug):
    if request.method == 'POST':
        form = forms.TeamRegistrationSeedingForm(request.POST)
        if form.is_valid():
            team_registration = models.TeamRegistration.objects.get(
                    pk=request.POST['team_registration'])
            team_registration.seed = int(request.POST['seed'])
            team_registration.save()
            tournament_division = team_registration.tournament_division
            models.TeamMatch.create_matches_from_slots(tournament_division)
            return HttpResponseRedirect(reverse("tmdb:bracket", args=(
                    tournament_division.tournament.slug,
                    tournament_division.division.slug,)))
    else:
        side = request.GET.get('side')
        round_num = request.GET.get('round_num')
        round_slot = request.GET.get('round_slot')
        tournament_division = get_object_or_404(models.TournamentDivision,
                tournament__slug=tournament_slug, division__slug=division_slug)
        existing_match = get_object_or_404(models.TeamMatch,
                division=tournament_division, round_num=round_num,
                round_slot=round_slot)
        if side == "upper":
            existing_team = existing_match.blue_team
        elif side == "lower":
            existing_team = existing_match.red_team
        else:
            raise ValueError("side was `%s`, must be `upper` or `lower`" %(
                    side,))
        new_seed = 2**(int(round_num) + 2) - existing_team.seed + 1
        form = forms.TeamRegistrationSeedingForm(initial={'seed': new_seed})
        form.fields['team_registration'].queryset = \
                models.TeamRegistration.get_teams_without_assigned_slot(
                        tournament_division)
    context = {
            'tournament_division': tournament_division,
            'tournament': tournament_division.tournament,
            'existing_team': existing_team,
            'new_seed': new_seed,
            'form': form,
    }
    return render(request, 'tmdb/modify_team_registration_seed.html', context)

def match_sheet(request, tournament_slug, division_slug, match_number=None):
    tournament_division = get_object_or_404(models.TournamentDivision,
            tournament__slug=tournament_slug, division__slug=division_slug)
    filename = "%s-%s" %(tournament_slug, division_slug)
    if match_number:
        matches = [models.TeamMatch.objects.get(division=tournament_division,
                number=match_number)]
        filename += "-match_%s.pdf" %(match_number,)
    else:
        matches = models.TeamMatch.objects.filter(
                division=tournament_division).order_by('number')
        filename += "-matches.pdf"
    sheet = create_match_sheets(matches)

    response = HttpResponse(sheet, content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename=%s' %(filename,)
    return response

def create_headtable_user(request):
    template_name = 'tmdb/add_user.html'
    context = {}
    context['form_action'] = reverse('tmdb:create_headtable_user')
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' %(
                    reverse('tmdb:login'), request.path,))
        form = forms.UserForm(request.POST)
        context['form'] = form
        if not request.user.has_perm('auth.add_user'):
            context['err_msg'] = permission_error_string(request.user,
                    "create users")
            return render(request, template_name, context, status=403)
        if form.is_valid():
            user = auth_models.User.objects.create_user(**form.cleaned_data)
            user.groups.set([get_headtable_permission_group()])
            return HttpResponseRedirect(reverse('tmdb:settings'))
    else:
        form = forms.UserForm()

    context['form'] = form
    return render(request, 'tmdb/add_user.html', context)

def create_ringtable_user(request):
    template_name = 'tmdb/add_user.html'
    context = {}
    context['form_action'] = reverse('tmdb:create_ringtable_user')
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' %(
                    reverse('tmdb:login'), request.path,))
        form = forms.UserForm(request.POST)
        context['form'] = form
        if not request.user.has_perm('auth.add_user'):
            context['err_msg'] = permission_error_string(request.user,
                    "create users")
            return render(request, template_name, context, status=403)
        if form.is_valid():
            user = auth_models.User.objects.create_user(**form.cleaned_data)
            user.groups.set([get_ringtable_permission_group()])
            return HttpResponseRedirect(reverse('tmdb:settings'))
    else:
        form = forms.UserForm()

    context['form'] = form
    return render(request, 'tmdb/add_user.html', context)

def get_ringtable_permission_group():
    group = auth_models.Group.objects.filter(name = "Ring Table").first()
    if not group:
        group = create_ringtable_permission_group()
    return group

def create_ringtable_permission_group():
    group = auth_models.Group.objects.create(name="Ring Table")
    group.permissions.set([auth_models.Permission.objects.get(
            name='Can change team match')])
    return group

def get_headtable_permission_group():
    group = auth_models.Group.objects.filter(name = "Head Table").first()
    if not group:
        group = create_headtable_permission_group()
    return group

def create_headtable_permission_group():
    group = auth_models.Group.objects.create(name="Head Table")
    group.permissions.set(auth_models.Permission.objects.filter(
            content_type__in=auth_models.ContentType.objects.filter(
                    app_label="tmdb")))
    group.permissions.add(auth_models.Permission.objects.get(
            name="Can add user"))
    return group
